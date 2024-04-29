

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

</br>

### 2.3 科斯塔斯环路（Costas Loop）

https://wiki.gnuradio.org/index.php/Costas_Loop

Costas 环路载波恢复模块，非常适合与 BPSK、QPSK 和 8PSK 同步。 Costas 环路锁定信号的中心频率并将其下变频至基带。



</br>



# 参考链接


[[1]. GNU Radio —— Packet Communications][#1]



[#1]:https://www.gnuradio.org/doc/doxygen/page_packet_comms.html


[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/df/3cf09df390b654b11b2e913b24fd2f.gif
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=/c6/8ec1f9ad8c5896f7d163eb321be6b9.png


