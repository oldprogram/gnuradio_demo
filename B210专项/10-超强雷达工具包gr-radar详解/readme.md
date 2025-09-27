### 一、环境准备
#### 1.1 docker gnuradio-3.8 环境准备

```
# 安装镜像
systemctl start docker 
git clone git@github.com:btfz-sdr/docker-gnuradio.git
cd docker-gnuradio/gnuradio-releases-38 
docker build -t ubuntu:gnuradio-38 .

# 运行 docker
xhost -  
xhost +local:docker 
docker run -it --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/bus/usb/:/dev/bus/usb/ \
    -v /home/btfz/Desktop/B210:/home/gnuradio/B210 \
    --privileged \
ubuntu:gnuradio-38  bash 

# zsh 方便使用命令行，自动提醒
sudo apt-get install wget zsh 
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 安装依赖
sudo apt-get install qt5-default 
sudo apt-get install libqwt-qt5-dev
sudo apt-get install libuhd-dev 
sudo apt-get install libqt5svg5-dev
sudo apt-get install doxygen 
sudo apt-get install doxygen-doxyparse 

# 编译安装
https://github.com/kit-cel/gr-radar
git clone https://github.com/kit-cel/gr-radar.git
cd gr-radar
git checkout maint-3.8  # 注意切分支
mkdir build
cd build
cmake ..
make

sudo ./../examples/setup/setup_core
ctest
sudo make install
```

</br>

**PS：** 上面操作完之后，如果退出 docker 容器之后，下次启动还要重复操作，可以用下面命令将当前容器状态保存为新镜像（增量存储）：

```
➜  ~ docker ps                                       
CONTAINER ID   IMAGE                COMMAND   CREATED         STATUS         PORTS     NAMES
d7926bff76c3   ubuntu:gnuradio-38   "bash"    7 minutes ago   Up 7 minutes             xenodochial_satoshi
➜  ~ docker commit d7926bff76c3 ubuntu:gnuradio-radar
sha256:dc19e62de441778ed9e4ce06afa269ea5f335c285df27f6670aa97f540d479e6
➜  ~ docker image list 
REPOSITORY   TAG              IMAGE ID       CREATED          SIZE
ubuntu       gnuradio-radar   dc19e62de441   19 seconds ago   3.29GB
ubuntu       gnuradio-38      69c3f019986b   23 hours ago     3.01GB
```

之后就可以用下面方法直接启动了：

```
xhost -  
xhost +local:docker 
docker run -it --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/bus/usb/:/dev/bus/usb/ \
    -v /home/btfz/Desktop/B210:/home/gnuradio/B210 \
    --privileged \
ubuntu:gnuradio-radar  bash 
```

</br>

#### 1.2 异常解决

**1）动态链接库链接不到导致倒入 radar 块失败问题**

由于上面安装脚本将 `libgnuradio-radar.so.1.0.0git` 安装在 ubuntu 不方便找到的位置 `/usr/local/lib/x86_64-linux-gnu`，为了让 `import radar` 导入没有异常，需要在终端中增加：

```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/x86_64-linux-gnu
```

否则会导致 ImportError：

```
➜  radar pwd
/usr/local/lib/python3/dist-packages/radar
➜  radar ls
__init__.py    __init__.pyc  _radar_swig.so  radar_swig.pyc
__init__.pybk  __init__.pyo  radar_swig.py   radar_swig.pyo
➜  radar cat __init__.py
# import swig generated symbols into the radar namespace
try:
    # this might fail if the module is python-only
    from .radar_swig import *
except ImportError:
    pass
```

**2）examples 中的流程图的 Rational Resampler 报错**

参考[该块的 wiki][#1]，分数带宽参数有如下要求：

> 分数带宽 (0, 0.5)，在最终频率下测量（使用 0.4）（浮点数）。
> 
>在 GNU Radio 3.8 中，默认值为 0，应将其更改为 0 到 0.5 之间的值；或者直接删除。删除分数带宽的值将导致模块使用默认值 0.4。

可以用下面命令一键修复：

```
find examples -type f -name "*.grc" -exec sed -i "s/fbw: '0'/fbw: ''/g" {} +
```

</br>

### 二、案例解析
#### 2.1 tests

**1）test_find_max_peak_c.grc**

![][p1]    

使用 Find Max Peak 模块，寻找最大峰值的信息：

```
// Print results
rx_time: 0:-1 
frequency: 5000 
power: 4.19432e+06 
phase: -3.24372e-08 
```

</br>

**2) test_ts_fft_cc.grc**

![][p2]

和上一个区别是：这里可以调节信号源的频率，上一个是调节 Find Max Peak 的阈值。

</br>

**3）test_signal_generator_cw_c.grc**

![][p3]

产生连续波的简单 demo。

</br>

**4）test_signal_generator_fmcw_c.grc**

![][p5]

产生 FMCW 波的简单 demo，运行之后其中心频率会按照右边这些图来变化。

</br>

**5）test_split_cc.grc**

![][p8]

模拟雷达信号与某个运动目标的相互作用，生成雷达接收信号。比如图中的多普勒导致的频移符合计算。

</br>

**6）test_static_target_simulator_cc.grc**

![][p9]

看完上面一个，这个就比较简单了，演示静态目标模拟器器对连续波产生的多普勒频移。

</br>

**7）test_msg_manipulator.grc**

![][p10]

这个会稍微复杂一点，利用 CW 波加高斯噪声制造出三个波峰的连续波，然后使用 OS-CFAR 模块进行寻找波峰，然后使用 Estimator CW 模块从频率偏移估计速度，实现模拟多普勒 CW 测速。

</br>

**8）test_usrp_echotimer_cc.grc**

![][p11]

这个借助一个 UHD 设备，实现收发一体，CW 测速。

</br>

**9）test_uhd_sink_source_inbuild.grc**

![][p12]

这个借助一个 UHD 设备，实现收发非一体，CW 测速。

</br>

#### 2.2 simulation
**1）simulator_cw.grc**

![][p13]

模拟 cw。

</br>

**2）simulator_dual_cw.grc**

![][p15]

![][p16] 

双路 cw 测速度和距离。

</br>

**3）simulator_dual_cw_estimation_rcs.grc**

![][p17]

和上一个很像，双路 cw 主要评估 rcs 对效果影响。

</br>

**4）simulator_sync_pulse.grc**

![][p18]

这是个计算发送和接收脉冲之间的 offset 的块演示。    

这个例子有问题，是需要基于输入和输出的 packet_len 计算 offset，但是 skip head 之后没了 packet_len，导致运行报错（只有 skip 0 不报错）

</br>

**5）simulator_fmcw.grc**

![][p19]

这个是模拟 FMCW，基本上是在 `test/5）test_split_cc.grc` 基础上扩展完善的，可以实现测速和测距。

关于 FMCW 产生的波形，可以参考 `test/4）test_signal_generator_fmcw_c.grc`

</br>

**6）simulator_fmcw_rcs.grc**

![][p20]

和上一个很像，主要评估 rcs 对效果影响。

</br>

**7）simulator_fsk_tracking_singletarget.grc**

![][p21]

![][p22]

基于 FSK 单目标雷达跟踪模拟，它能够根据雷达的距离和速度测量数据，使用卡尔曼滤波器或粒子滤波器来持续追踪一个目标。

</br>

**8）simulator_ofdm.grc**

OFDM 是一种多载波调制技术，它把高速数据流分解到多个正交的低速子载波上进行传输。当它与 QPSK 调制结合并用于雷达测速测距时，其工作原理与传统的 FMCW（调频连续波）雷达有本质区别。它利用了 OFDM 信号独特的频率结构来同时提取距离和速度信息。

- **测距**：利用信号往返的时延。该时延在频域上表现为各子载波之间的线性相位差。通过测量这一相位差的斜率，即可计算出目标距离。
- **测速**：利用目标移动产生的多普勒频移。这表现为连续 OFDM 符号间，同一子载波的相位发生旋转。通过测量旋转速度，即可得出目标速度。

该系统能同时从一个信号中提取距离和速度信息，功能强大且高效。

![][p23]

![][p24]

OFDM 雷达将一个复杂的测距测速任务解耦成了两个独立的测量：

- **测距**：通过在一个 OFDM 符号内部，测量不同子载波之间的相位差。
- **测速**：通过测量不同 OFDM 符号之间，同一子载波的相位变化。

这种独特的方法使得 OFDM 雷达能够同时获得目标的距离和速度信息，并拥有高分辨率、抗干扰能力强等优点，这使其在未来的自动驾驶、工业传感和物联网等领域有巨大的应用潜力。

</br>

#### 2.3 UHD 雷达

**1）usrp_echotimer_cw_grc**

![][p25]

该 GNU Radio 流程图描述了一个基于 **USRP 硬件的连续波（CW）多普勒雷达系统**。

其核心原理是利用多普勒效应来测量目标速度。
1.  首先，“信号发生器”产生一个**连续波**并发送出去。
2.  接收到回波后，“复数共轭相乘”模块将接收信号与发射信号进行**混频**。这一步会产生一个**拍频**信号，其频率就是目标的多普勒频移。
3.  随后，通过**傅里叶变换（FFT）**，系统将拍频信号转换为频域，以准确识别多普勒频移。
4.  Find Max Peak 模块直接在 FFT 结果中寻找最大的频率峰值。
5.  Estimator CW 模块将这个最大峰值的频率偏移量，精确地转换为目标的速度。

这套系统专门用于**非接触式地测量目标的移动速度**。

</br>

**2）usrp_echotimer_dual_cw.grc**

![][p26]

该 GNU Radio 流程图展示了一个先进的**双频连续波（Dual-CW）雷达**系统，能够**同时测量目标的速度和距离**。

**工作原理**

1.  **信号生成**：您将 `+6M` 和 `-6M` 这两个连续波信号相加，创建了一个包含两个频率分量的**混合发射信号**。在复数基带信号处理中，`+6M` 和 `-6M` 代表了两个独特的通道，它们携带了相同的目标信息。

2.  **回波处理**：当这个混合信号遇到目标并反射回来后，回波中依然同时包含 `+6M` 和 `-6M` 这两个分量，但它们都因多普勒效应而产生了频率偏移，也因目标角度而产生了相位偏移。

3.  **通道分离**：您的处理链将回波分成了两路，并分别与 `-6M` 和 `+6M` 进行 `Multiply Conjugate` 混频操作。
    * 第一路回波与 `-6M` 混频后，**有效提取出了回波中的 `+6M` 频率分量**。这个混频的输出信号将包含 `+6M` 信号的多普勒频移信息。
    * 第二路回波与 `+6M` 混频后，**有效提取出了回波中的 `-6M` 频率分量**。这个混频的输出信号将包含 `-6M` 信号的多普勒频移信息。

通过上述处理，系统成功地将回波中的两个频率分量（`+6M` 和 `-6M`）分离成了两个独立的基带信号。

这个系统之所以强大，正是因为它巧妙地利用 `+6M` 和 `-6M` 这两个频率分量，实现了三维信息的同步获取：

1.  **速度测量**：通过分析任一处理路径中混频后的多普勒频移，可以精确计算出目标的速度。

2.  **角度测量**：通过比较两条路径最终输出信号的**相位差**，可以推算出目标相对于雷达的**角度**。

3.  **距离测量**：由于系统同时发射了 `+6M` 和 `-6M` 两个频率，它们在混频后会产生一个 `12M` 的**差拍频**。这个差拍频信号的**相位**，与目标距离成正比。通过测量这个相位的变化，系统能够精确地计算出目标的**距离**。

因此，这个流程图展示了一套完整且强大的**三维信息感知**系统，能够从一个回波中同时确定目标的**速度、角度和距离**，远超一般雷达的功能。

</br>

**3）usrp_echotimer_dual_cw_rcs.grc**

![][p27]

该 GNU Radio 流程图是上一个**双频 CW 雷达系统**的升级版。

它最大的不同在于增加了**“RCS 估算器”**模块。RCS，即**雷达散射截面积**，是一个物理量，用于衡量目标反射雷达信号的强度，反映了目标的“雷达可见性”。

该新模块利用系统已知的参数（如天线增益、发射功率）和已测得的**目标距离**，来计算出目标的 RCS 值。

因此，这个流程图所展示的系统不仅能够同时测量目标的**速度**和**距离**，还能进一步量化目标的**雷达散射截面积**，从而提供更全面的目标特性信息。

</br>

**4）usrp_echotimer_dual_cw_tracking.grc**

![][p28]

这个流程图在上一个版本的基础上，增加了**目标跟踪**功能。

它保留了双频 CW 雷达同时测量速度和距离的核心能力，但将这些原始测量数据接入了全新的**“单目标跟踪”**模块。

这个跟踪模块使用高级的滤波器（如卡尔曼或粒子滤波器），将每次独立的测量数据**整合**起来，对目标的运动轨迹进行**平滑和预测**。

它的作用是：
* 过滤掉雷达测量中的随机噪声。
* 即使目标短时间被遮挡，也能根据之前的运动轨迹预测其位置。
* 实现对单个目标的稳定、持续跟踪。

因此，这个流程图代表了一个更完整、更具实用性的雷达系统，实现了从原始信号处理到最终**可靠目标追踪**的全过程。

</br>

**5）usrp_echotimer_fmcw.grc**

![][p29]

这个流程图展示了一个完整的**调频连续波（FMCW）雷达**系统。

FMCW 雷达的原理与之前测速测距的 CW 雷达完全不同，它利用**频率差**来测量距离。

**工作原理**

1.  **发射调频波**：首先，“FMCW 信号发生器”会生成并发送一个频率随时间线性变化的连续波信号（即“**chirp**”）。

2.  **混频**：当回波信号返回时，它与正在发射的信号进行**混频**（`Multiply Conjugate`）。由于回波存在时延，其频率会与当前发射信号的频率有一个恒定的差异。

3.  **距离测量**：这个频率差异被称为“**拍频**”（Beat Frequency）。拍频的频率值与目标的**距离**成正比。

4.  **速度测量**：通过分析**调频波上升和下降**两个阶段的拍频差异，系统可以进一步计算出目标的速度。

整个流程图通过 FFT 将拍频转换为频域信号，并用 `Estimator FMCW` 模块进行最终的距离和速度估算，实现了完整的 FMCW 雷达功能。

</br>

**6）usrp_echotimer_fsk.grc**

![][p31]

这个流程图展示了一个基于**频移键控（FSK）**原理的雷达系统。它能够同时测量目标的距离和速度。

* **工作原理**：它通过信号发生器交替发射两个不同频率（高频和低频）的连续波信号。
* **核心功能**：系统将回波与发射信号进行混频，并产生两个拍频。这两个拍频之间的频率差异与目标的**距离**成正比。

`FSK 估算器`模块就是利用这个原理，通过**傅里叶变换（FFT）**分析来同时计算目标的**距离和速度**。这个系统实现了**无脉冲**的精确测距和测速。

</br>

**7）usrp_echotimer_fsk_tracking_singletarget.grc**

![][p32]

这个流程图展示了一套完整的**FSK 雷达追踪系统**。

**工作原理**

1.  **FSK 测距测速**：它首先采用**频移键控（FSK）**原理，通过在两个频率之间切换，并利用`FSK 估算器`模块来测量目标的**速度**和**距离**。

2.  **目标跟踪**：与之前的流程图不同，它将测得的原始速度和距离数据，接入**“单目标跟踪”**模块。

3.  **平滑与预测**：该跟踪模块使用**粒子滤波器**（`Filter: particle`），对雷达的原始测量值进行**滤波**和**平滑**处理。这使得系统能够排除测量噪声、处理数据丢失，并**预测目标未来的位置**。

这个流程图代表了一个功能完备的雷达系统，它不仅能够感知目标的实时状态，更能对其运动轨迹进行**稳定、持续的追踪**，是实际应用中非常重要的一环。

</br>

**8）usrp_echotimer_sync_pulse.grc**

![][p33]

该 GNU Radio 流程图展示了一个基于 **USRP 软件无线电**的脉冲回波测距系统。

其工作流程如下：
1.  “信号发生器”生成一个**同步脉冲**，并由 USRP 发射出去。
2.  同时，“USRP 回波计时器”模块负责接收回波信号，它也使用了另一个 USRP 设备。
3.  “同步脉冲估算器”是核心，它通过**相关性分析**，精确地测量发射脉冲与接收回波之间的时间延迟。
4.  根据这个时延，系统即可推算出目标的**距离**。

最终，通过打印和图形界面，该系统能实时显示测量的距离结果和回波波形。这是一个典型的利用信号相关性进行回波测量的应用。

</br>

### 三、附加原理
#### 3.1 Multiply Conjugate 流0 x 流1 的复共轭

`Multiply Conjugate` 模块的操作是将**流 0** 乘以**流 1 的复共轭**。

新输出信号的特性：

* **幅度**：新输出信号的幅度是两个输入信号**幅度的乘积**（$A_0 A_1$）。
* **相位**：新输出信号的相位是两个输入信号的**相位差**（$\phi_0 - \phi_1$）。
* **频率**：新输出信号的频率是两个输入信号频率的**差值**。

这完美地解释了为什么 `Multiply Conjugate` 模块在雷达和通信等领域如此强大，因为它能够从复杂的输入信号中精确地提取出关键的**频率差**和**相位差**信息。

</br>

#### 3.2 回波的频率、相位特性

**1）回波的频率特性**

当一个连续波 (CW) 信号遇到一个以正速度运行的障碍物时，其回波频率会因**多普勒效应**而发生偏移。无论是正频率还是负频率的信号，都会经历相同的多普勒频移。

假设：
* 正频率信号：$f_{pos}$
* 负频率信号：$f_{neg}$ （其中 $f_{neg} = -f_{pos}$）
* 障碍物的多普勒频移：$f_D$ （正速度，所以 $f_D > 0$）

回波的频率特性将是：
* **正频率信号的回波**：$f^\prime_{pos} = f_{pos} + f_D$
* **负频率信号的回波**：$f^\prime_{neg} = f_{neg} + f_D$

这意味着，回波信号的**频率差保持不变**：$f^\prime_{pos} - f^\prime_{neg} = (f_{pos} + f_D) - (f_{neg} + f_D) = f_{pos} - f_{neg}$。

</br>

**2）回波的相位特性**

回波的相位特性主要受到两个因素的影响：**初始相位**和**往返时延**。

假设：
* 起始相位相同：$\phi_0$
* 信号往返时延：$\tau = \frac{2R}{c}$ （$R$ 是距离，$c$ 是光速）

回波信号的相位会比发射信号的相位滞后 $2\pi f \tau$。

* **正频率信号的回波相位**：$\phi^\prime_{pos} = \phi_0 - 2\pi f_{pos} \tau$
* **负频率信号的回波相位**：$\phi^\prime_{neg} = \phi_0 - 2\pi f_{neg} \tau = \phi_0 - 2\pi (-f_{pos}) \tau = \phi_0 + 2\pi f_{pos} \tau$

可以看出，由于负频率的存在，回波的相位特性截然不同。

</br>

**3）相位差和频率差的特性**

* **相位差**：两个回波信号的相位差为：
    $\Delta\phi^\prime = \phi^\prime_{pos} - \phi^\prime_{neg} = (\phi_0 - 2\pi f_{pos} \tau) - (\phi_0 + 2\pi f_{pos} \tau) = -4\pi f_{pos} \tau$

    这个相位差 $\Delta\phi$ 直接与**距离** $R$ 相关（因为 $\tau$ 与 $R$ 相关）。

* **频率差**：如上所述，回波的频率差**不会**因为多普勒效应而改变，始终等于 $f_{pos} - f_{neg}$。

这种特性是双频连续波雷达能够同时测量**速度**和**距离**的基础：多普勒频移用于测速，而两路信号的相位差则用于精确测距。


</br></br>

[#1]:https://wiki.gnuradio.org/index.php/Rational_Resampler    

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_find_max_peak_c_grc.png
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_ts_fft_cc_grc.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_signal_generator_cw_c_grc.png     
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_signal_generator_fmcw_grc.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_split_cc_grc.png
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_static_target_simulator_cc_grc.png
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_msg_manipulator_grc.png
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_usrp_echotimer_cc_grc.png
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/test_uhd_sink_source_inbuild_grc.png
[p13]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_cw_grc.png
[p15]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_dual_cw_grc.png
[p16]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_dual_cw_grc_gui.gif
[p17]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_dual_cw_estimation_rcs_grc.png
[p18]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_sync_pulse_grc.png
[p19]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_fmcw_grc.png     
[p20]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_fmcw_rcs_grc.png
[p21]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_fsk_tracking_singletarget_grc.png    
[p22]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_fsk_tracking_singletarget_gui.gif
[p23]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_ofdm_grc.png
[p24]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/simulator_ofdm_grc.gif
[p25]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_cw_grc.png
[p26]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_dual_cw_grc.png
[p27]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_dual_cw_rcs_grc.png
[p28]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_dual_cw_tracking_grc.png
[p29]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_fmcw_grc.png
[p31]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_fsk_grc.png
[p32]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_fsk_tracking_singletarget_grc.png
[p33]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/usrp_echotimer_sync_pulse_grc.png

