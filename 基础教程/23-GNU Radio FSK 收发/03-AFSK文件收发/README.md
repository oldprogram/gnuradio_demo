### 一、背景知识

**BFSK** 和 **AFSK** 的核心逻辑是一样的，都是通过改变“频率”来代表二进制的 0 和 1。它们最大的区别在于**操作的对象**不同：

| 特性 | **BFSK** (二进制频移键控) | **AFSK** (音频频移键控) |
| --- | --- | --- |
| **操作对象** | 直接调制 **射频载波** (RF) | 调制 **音频信号** (Audio) |
| **频率范围** | 高频 (如 MHz, GHz) | 低频 (如 300 Hz - 3000 Hz，人耳可听) |
| **实现方式** | 硬件电路直接控制发射频率 | 通过声卡或音频发生器产生声音 |
| **复杂度** | 较高，需要专门的无线电硬件 | 较低，普通设备（如手机、电脑）即可生成 |
| **典型应用** | 车库门遥控器、寻呼机、底层数传 | 拨号上网调制解调器、业余无线电 (APRS)、紧急警报系统 |

</br>

**1. 什么是 BFSK？**

**BFSK (Binary Frequency Shift Keying)** 是最原始的数字调制方式。它直接让无线电发射机在两个不同的频率之间跳变：

* **频率 A ($f_1$):** 代表逻辑 **1**（传号/Mark）。
* **频率 B ($f_0$):** 代表逻辑 **0**（空号/Space）。

**特点：** 它不经过“声音”这个环节，直接在射频层面切换。这种方式效率很高，信号也比较干净，但通常需要专用的射频芯片来实现。

</br>

**2. 什么是 AFSK？**

**AFSK (Audio Frequency Shift Keying)** 是将数据先转换成“两种不同频率的声音”，然后再把这个声音传给发射机。

* **过程：** 电脑声卡发出两个不同音调的嘀嗒声（例如 $1200\text{ Hz}$ 和 $2200\text{ Hz}$）。
* **传输：** 这些声音通过麦克风接口进入电台，像传输语音一样被发射出去。

**特点：** 它是“二次调制”。如果你在电台旁边，你能亲耳听到数据传输的声音。它的优势是**兼容性极强**，任何能传声音的设备（如对讲机、电话线）都能用来传数据，而不需要改造内部硬件。


---

**核心区别总结**

- **直接 vs 间接：** BFSK 是直接变频；AFSK 是先变音频，再由发射机把音频载到射频上。
- **听觉感受：** BFSK 信号在空气中是无法直接通过音箱听到的；而 AFSK 在发射前就是一段段刺耳的“嘟嘟”声（类似于老式拨号上网或传真机的声音）。
- **带宽：** 理论上 BFSK 更节省频谱资源，而 AFSK 因为经过了音频电路的转换，会受到音频带宽（通常 $3\text{ kHz}$）的限制。


</br>

### 二、使用数据包和 AFSK 进行文件传输

下面展示了一个使用频移键控 (FSK) 向远程接收器发送数据包的示例。数据包的概念在“[数据包通信][#1]”一书中已有详细介绍。以下示例旨在说明 FSK 可以用于发送任何数据内容。

**注意：本教程旨在演示如何使用数据包和 FSK 调制方式在计算机之间传输文件。但是，它不包含前向纠错、流量控制或 TCP/IP 等协议中常见的其他方法。**

本实验使用一个 github 开源项目：[gr-control][#2] 中的一部分，后续有机会我会针对它出一个单独的介绍视频    

![][p1]

</br>

#### 2.1 接收流程图

`pkt_fsk_rcv.grc` 使用与上一节流程图中相同的频率变换 FIR 滤波器正交解调模块接收 AFSK 信号。如果标记频率（Mark frequency=1.2KHz）低于间隔频率（Space frequency=2.2KHz），则 1 和 0 会反转。为了纠正这个问题，使用了一个乘以常数模块，该常数由 QT GUI 选择器设置（选择 reverse 时乘以 -1，否则乘以 1）。

符号同步模块需要一个归一化为 1 的输入信号。为此，使用了自动增益控制 [(AGC) 模块][#3]。[符号同步模块][#4]会检查数据流的多个样本，以查找数据中的转换，其采样点数（以每个符号的采样点数为准）即为数据流的转换点。比特流输入到二进制切片器后，输出为解包后的 1 或 0 字节。

为了检测数据包的开头并实现字节对齐，[关联访问码-标签流块][#5]会检测访问码，并将有效载荷传递给 [Stream_CRC32][#6] 以检查 CRC 是否有效。如果 CRC 有效，则将数据发送到 [File_Sink][#7]。

![][p2]

---
**备注：** 这里重点介绍下[符号同步模块][#4]

**Symbol Sync** 模块用于执行**时钟恢复（Clock Recovery）**。它能够与数字信号中的符号实现同步，提取符号并将其还原为独立的表现形式（例如位/Bit）。由于时钟恢复能将一串符号采样流还原为原始的 1 和 0，因此这通常是解调过程中至关重要的最后一步。该模块是 **Clock Recovery MM** 和 **MSK Timing Recovery** 模块的继任者，后两者目前已被弃用。

Symbol Sync 模块主要执行以下四个步骤：
- **估计并跟踪符号率**：在给定初始“每符号采样数（SPS）”估计值及允许偏差范围的情况下，实时跟踪实际的符号速率。
- **执行定时同步**：进行必要的定时调整，确保信号在最准确的时刻被采样——即每个符号或脉冲达到最大值的时刻。
- **抽取（Decimate）信号**：对信号进行降采样，使输出通常保持为每符号 1 个采样点（用户也可以根据需要设置为多个，但通常是 1 个，有时是 2 个）。
- **适当的滤波**：对信号进行相应的匹配滤波处理。

实质上，Symbol Sync 模块运行着一个循环（通常长度为一个符号的采样周期），并不断调整该循环，直到它与序列中的每个符号完美对齐。

![][p4]

</br>

**Symbol Sync 模块的作用与必要性：**

在数字调制（如 FSK）中，1 和 0 会被映射为特定频率的信号。解调后，我们得到的是一组采样点序列。例如，一段代表 “1” 的标记频率信号会被采样为 `sps`（每符号采样数）个数值。我们的目标是从这堆采样数据中精准还原出最初的位数据。

你可能会想：“这不简单吗？每取连续 `sps` 个点，判断其大多数是 -1 还是 1，进而输出不就行了？”

但在实际操作中，必须面对两个核心挑战：

1. **最佳采样点定位（定时偏移）**：如果采样起始位置偏移（采样在符号切换的边缘而非中心），判定结果就会出错。
2. **采样率漂移（时钟误差）**：受多普勒频移或硬件晶振误差影响，实际的 `sps` 可能并非整数（如 4.001 而非 4）。随着时间推移，这种微小误差会累积，导致固定的采样窗口逐渐“对不准”符号。

因此，我们需要 **Symbol Sync** 模块来“优雅”地处理。它能动态跟踪信号的节奏，实时调整采样位置和间隔，确保始终在波形最稳定的时刻提取数据，从而实现可靠的符号同步。

![][p5]

---

</br>

#### 2.2 发送流程图

`pkt_fsk_xmt.grc` 是发送流程图，其中 `EPB: File Source to Tagged Stream` 是一个 python block 它替代了 File_Source 模块、Stream_to_Tagged_Stream 模块以及 Burst_Shaper 模块的部分功能。该 Python 模块执行以下操作：

- 发送文件级别的前导码，以便接收方进行同步。
- 以 “Pkt_Len” 为单位读取文件。
- 将数据转换为 Base64 编码，即每 3 个字节的输入产生 4 个字节的输出。
- 发送每个带有修改后的 “packet_len” 标签的 Base64 数据块。
- 发送文件后填充消息，以确保所有缓冲区都已刷新。

前导码由百分号“%”后跟 50 个大写字母 “U”，再后跟一个 “]” 组成。它重复四次，以便接收方同步。文件后填充信息发送 10 次。因此整个发送的文件的形式为：`4 x 前导码` + `base64(文件内容)` + `10 x 前导码`。

![][p3]

自定义 python block 对文件处理的流程如下：

| 状态 (State) | 阶段名称 | 发送内容 (Output Items) | 标签长度值 (Tag Value) | 循环/结束条件 |
| :--- | :--- | :--- | :--- | :--- |
| **State 0** | **前导同步码** | 52字节的 `char_list` (主要为 ASCII 85，即 'U') | `self.c_len` (固定 52) | 循环发送 **4 次** 后跳转 |
| **State 1** | **文件数据传输** | 读取 `Pkt_len` 原始数据并进行 **Base64 编码** 后的字节 | `e_len` (Base64 后的实际长度) | 持续循环，直到文件读取完毕 (EOF) |
| **State 2** | **文件名传输** | 8字节 `char_list` 前缀 + 文件名字符串 | `fn_len + 8` (文件名长度 + 8) | 发送 **1 次** 后跳转 |
| **State 3** | **后置填充码** | 52字节的 `char_list` (用于确保数据完全送出缓存) | `self.c_len` (固定 52) | 循环发送 **10 次** 后跳转 |
| **State 4** | **传输结束** | 无数据发送 (time.sleep 10秒) | 无 (返回 0) | 执行 1 次后进入 State 5 (静默) |

之后将每一个 packet_len 长度的数据增加 CRC32，并生成帧头，最终形成一帧数据：`帧头 + payload(packet_len) + CRC32` 

再之后我们就比较熟悉了，分别是将字节流转换为 bit 流，然后 `repeat->multiply->add->vco` 实现 FSK 编码，最终通过 ZMQ PUB 发出。

</br>

#### 2.3 运行

打开两个流程图 `gnuradio-companion pkt_fsk_rcv.grc pkt_fsk_xmt.grc` 分别点击 `RUN->Generate` 在同级文件夹下生成 `pkt_fsk_rcv.py` 和 `pkt_fsk_xmt.py` 两个可执行文件。

接着先运行接收，然后在运行发送：

```
python3 -u pkt_fsk_rcv.py  # 在终端 1 中运行
python3 pkt_fsk_xmt.py --InFile="gr-logo.png"  # 在终端 2 中运行
```

当发送完毕，会看到同级文件夹下会出现一个 `output.tmp` 文件（这个文件就是我们发送的 python block 对文件处理的结果：4 遍 `%U...]` + 文件内容的 base64 格式 + %UUUUUUUgr-logo.png + 10 遍 `%U...]`）

我们如果想要得到原始的文件内容，需要执行下面命令，还原出原本的文件：

```
python3 strip_preamble.py output.tmp output.png
```

</br>

### 参考链接

[[1]. GRC Wiki —— 符号同步][#4]     
[[2]. PDF —— Andy-Walls-Samples-to-Digital-Symbols.pdf][#8]       
[[3]. GitHub —— gr-control][#2]



</br>




[#1]:https://wiki.gnuradio.org/index.php?title=Packet_Communications      
[#2]:https://github.com/duggabe/gr-control/tree/main   
[#3]:https://wiki.gnuradio.org/index.php?title=AGC      
[#4]:https://wiki.gnuradio.org/index.php?title=Symbol_Sync    
[#5]:https://wiki.gnuradio.org/index.php?title=Correlate_Access_Code_-_Tag_Stream     
[#6]:https://wiki.gnuradio.org/index.php?title=Stream_CRC32    
[#7]:https://wiki.gnuradio.org/index.php?title=File_Sink    
[#8]:https://www.gnuradio.org/grcon/grcon17/presentations/symbol_clock_recovery_and_improved_symbol_synchronization_blocks/Andy-Walls-Samples-to-Digital-Symbols.pdf     

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/github_gr_control.png
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/pkt_fsk_rcv_grc.png       
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/pkt_fsk_xmt_grc.png      
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/Symbol_sync_1.png    
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202601/fsk_signal_pic2.png
