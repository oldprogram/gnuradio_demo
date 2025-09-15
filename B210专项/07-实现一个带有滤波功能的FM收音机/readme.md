### 一、启动环境

**本次运行 docker 的命令和之前稍微有点不一样**：由于进入 docker 后发现 `ls /dev/snd -all` 声卡都属于 polkitd 组，而不是 audio 组，因此在启动 docker 时通过下面命令让当前用户加入 polkitd 组，从而能够在非 root 权限情况下使用声卡

- 验证非 sudo 权限下是否可以使用声卡，可以 `sudo apt-get install alsa-utils`，然后 `aplay -l`
- 验证当前用户是否属于 polkitd 组，可以使用 `groups` 命令

**如果你用的不是 docker** 需要先看看声卡属于什么组，然后将当前用户加入对应组，然后刷新：    

- `sudo usermod -aG polkitd gnuradio    # 将 gnuradio 加入 polkitd 组`
- `newgrp polkitd # 刷新`

</br>

下面是 docker 命令：

```
systemctl start  docker
xhost -          
xhost +local:docker 
docker run -it --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/bus/usb/:/dev/bus/usb/ \
    -v /run/user/1000/pulse:/run/user/1000/pulse \
    -v /home/btfz/Desktop/B210:/home/gnuradio/B210 \
    --privileged \
    --group-add=polkitd \
    ubuntu:gnuradio-310 bash

zsh
export UHD_IMAGES_DIR=/home/gnuradio/B210/B210_images/
uhd_find_devices
```

**PS：** 如果报找不到 card '0'，就用 `ls -all /dev/snd` 输出显示设备是 controlC1，这意味着你的声卡设备是 Card 1，而不是 ALSA 默认查找的 Card 0。这就是 cannot find card '0' 错误信息的来源。进行强制指定： `export ALSA_CARD=1`

测试声音使用：

```
sudo apt install sox
play -n synth 2 sin 440  # 生成 2 秒的 440Hz 标准 A 音
```

但是我发现 ALSA 是 linux 音频底层硬件，pulseaudio 是上层服务，会将底层的统一管理，对接应用层（统一分配使用哪个硬件播放），如果有 pulseaudio 使用起来会优雅一点，否则就要强制指定对应的硬件进行播放了。

但是我发现 docker 内想要优雅的使用 pulseaudio [极其困难][#2]，涉及[大量权限][#1]问题。

</br>

### 二、核心要注意的点

第二个要注意的点是：我们在 GNU Radio 中使用了 python block 来实现高斯滤波器，并基于 numba 加速（纯 python 运行太慢，这里使用 numba 先将 python 转化为 C 然后加速运行，需要在 docker 内安装该 python 组件：`sudo python3 -m pip install numba --break-system-packages` ！！！

</br>

### 三、流程图介绍

**1）FM 解调逻辑**

FM 解调涉及的模块如下：

![][p1]

**首先**经过 Rational_Resampler（有理重采样），将采样率除 4；然后经过一个低通滤波器，低通滤波设置的截至频率为 100Hhz；

**接着**经过一个用于解调广播 FM 信号的 WBFM 接收块，因为我们将 2M 采样率的数据经过了 4 倍下采样，因此进入 WBFM 的复基带信号的采样率为 2M/4 = 500KHz，同时我们设置了 10 倍音频抽取，因此输出的音频频率为 500KHz/10 = 50KHz；

**最后**由于音频输出一般需要 48KHz 的采样率，因此将音频流经过一个有理重采样，插值 48，抽取 50，因此输出的音频流变为：50KHz/50*48 = 48 KHz。

**2）FM 信号低通滤波算法**

为了从源头去除一些干扰，在进行 FM 解码前实施低通滤波，这里将该低通滤波器的两个主要选项：截至频率和传输带宽通过滑动条，让用户可以实时调节；并且用 QT GUI Frequency Sink 用来显示实施滤波前后的频谱的变化。

一般来说：如果不经过低通滤波，前后两个频谱图重合；当改变截止频率和传输带宽时，只有中心频率附近部分重合，然后两边产生跌落，从而过滤掉无用的频率数据。需要注意：距离中心频率的重合部分/宽度越小，滤波效果越强，但是也可能导致严重数据失真（一般情况需要保证距离中心频率 8Khz 左右宽度）

![][p2]    

3）音频降噪算法

音频降噪主要采用两种算法：

- 低通滤波：滤除音频中的高频部分
- 高斯滤波：滤除音频中的"雪花"噪声

![][p3]

其中低通滤波器设置的截止频率为 8KHz，滤除 8KHz 以上的频率（因为人耳可接收的声音主要在 8KHz 以下）；

高斯滤波器是一种线性滤波器，能够有效的抑制噪声，平滑图像。其作用原理和均值滤波器类似，都是取滤波器窗口内的像素的均值作为输出。其窗口模板的系数和均值滤波器不同，均值滤波器的模板系数都是相同的为1；而高斯滤波器的模板系数，则随着距离模板中心的增大而系数减小。所以，高斯滤波器相比于均值滤波器对图像个模糊程度较小。

这里是代码实现的高斯滤波，并基于 numba 加速（纯 python 运行太慢，这里使用 numba 先将 python 转化为 C 然后加速运行，需要在电脑上安装该 python 组件：`sudo python3 -m pip install numba --break-system-packages` ！！！

```
import numpy as np
from gnuradio import gr
import numba

@numba.jit(nopython=True)
def numba_convolve(in0, kernel):
    return np.convolve(in0, kernel, mode='same')

class GaussianFilter(gr.sync_block):
    def __init__(self, window_size=5, std_dev=1.0):
        gr.sync_block.__init__(
            self,
            name='Gaussian Filter',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.window_size = window_size
        self.std_dev = std_dev
        self.gaussian_kernel = self.generate_gaussian_kernel()

    def generate_gaussian_kernel(self):
        x = np.arange(-(self.window_size // 2), self.window_size // 2 + 1)
        gaussian = np.exp(-(x ** 2) / (2 * self.std_dev ** 2))
        return gaussian / gaussian.sum()

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        if 0:
            # 边界填充
            pad_width = self.window_size // 2
            padded_in0 = np.pad(in0, (pad_width, pad_width), mode='symmetric')
            convolved = numba_convolve(padded_in0, self.gaussian_kernel)
            out[:] = convolved[pad_width:pad_width + len(out)]
        else:
            out[:] = in0
        return len(output_items[0])
```

注意：这里 `work 中的 if 0 如果改为 if 1` 就会使能高斯滤波，否则就是直接透传。

最后，可以在 GUI 页面上看到经过滤波器之后的瀑流图：

![][p4] 


</br>

### 参考链接

</br>

[[1]. GR WiKi —— Multiply Const][#6]    
[[2]. GR WiKi —— QT GUI Range][#7]    
[[3]. GR WiKi —— Audio Sink][#8]    
[[4]. GR WiKi —— 有理重采样器][#9]    
[[5]. GR WiKi —— 低通滤波器][#10]    
[[6]. GR WiKi —— WBFM Receive][#11]       
[[7]. GR WiKi —— AGC][#12]    
[[8]. GR WiKi —— PLL Carrier Tracking][#13]    
[[9]. GR WiKi —— AM Demod][#14]    
[[10]. GitHub —— AM 调制基础知识][#15]    
[[11]. GitHub —— AM 单边带和双边带调制][#16]   
[[12]. CSDN —— 高斯滤波的理解与学习][#17]    
[[13]. 博客园 —— 图像处理基础(4)：高斯滤波器详解][#18]    

[#1]:https://gemini.google.com/app/e7c2c915b0e393a0?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all    
[#2]:https://www.doubao.com/chat/19945218343574530    
[#6]:https://wiki.gnuradio.org/index.php/Multiply_Const  
[#7]:https://wiki.gnuradio.org/index.php/QT_GUI_Range     
[#8]:https://wiki.gnuradio.org/index.php/Audio_Sink     
[#9]:https://wiki.gnuradio.org/index.php/Rational_Resampler    
[#10]:https://wiki.gnuradio.org/index.php/Low_Pass_Filter    
[#11]:https://wiki.gnuradio.org/index.php/WBFM_Receive    
[#12]:https://wiki.gnuradio.org/index.php/AGC    
[#13]:https://wiki.gnuradio.org/index.php/PLL_Carrier_Tracking    
[#14]:https://wiki.gnuradio.org/index.php/AM_Demod    
[#15]:https://github.com/oldprogram/gnuradio_demo/tree/main/%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B/21-GNU%20Radio%20%E5%9F%BA%E7%A1%80%E8%B0%83%E5%88%B6/01-AM_DSB    
[#16]:https://github.com/oldprogram/gnuradio_demo/tree/main/%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B/21-GNU%20Radio%20%E5%9F%BA%E7%A1%80%E8%B0%83%E5%88%B6/02-AM_SSB    
[#17]:https://blog.csdn.net/leonardohaig/article/details/120464251    
[#18]:https://www.cnblogs.com/wangguchangqing/p/6407717.html     

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/fm_receive.png    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/low_pass_filter.jpeg
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/sound_jiangzao.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/sound_jiangzao_gui.jpeg
    


