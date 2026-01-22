
### 一、基础知识
#### 1. 模块概述

**正交解调 (Quadrature Demod)** 模块用于执行频率解调（Frequency Demodulation）。它接收复数基带采样信号，并输出代表瞬时频率变化的浮点数流。

* **应用场景：** 最常用于解调 FM、FSK、GMSK 等通过**频率偏移**传递信息的调制信号。
* **局限性：** 该模块目前**不支持 C++ 代码生成**。若 GRC 流图的输出语言设置为 C++，则无法直接使用此模块。

</br>

#### 2. 核心原理：从相位到频率

**频率调制 (FM)** 的本质是随输入信息同步改变载波的频率。由于频率是相位随时间的变化率（数学上，频率是相位的导数），因此解调的关键在于**计算连续样本之间的相位变化**。

**a）复平面上的相位差**

下图展示了 FM 信号的两个连续样本在 **复数平面（阿甘得图/Argand diagram）** 上的位置。通过计算这两个矢量之间的夹角（相位差），即可还原出该时刻的频率信息。

<img src="https://tuchuang.beautifulzzzz.com:3000/?path=202601/Phase-change-constellation-diagram.png" width="400"/>

</br>

**b）极化鉴别器电路 (Polar Discriminator)**

计算相位变化最有效的方法是将当前样本与前一个样本的 [**共轭版本**][#1] 相乘。其数学描述与标准框图如下：

![][p2]

</br>

#### 3. GRC 等效实现与增益计算

在 GNU Radio 中，`Quadrature Demod` 模块的功能可以通过以下基础模块组合实现：

<img src="https://tuchuang.beautifulzzzz.com:3000/?path=202601/Polar-discriminator-GRC-block-diagram.png" style="clip-path: inset(0 0 10% 0);"/>

* **Complex to Arg (复数转辐角)：** 输出当前样本与前样本之间的相位差  $\Delta\phi$（单位：弧度/Radians）。
* **Multiply Const (乘法常量)：** 对应 `Quadrature Demod` 模块中的 **Gain（增益）** 参数。

</br>

**a）增益 (Gain) 的推导逻辑**

为了将输出转化为物理意义上的频率（Hz）或进行归一化，我们需要进行单位换算：

1. **弧度转周 (Cycles)：** 除以 $2\pi$。
2. **转为频率 (Hz)：** 除以采样周期 $T$（即乘以采样率 $f_s$）。
3. **归一化：** 除以信号的最大频偏 (Deviation)。

综合以上步骤，**归一化增益公式**为：

$$Gain = \frac{f_s}{2\pi \cdot \text{deviation}}$$

**注意：** 在模块中，该频偏默认变量名为 `fsk_deviation_hz`，但这仅是命名惯例，该模块同样适用于模拟 FM（如 WFM 或 NFM）。**常见频偏参考值如下表：**

| 信号类型 | 典型频偏 (Deviation) |
| --- | --- |
| 宽带调频广播 (WFM) | $75\text{ kHz}$ |
| 窄带调频 (NFM/对讲机) | $5\text{ kHz}$ |
| 数字 FSK | 中心频率到传号/空号频率的距离 |

</br>

### 二、示例流程图
#### 示例 1：模拟调频信号

下面显示了模拟调频电台的该模块的示例流程图：

![][p4]

SDR 的输出信号被送至 FFT 低通滤波器，该滤波器仅允许模拟 FM 信号通过。输出信号随后被送至正交解调模块进行频率解调。该模块的 **增益** 设置为 `samp_rate/(2*pi)`。（如果想要输出归一化的信号，即将最大限值设为 ±1，可以将上述公式修改为 `samp_rate/(2*pi*deviation)`，其中 deviation 为发射机的实际频偏，单位为 Hz。对于广播 FM ，这个值是一个标准化的行业规范：`deviation = 75Khz`）

该流程图的输出结果如下所示：

![][p5]

QT GUI 时间接收器的幅度限制为 `+/-100 kHz (100e3)`。通过暂停信号，可以测量电台的最大偏差。

</br>

#### 示例 2：FSK 信号

![][p6]

这个流程图演示了如何从宽带采集文件中解调窄带 FSK 信号：

![][p7]    

这个流图展示了如何把 **正交解调（Quadrature Demod）** 模块当作一个 **FSK（频移键控）信号探测器** 来使用。

首先，**频率转换 FIR 过滤器**就像一个“选台器”，它从宽阔的信号流中把我们要的那一小段窄带信号抠出来，并转成基带信号。

接下来，正交解调模块会输出一串浮点数：

* 如果信号偏向**高频**（代表某个比特），它就输出**正数**；
* 如果频率**没变化**，它就输出 **0**；
* 如果信号偏向**低频**（代表另一个比特），它就输出**负数**。

通过这种方式，它就把频率的变化变回了高低起伏的电信号，完成了 FSK 解调。

在这种场景下，如果你知道高低频率之间的差值（`fsk_deviation`）以及过滤后的采样率（`baseband_samp_rate`），那么给这个模块设置 **增益（Gain）** 参数时，有一个很好用的公式：
**增益 = 采样率 / (π × 频差)**

使用这个公式的好处是：它可以对输出进行“标准化”，确保解调出来的有用信号幅度正好控制在 **-1.0 到 1.0** 之间，既清晰又方便后续处理。

</br>

#### 示例 3：BFSK（2FSK）信号

下面流程图展示了使用 VCO 模块进行BFSK 调制的过程：

![][p9]

下面流程图展示了使用正交解调模块进行 BFSK 信号恢复的过程：

![][p8]    

使用上面 BFSK 进行收发的效果如下：

![][p10]    

</br>

### 参考链接

[[1]. GnuRadio Wiki —— Quadrature_Demod][#2]    
[[2]. GnuRadio Wiki —— Simulation_example:_FSK][#3]     



[#1]:http://www.hyperdynelabs.com/dspdude/papers/DigRadio_w_mathcad.pdf         
[#2]:https://wiki.gnuradio.org/index.php/Quadrature_Demod        
[#3]:https://wiki.gnuradio.org/index.php/Simulation_example:_FSK        
  
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Polar-Discriminator-Delay-Conjugate-Method.png       
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Polar-discriminator-GRC-block-diagram.png    
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/FM-demod-with-quad-demod-block.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Polar-discriminator-output-time-domain.png       
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Quadrature_Demod_flowgraph.png     
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Quadrature_Demod_example.png    
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/RTTY_rcv.png      
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/FSK2_mod_demod.png     
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/BFSK_tx_rx.png     


