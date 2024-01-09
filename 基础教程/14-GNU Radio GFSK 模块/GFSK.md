
## 1 GFSK 背景知识

调制分类如下：[^[2]^][#2]

![][p6]

** GFSK 是 FSK 的扩展，其中调制信号的频率不会在二进制数据的每个符号周期开始时立即改变。 ** 因此，bit 0-> 1 或反之变得更加平滑。换句话说，与传统的 FSK 相比，调制信号的幅度和相位变化将相对较小。原则上，FSK 是使用独立的本地振荡器分别用于同相和正交分量来实现的，并且振荡器将在每个符号周期开始时切换以生成用于调制的载波频率。一般而言，所有独立振荡器在符号周期开始时不会处于相同的幅度和相位，因此这会导致传输信号的每个比特变化的频率突然变化。因此，调制后的 FSK 信号将非常宽，并且具有不可忽略的旁瓣。下图说明了这一点。

![图 1：给定数字信号的 FSK 调制信号][p3]

信号被正确解码的前提是：在每个符号周期之后具有精确和准确的幅度和相位值。** 如果接收端收到这样的信号，将会造成信道失真、干扰、热再生等，从而降低 FSK 的性能。 **

在 GFSK 调制方案中，需要在基带波形信号前引入高斯滤波器。典型的高斯滤波器是脉冲响应为高斯函数的滤波器（如下图为高斯脉冲响应）

![图 2：高斯滤波器的脉冲响应][p4]

时阈上的高斯函数在频阈上仍是高斯函数，因此该滤波器的频率响应非常窄。当输入信号通过此类滤波器时，与不涉及滤波的 FSK 方案相比，所得到的滤波信号的频谱宽度会减小。**因此，FSK 中频率的任何突然变化都会被滤除，这使得每个符号周期开始时的转换比 FSK 相对平滑**（下图是 GFSK 信号的响应）

![图 3：高斯滤波信号和 GFSK 调制信号响应][p5]

该滤波器的优点是降低边带功率，减少对相邻信道的干扰，但代价是增加码间干扰 (ISI)。**因此，仔细设计具有最佳截止频率的高斯滤波器对于确保最小化 ISI 相关影响非常重要**。此外，还可以使用其他稳健的信号处理和信道均衡技术来克服 ISI 的影响。

调制信号之前的这个滤波阶段也称为脉冲整形，因为数据脉冲被滤除以产生具有急剧上升和下降时间的干净输出信号，这有助于准确确定接收信号的载波频率。GFSK 技术非常有用，广泛用于无线系统和技术，例如改进 Layer 2 protocol,、蓝牙、IEEE 802.15.4 和 Z-wave。

</br>

## 2 GNU Radio GFSK 模块参数详解

**GFSK Mod 的输入是字节流 byte stream，输出是基带复杂调制信号。**

参数 | 意义 | 解释
---|---|---
Samples/Symbol | `Samples per baud >= 2 (integer)` </br> `Default value = 2`| [这有个链接介绍的比较清楚][#5]</br></br>![][p7]
Sensitivity | `Given to the Frequency Mod` </br> `Default value = 1.0`| [Frequency Mod][#8]
BT | `Gaussian filter bandwidth * symbol time (float)`</br>`Default value = 0.35`| 这有个 matlab 关于高斯滤波器的 BT 参数对滤波效果的影响文章</br></br>![][p8]
Verbose | `Prints the value of bits per symbol and BT`</br>`Default value = Off`
Log | `Prints the following modulation data to .dat files:`</br>`* Chunks to Symbol data is written to "nrz.dat"`</br>`* Output of Gaussian filter is written to "gaussian_filter.dat"`</br>`* Output of frequency modulator is written to "fmmod.dat"`</br>`Default value = Off`
Unpack (depreciated in GNU Radio 3.8) | `Unpack input byte stream?`


</br>

**GFSK Demod 的输入是基带复杂调制信号，输出是 a stream of bits unpacked, 1 bit per byte (the LSB)**

参数 | 意义 | 解释
---|---|---
Samples/Symbol | `Samples per baud >= 2 (integer)` |
Sensitivity | `Given to the Quadrature Demod` | 
Gain Mu | `Controls rate of mu adjustment` | 
Mu | `Fractional delay [0.0, 1.0]` | 
Omega Relative Limit | `Sets max variation in omega (float, typically 0.000200 (200 ppm))` |
Freq Error | `Bit rate error as a fraction` | 
Verbose | `Print information about modulator?` | 
Log | `Print modualtion data to files? (bool)` | 


</br>

## 3 GNU Radio GFSK 模块简示例

我们对 9 位长的比特流 `000111011` 进行 GFSK 调制，然后对其进行 GFSK 解调：

![][p1]

</br>

运行后效果如下：

![][p9]

解释：我这里采样率故意设置为 10KHz，这样在时序图中每个采样占用 0.1 MS 方便观察。从图中可以看到信号 2 和信号 3 是一致的，说明我们经过 GFSK 调制解调后数据和原来保持一致。（这里有个 delay 滑动条，用来平移原始信号，方便错开观察的，其数值的意义是延迟 n 个样本）



[[1].什么是 GFSK 调制？][#1]
[[2].Frequency-shift keying][#2]
[[3].GFSK vs FSK][#3]
[[4].Digital GFSK Carrier Synchronization-IEEE][#4]
[[5].Samples Per Symbol][#5]
[[6].FIR Gaussian Pulse-Shaping Filter Design - Matlab][#6]
[[7].数字和模拟滤波器 — 示例][#7]
[[8].Frequency Mod][#8]
[[9].GFSK Demod][#9]

[#1]:https://www.everythingrf.com/community/what-is-gfsk-modulation
[#2]:https://en.wikipedia.org/wiki/Frequency-shift_keying
[#3]:https://www.rfwireless-world.com/Terminology/GFSK-vs-FSK.html
[#4]:https://ieeexplore.ieee.org/document/4145694
[#5]:https://dsp.stackexchange.com/questions/66516/samples-per-symbol-and-number-of-symbols-for-qam
[#6]:https://ww2.mathworks.cn/help/signal/ug/fir-gaussian-pulse-shaping-filter-design.html
[#7]:https://ww2.mathworks.cn/help/signal/examples.html?category=digital-and-analog-filters&s_tid=CRUX_topnav
[#8]:https://wiki.gnuradio.org/index.php?title=Frequency_Mod
[#9]:https://wiki.gnuradio.org/index.php/GFSK_Demod
[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/b2/55323716a60ecad6f7c4ff0c170fae.png
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=/6c/9f7e26850c39d78e1a777dddb35726.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=/90/1336cefd8cf1945c47c0c4c49bd443.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=/d4/8cef01cfd34733a928e9965a3280d3.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=/64/9ec3b64cd1c89b2fbfd3956585344d.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=/e6/e817d8e607c1d574e055a3c7ff8d23.png
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=/29/b27421a424a2748691265e2ab79d93.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=/4c/c548365617de1179c70005ce8236f0.png
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=/40/2e8ee72a7762a550541150185b8020.png







