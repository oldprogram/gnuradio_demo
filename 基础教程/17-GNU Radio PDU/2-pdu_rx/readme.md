

## 1 接收概述

接收器要比发送复杂得多。这里涉及的工作主要是接收帧的检测和同步。我们必须假设帧以潜在随机时间间隔的突发形式传入。

有一点非常重要：让一个简单的协议在所有场景下工作是非常困难的。我们必须假设一些数据包将由于开始时的漏检或突发处理期间同步统计数据不佳而丢失。

通用接收器示例可以在 packet_rx.grc 中找到。该层次块提供 PHY 帧的主要检测、同步、标头/有效负载管理、解调和解码。


## 2 相关块介绍
### 2.1 相关性估计器（Correlation Estimator）

https://wiki.gnuradio.org/index.php/Correlation_Estimator

相关估计器模块将输入信号与提供的样本向量相关联。该块设计用于通过相关搜索同步字，并使用相关结果来获得时间和相位偏移估计。这些估计作为流标签向下游传递，以供后续同步块使用。

下图是其工作原理：相关块将传入的样本流与已知模式进行比较，当存在匹配时达到峰值。最常见的相关码是巴克码。此处显示了 7 位巴克码。


![][p1]

下面是采用 BPSK 编码的 8 字节前导码，sps 为 4 的匹配效果图（test_corr_est.grc）：

![][p2]

- bit 数为 8*8*4 = 256 个
- 采用 100Khz 采样显示的 QT GUI Time Sink 图，因此每一个数据占 0.01 ms
- 图中从开始有峰值到最高峰时间大约：521.29-518.72，再除以 0.01 能够得出这段时间大致的数据个数：256.9999
- 算上我们肉眼看起始时间的误差，基本上符合理论计算：前导码完全匹配时峰值最大

此外，标签输出分别为：

- phase_est：相位偏移的估计。 phase_est 标签可由下游模块用来调整其相位估计器/校正循环，目前由 Costas Loop 模块实现。
- time_est：符号定时偏移的估计。 time_est 标签可用于调整任何下游同步块（例如Symbol Sync ）的采样定时估计。
- corr_est：估计的相关值(从图中还不知道为什么是那个值)
- amp_est：超过估计幅度 1。估计幅度是块处理的时间窗口中任何一个样本的最大幅度（至少包括整个同步字）
- corr_start：相关性的起始样本及其值（与 corr_est 相同的值）

</br>

### 2.2 多相时钟同步（Polyphase Clock Sync）

https://wiki.gnuradio.org/index.php/Polyphase_Clock_Sync

使用多相滤波器组的定时同步器。

该模块通过最小化滤波信号的导数来执行定时同步，从而最大化 SNR 并最小化 ISI（符号间干扰）。

**多相时钟同步模块的详细信息**

我们可以使用多种算法来恢复接收器的时钟，几乎所有算法都涉及某种反馈控制环路。那些没有使用反馈的通常使用前导码。多相时钟同步块为我们做了三件事：首先，它执行时钟恢复；其次，它使用接收器匹配滤波器来消除 ISI；第三，它对信号进行下采样。

该模块的工作原理是计算输入信号的第一个差分，该差分与其时钟偏移相关。如果我们首先非常简单地模拟这一点，我们就可以看到差分滤波器如何为我们工作。

如下：`symbol_differential_filter.grc`

![][p3]

1）原始数据为：49 个 0 + 1 + 50 个 0,总共 100 个数据。
2）经过 32K 节流阀限制速度
3）送入内插 FIR 滤波器：采用 4 倍内插，数据变为 100*4 个，同时对数据实施 RRC 卷积（因此，看到的运行图中一个周期 400 个数据，大约 12.5ms）
4）然后送入多相任意重采样：这里没有实施滤波，仅仅进行 1.2 倍重采样，因此数据变为：400*1.2，周期变为 15ms
5）然后送入抽取 FIR 滤波器：这里的抽取率为 1 表示没有抽取，仅仅实施了 RRC 滤波（因此总样本没变，总周期没变）
6）然后分两路：一路送入 delay 1 的块，产生延时 1 sample/items 的效果，本质为 out[n] = in[n-1]；一路送入抽取 FIR 滤波器，实施差分滤波（本质是 out[n] = in[n-2]-in[n]，其实是微分过程）

因为我们采样最理想的点在第一路数据的峰值点，即微分为 0 的点（斜率），上面第 6 步骤比较巧妙的实现了：第二路接近 0 时，对应第一路的峰值点，也就是最佳采样点。运行效果如下：

![][p4]

实际上，我们不是使用单个滤波器，而是使用一组有不同相位的滤波器 `symbol_differential_filter_phases.grc`：

![][p5]

1）原始数据没变，节流阀没变，4 倍内插没变，1.2 倍多相任意重采样没变，仅实施 RRC 的抽取滤波器没变
2）然后分 6 路：一路直出；5 路分别实施分数重采样，分数重采样可以轻松实现相移（0～1），可以将 5 路滤波器理解为将单位圆（0～2pi）分割为 5 等份。由于该滤波器除了进行相移之外，还会产生延时（实测发现：0 相位重采样时会丢弃 3 个样本，即：out'[n] = in[n+3]），因此后续我们用延时块进行矫正。
- 第 1 路直出：out'[n] = in[n]
- 第 2 路 0 相移，因此使用 [-1.0,1] 进行差分滤波，out[n] = in[n-2]-in[n]，delay 1 会产生 out'[n] = out[n-1] = in[n-3]-in[n-1]
- 其他 4 路有非 0 相移，使用 [0,-1,0,1] 进行差分滤波，out[n] = in[n-3]-in[n-1]，delay 1 会产生 out'[n] = in[n-4]-in[n-2]
- PS：由于 2～5 路实施了分数重采样，因此作用 3 个样本丢弃，最终公式为：
	- out'[n] = in[n]-in[n+2]
	- out'[n] = in[n-1]-in[n+1]

运行效果如下：

![][p6]

我们可以看到：d(sym0)/dt + phi3 的信号在 0 处有一个采样点。这告诉我们，我们的理想采样点发生在这个相位偏移。因此，如果我们取接收器的RRC滤波器，并通过 phi3 (which is 3*2pi/5) 调整其相位，则我们可以校正时序失配，并在该采样时间选择理想的采样点。

上面的方法是采用开环方式来做选择，不能做到自动选择，此时需要引入二阶控制回路：控制回路从其中一个滤波器开始，并计算输出作为误差信号。然后，它与误差信号成比例地在滤波器组中向上或向下移动，因此我们试图找到误差信号最接近0的位置。这是我们针对采样点的最佳滤波器。因为我们预计发射和接收时钟会相对彼此漂移，所以我们使用二阶控制环路来获取正确的滤波器相位以及两个时钟之间的速率差。

下面流程图 `Qpsk_stage3.grc` 展示了获取通道模型输出的 QPSK 信号，传递到 Polyphase Clock Sync 模块。该块设置有 32 个滤波器和 2pi/100 的环路带宽。

![][p7]

运行此流程图时，我们看到由于 32 个滤波器之后的 ISI，星座图仍然有一点噪声，但一旦我们将通道噪声电压设置调整为大于 0，它很快就会被噪声吸收。(图中绿色为未经过多相时钟同步的星座图，蓝色为经过多相时钟同步的星座图，当噪声为 0 时，调节 timing offset 观察时钟同步效果)

![][p8]


</br>



### 2.3 科斯塔斯环路（Costas Loop）

https://wiki.gnuradio.org/index.php/Costas_Loop

Costas 环路载波恢复模块，非常适合与 BPSK、QPSK 和 8PSK 同步。 Costas 环路锁定信号的中心频率并将其下变频至基带。



</br>



# 参考链接


[[1]. GNU Radio —— Packet Communications][#1]
[[2]. GNU Radio —— 符号同步][#2]
[[3]. 百度百科 —— 微分][#3]
[[4]. GNU Radio —— 分数重采样器（最小均方误差滤波）][#4]
[[5]. 维基百科 —— 最小均方误差][#5]
[[6]. 论坛 —— 分数重采样器丢失样本][#6]


[#1]:https://www.gnuradio.org/doc/doxygen/page_packet_comms.html
[#2]:https://wiki.gnuradio.org/index.php/Symbol_Sync
[#3]:https://baike.baidu.com/item/%E5%BE%AE%E5%88%86/317988?fr=ge_ala
[#4]:https://wiki.gnuradio.org/index.php/Fractional_Resampler
[#5]:https://en.wikipedia.org/wiki/Minimum_mean_square_error
[#6]:https://discuss-gnuradio.gnu.narkive.com/P9K43igR/fractional-resampler-discards-samples

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/df/3cf09df390b654b11b2e913b24fd2f.gif
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=/c6/8ec1f9ad8c5896f7d163eb321be6b9.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=/18/cfe7953e913a43a349db123c242e99.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=/62/d78ffa73c8e216477f60a2a7d5539f.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=/39/fa74efd0e77a1b2c5810787ef12179.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=/4c/0b1b34474088d50e45c2d67823682f.png
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=/61/a3c3191087341f6b6c9158d45528bb.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=/22/daa45131de51c558e2b8bec5631f89.png


