### 一、OFDM 数据准备阶段
#### 1.1、ofdm header 和 ofdm payload 生成
##### 1.1.1 包生成与CRC32

![][p1]

随机数每次生成 1K 级别的 0～255 的随机数，然后以 96 字节级别打包，针对每个包增加一个 crc32，最终形成 100 字节的包

##### 1.1.2 基于星座技术包头和 payload 生成

![][p2]

Packer Header Generatar 基于 header_formatter 的格式要求，对随机数据+CRC32 生成包头（详细见 1.2 header 生成深入理解）
随机数据+CRC32 经过 Repack Bits (8/2) 准备做 QPSK 编码（每个输入的1字节，包含 8bits 信息 ; 每个输出 1 字节包含 2bits 信息)

接着将 header 数据和经过 8/2 变化的随机数据+CRC32 的数据送入星座编码（Chunks to Symbols），对于 header 实施 BPSK，对于 payload 实施 QPSK。(从 byte 变为复数，BPSK的星座是极坐标的两个点，QPSK 是极坐标中的 4 个点）

```BASH
>>> from gnuradio import digital
>>> digital.constellation_qpsk().points()
[(-1.4142135381698608-1.4142135381698608j), (1.4142135381698608-1.4142135381698608j), (-1.4142135381698608+1.4142135381698608j), (1.4142135381698608+1.4142135381698608j)]
>>> digital.constellation_bpsk().points()
[(-1+0j), (1+0j)]
```

最后将 head 和 payload 合并（一前一后拼接）形成 448 字节的带标记的复数流，用于后续的 OFDM。

</br>

#### 1.2、header 生成深入理解
##### 1.2.1 Packet Header Generator

https://wiki.gnuradio.org/index.php/Packet_Header_Generator
为带标签的流式数据包生成标头。
输入：带标签的字节流。这将被完全消耗，不会附加到输出流。
输出：包含标头的标记流。标头的详细信息在标头格式化程序对象（类型为 packet_header_default 或其子类）中设置。要使用默认标头，请参阅[数据包标头生成器（默认）][#1]。

##### 1.2.2 Packet Header Generator (Default)

根据指定的长度为带标记的流式数据包生成默认标头。该块是数据包标头生成器的特例
输入：带标签的字节流。这将被完全消耗，不会附加到输出流。请注意，每个字节使用了所有 8 位。
输出：包含标头的标记流。

##### 1.2.3 gr::digital::packet_header_default 类参考

https://www.gnuradio.org/doc/doxygen/classgr_1_1digital_1_1packet__header__default.html

![][p3]

##### 1.2.4 ofdm header 格式与解析

**ofdm 格式如下：**

Encodes the header information in the given tags into bits and places them into out.    
Uses the following header format: 

- Bits 0-11: The packet length (what was stored in the tag with key len_tag_key) 
- Bits 12-23: The header number (counts up every time this function is called) 
- Bit 24-31: 8-Bit CRC 
- All other bits: Are set to zero

If the header length is smaller than 32, bits are simply left out. For this reason, they always start with the LSB.

However, it is recommended to stay above 32 Bits, in order to have a working CRC.

Reimplemented in [gr::digital::packet_header_ofdm][#2].

翻译为中文是：
0-11 bits(12bits）： 数据包长度
12-23 bits(12bits)：标头编号（每次调用进行累加）
crc8 (8bits)：
others (设置为0），对于 packer_header_ofdm ：

**下面是 ofdm 头生成的核心代码：**

```PYTHON
from gnuradio import digital

occupied_carriers = (list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)),)
length_tag_key = "packet_len"
header_mod = digital.constellation_bpsk()
payload_mod = digital.constellation_qpsk()

header_formatter = digital.packet_header_ofdm(
    occupied_carriers,                                 # See carrier allocator //(48个)
    n_syms=1,                                          # The number of OFDM symbols the header should be (usually 1)
    len_tag_key=length_tag_key,                        # The tag key used for the packet length (number of bytes) 
    frame_len_tag_key=length_tag_key,                  # The tag key used for the frame length (number of OFDM symbols, this is the tag key required for the frame equalizer etc.)
    bits_per_header_sym=header_mod.bits_per_symbol(),  # Bits per complex symbol in the header, e.g. 1 if the header is BPSK modulated, 2 if it's QPSK modulated etc.
    bits_per_payload_sym=payload_mod.bits_per_symbol(),  # Bits per complex symbol in the payload. This is required to figure out how many OFDM symbols are necessary to encode the given number of bytes.
    scramble_header=False                              # Set this to true to scramble the bits. This is highly recommended, as it reduces PAPR spikes.
)

print(digital.packet_headergenerator_bb(header_formatter.base(), length_tag_key))
```

<font color=#FF000> **我在流程图中新增一个 python 块，用于 debug，解析实时的 header 信息：** </font>

![][p4]

将 Embedded Python Block 的 debug 参数设置为 True，点击 RUN-> Generate，会在流程图的同级目录生成一个 tx_ofdm.py

在终端中运行：(便可以看到对 header 的实时解析）

```BASH
➜  OFDM python tx_ofdm.py
...
one input, input_offset = 00050448 --> 
data_lsb[000000/000192]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 01 01 00 01 01 00 00 00 00 00 01 00 idx| 00 00 00 00 00 00 00 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
data_lsb[000048/000192]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 00 00 01 01 01 00 00 00 00 00 01 00 idx| 01 01 00 01 00 01 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
data_lsb[000096/000192]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 01 00 01 01 01 00 00 00 00 00 01 00 idx| 00 01 01 01 01 01 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
data_lsb[000144/000192]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 00 01 01 01 01 00 00 00 00 00 01 00 idx| 01 00 00 00 00 00 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]

one input, input_offset = 00050640 --> 
data_lsb[000000/000144]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 01 01 01 01 01 00 00 00 00 00 01 00 idx| 00 00 01 00 01 00 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
data_lsb[000048/000144]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 00 00 00 00 00 01 00 00 00 00 01 00 idx| 00 01 01 01 00 01 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
data_lsb[000096/000144]=[00 00 01 00 00 01 01 00 00 00 00 00 len| 01 00 00 00 00 01 00 00 00 00 01 00 idx| 01 01 00 01 01 01 01 00 crc| 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |other]
```

**注意：**    
1）<font color=#FF000> **为什么不直接点运行，而是在终端中运行？** </font>因为终端中运行看 log 方便，且不容易卡    
2）Embedded Python Block，<font color=#FF000> **每次输入有多个 header（48字节，注意是小端模式），通过 packet_len 标签进行标记，因此代码用了一些标签处理的知识** </font>： https://wiki.gnuradio.org/index.php?title=Python_Block_Tags    

</br>

### 二、OFDM 阶段

OFDM 本质是分批运输：

![][p5]

#### 1.1、OFDM Carrier Allocator
##### 1.1.1 参数及意义

![][p6]

https://wiki.gnuradio.org/index.php/OFDM_Carrier_Allocator

参数 | 本案例中的值 | 意义
---|---|---
FFT length | 64 | FFT长度也是OFDM符号的最大宽度、输出矢量大小和占用载波和导频载波中元素的最大值</br></br>FFT length, is also the maximum width of the OFDM symbols, the output vector size and maximum value for elements in occupied_carriers and pilot_carriers.
Occupied Carriers | (list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)),)</br></br>([-26, -25, -24, -23, -22, -20, -19, -18,</br>-17, -16, -15, -14, -13, -12, -11, -10,</br>-9, -8, -6, -5, -4, -3, -2, -1,</br>1, 2, 3, 4, 5, 6, 8, 9,</br>10, 11, 12, 13, 14, 15, 16, 17,</br>18, 19, 20, 22, 23, 24, 25, 26],)    --> 48</br></br>IEEE 802.11a 标准建议在 -26 到 +26 的子载波上进行传输，总共 52 个子载波。这就是我们现在在示例中使用的内容。该子载波索引是相对于索引 0 处的某个中心载波频率的。子载波之间的频率间隔将由 FFT 的大小来确定。</br></br>根据 IEEE 标准，底部 6 个子载波和顶部 5 个子载波是空的。这通常是为了防止过度的带外发射。对信号应用低通滤波器时也很方便。</br></br>此外，零子载波为空。这也是对在载波频率上具有干扰的硬件设备的测量，特别是具有调谐到载波频率的振荡器的同步器。 | A vector of vectors of indexes.</br></br>Example: if occupied_carriers = ((1, 2, 3), (1, 2, 4)), the first three input symbols will be mapped to carriers 1, 2 and 3. After that, a new OFDM symbol is started. The next three input symbols will be placed onto carriers 1, 2 and 4 of the second OFDM symbol. The allocation then starts from the beginning. </br></br>Order matters! 秩序很重要！The first input symbol is always mapped onto `occupied_carriers[0][0]`.
Pilot Carriers | ((-21, -7, 7, 21),)  --> 4 | The position of the pilot symbols（导频符号的位置）. Same as occupied_carriers, but the actual symbols are taken from pilot_symbols instead of the input stream.但是实际符号取自导频符号而不是输入流。
Pilot Symbols | ((1, 1, 1, -1),)</br></br>最后，导频子载波（-21，-7，7，21）也包含接收机已知数据。这些序列用于各种各样的目的，并且依赖于协议。这里，导频序列是（1，1，1、-1），每个导频音一个符号。 | The pilot symbols which are placed onto the pilot carriers. pilot_symbols[0][0] is placed onto the first OFDM symbol, on carrier index pilot_carriers[0][0] etc.</br></br>放置在导频载波上的导频符号。pilot_symbols[0][0] 被放置在第一个 OFDM 符号上、载波索引 pilot_carriers[0][0] 等上。
Sync Words | (sync_word1, sync_word2)</br>[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, -1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, -1.41421356, 0.0, -1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, -1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, 1.41421356, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]</br></br>[0, 0, 0, 0, 0, 0, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 0, 0, 0, 0, 0]</br></br>需要注意的是，导言（同步词的组合）不遵循这些规则。同步字在导频子载波上发送非导频序列。（64+64） | OFDM symbols that are prepended to the OFDM frame (usually for synchronisation purposes, e.g. OFDM symbols with every second sub-carrier being idle). Is a vector of complex vectors of length fft_len</br></br>准备到 OFDM 帧的 OFDM 符号（通常用于同步目的，例如，具有空闲的每二个子载波的 OFDM 符号）。是长度为 fft_len 的复向量的向量
Length tag key | packet_len | The key of the tag identifying the length of the input packet.
Shift Output | true | Whether to 'fftshift' the output OFDM symbols. 如果使用，则应实例化后续 FFT，以使其知道输入被移位。默认值为 true。

##### 1.1.2 总结该块的功能

将第一节形成的 448 字节的  Pre-OFDM 数据，分为 64 个子载波传输（FFT length），这 64 个中：

- ([-26, -25, -24, ... 22, 23, 24, 25, 26],) 48（Occupied Carriers） 个用于运输 Pre-OFDM 数据，
- ((-21, -7, 7, 21),) 4(Pilot Carriers) 个用于运输导波，导波数据（Pilot Symbols）是：((1, 1, 1, -1),)
- 底部 6 个子载波和顶部 5 个子载波是空的。这通常是为了防止过度的带外发射。对信号应用低通滤波器时也很方便
- 零子载波为空。这也是对在载波频率上具有干扰的硬件设备的测量，特别是具有调谐到载波频率的振荡器的同步器。

实际发送时，先在 64 个子载波上发送 Sync Words 1，然后再发送 Sync Words 2，然后再将 448 字节数据按照 Occupied Carriers 的顺序分配到每个子载波上，不足 48 的整数倍，进行补 0。

</br>

<font color=#FF000> 同 header debug python block，这里我也做了一个用于打印64路子波数据的调试块：</font>

![][p7]

将 Embedded Python Block 的 debug 参数设置为 True，点击 RUN-> Generate，会在流程图的同级目录生成一个 tx_ofdm.py

在终端中运行：(便可以看到对 64 路子波的实时数据）

![][p8]

图中是为了好看：
- b0 ->  (-1+0j)    <BPSK>
- b1 -> (1+0j)
- q0 -> (-1.4142135381698608-1.4142135381698608j) <QPSK>
- q1 -> (1.4142135381698608-1.4142135381698608j)
- q2 -> (-1.4142135381698608+1.4142135381698608j)
- q3 ->  (1.4142135381698608+1.4142135381698608j)
- x0 -> 0                   <同步字的编码>
- x- -> -1.41421356
- x+ -> 1.41421356

</br>

#### 1.2、FFT
##### 1.2.1 参数及意义

![][p9]

https://wiki.gnuradio.org/index.php?title=FFT

该块采用浮点或复数值的矢量并计算FFT。如果您只想查看信号的频域，QT GUI frequency Sink对用户更友好。

请注意，即使输入信号是 real 的，输出也将是 complex 的，因此如果您想查看幅度，则必须使用 complex to Mag 或类似的块。

参数 | 本案例中的值 | 意义
---|---|---
FFT Size | fft_len = 64 | Number of samples used in each FFT calculation, which also determines how many points are in the output.</br>每个FFT计算中使用的样本数，这也决定了输出中有多少点。
Forward/Reverse | Reverse | Whether to do an FFT or IFFT.
Window | () | Type of window to apply to each set of samples before the FFT is taken, default is a blackmanharris window. The argument of the window.blackmanharris() function is simply how many points in the window, which must match the FFT size. If an empty window "[]" is supplied then no windowing math is performed.</br></br>在进行FFT之前应用于每组样本的窗口类型，默认为blackmanharris窗口。window.blackmanharris（）函数的参数只是窗口中必须与FFT大小匹配的点的数量。如果提供了空窗口“[]”，则不执行开窗运算。
Shift | yes | Whether or not to do an "fft shift" which puts DC (0 Hz) in the center. If you are not sure what this means, leave it set to Yes. Only active when input type is complex.</br></br>是否进行将DC（0 Hz）置于中心的“fft移位”。如果您不确定这意味着什么，请将其设置为“是”。仅当输入类型复杂时才处于活动状态。
Num Threads | 1 | Number of threads to assign to perform the FFTs.</br>要分配以执行FFT的线程数。

##### 1.2.2 总结该块的功能

该块负责 IFFT， Using Inverse FFT to create the OFDM symbol（使用逆FFT创建OFDM符号）（通过借助 FFT 和 IFFT 特性，实现数据的时域频域切换与还原）：

![][p10]

</br>

#### 1.3、OFDM Cyclic Prefixer
##### 1.3.1 参数及意义

![][p11]

https://wiki.gnuradio.org/index.php?title=OFDM_Cyclic_Prefixer

添加循环前缀并对OFDM符号执行脉冲整形。

**输入**

OFDM符号（在时域中，即IFFT之后）。可选地，可以处理整个帧。在这种情况下，必须指定长度标签密钥，该密钥保存表示帧中有多少OFDM符号的标签的密钥。

**输出**

一种（标量）复符号流，包括循环前缀和脉冲整形。

注：如果处理了完整的帧，并且 Rolloff 大于零，则最后的 OFDM 符号后面跟着脉冲整形的延迟线。脉冲形状是时域中的升余弦。

参数 | 本案例中的值 | 意义
---|---|---
FFT Length | fft_len = 64 | FFT Length (i.e. length of the OFDM symbols)
CP Length | fft_len//4 | Cyclic prefix length (in samples)</br>前缀是符号时间的 10% 到 25% 之间的任意位置
Rolloff | rolloff = 0 | Length of the rolloff flank (in samples). 该参数有时可被描述为 FFT 长度的百分比，因此： Rolloff (%) = (Rolloff (samples)/ FFT_len) * 100.</br></br>An explanation of this parameter can be found here
Length Tag Key | packet_len | For framed processing, the key of the length tag -> 对于帧处理，长度标记的键

##### 1.3.2 总结该块的功能

该块负责增加循环前缀：

![][p12]

延迟扩散就像你可能从前面的车上得到的不想要的飞溅。在衰退过程中，前面的符号同样向后飞溅，我们希望避免这种情况。

增加与前车的距离以避免飞溅。信号向后移动中间出现空白，实际信号不能用空（喜欢连续信号的硬件不适合），可以采用（扩展符号，使其长度为1.25倍 -> CP Length = fft_len//4）下图的方式实现：

![][p13]

循环前缀是我们添加到珍贵货物前面的多余信号，即符号
Cyclic prefix is this superfluous bit of signal we add to the front of our precious cargo, the symbol.

</br>

因此，一个完整的 OFDM 过程如下：

![][p10]

</br>

### 三、附件
#### 3.1、流程图
##### 3.1.1 流程图

![][p14]

</br>

##### 3.1.2 效果图

![][p15]

</br>

##### 3.1.3 如何体验

1）**简单体验**：打开流程图，点击运行，可以看到 3.1.2 的效果图（包含 pre-OFDM 的 header 和 data 数据；经过 OFDM 的时域图和频域图）    
2）**深入理解 pre-OFDM 数据的形成体验**：参考 1.2，将 Embedded Python Block 的 debug 参数设置为 True，点击 RUN-> Generate，会在流程图的同级目录生成一个 tx_ofdm.py ，在终端中运行 python tx_ofdm.py 便可以看到对 header 的实时解析    
3）**深入理解 OFDM 子载波分配、同步字、导波、数据载波等细节的体验**：参考 1.1.2，将 Embedded Python Block 的 debug 参数设置为 True，点击 RUN-> Generate，会在流程图的同级目录生成一个 tx_ofdm.py，在终端中运行 python tx_ofdm.py  便可以看到对 64 路子波的实时数据    

</br>

#### 3.2、参考资料

[1]. https://www.ee.iitb.ac.in/course/~vishrant/ofdm-tranmission-reception.pdf    
[2]. https://github.com/rwth-ti/gr-ofdm    
[3]. 一本好书中介绍 OFDM：https://complextoreal.com/wp-content/uploads/2013/01/ofdm2.pdf（非常详细，英文图文并茂，一个就够） 22-正交频分复用（OFDM，DMT）    
[4]. 维基百科 OFDM：https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing    
[5].《面向工程师的软件定义无线电，2018 年》：第 10 章：正交频分复用(pdf) https://www.analog.com/en/resources/technical-books/software-defined-radio-for-engineers.html    
[6]. gnu radio 推荐阅读：https://wiki.gnuradio.org/index.php?title=SuggestedReading    
[7]. gnu radio :    https://wiki.gnuradio.org/index.php/Basic_OFDM_Tutorial     
  https://wiki.gnuradio.org/index.php/OFDM_Transmitter    
                        https://www.gnuradio.org/doc/doxygen-3.7.3/page_ofdm.html    
[8]. 论文：OFDM Simulation Using GNURadio on Dynamic Channels https://www.atlantis-press.com/article/125984561.pdf    
[9]. 深入探讨 GNURadio 中的 OFDM 实现：https://esrh.me/posts/2022-07-25-gnuradio-ofdm    
[10]. Implementation of OFDM systems using GNU Radio and USRP：https://ro.uow.edu.au/cgi/viewcontent.cgi?referer=&httpsredir=1&article=4984&context=theses    
[11]. Using the GNU Radio Software in the OfdmMulticarrier Communications：https://iopscience.iop.org/article/10.1088/1755-1315/172/1/012032/pdf    
[12]. gr-ofdm GNU Radio module：https://github.com/rwth-ti/gr-ofdm    
[13]. 知乎：OFDM（正交频分复用）技术：https://zhuanlan.zhihu.com/p/137712898（基础，好理解）    
[14]. CSDN：给“小白”图示讲解OFDM的原理（需要VIP）：
https://blog.csdn.net/madongchunqiu/article/details/18614233（讲的不错，需要VIP）    
https://zhuanlan.zhihu.com/p/548423594（不要VIP）    
[15]. 博客园：【OFDM 】给“小白”图示讲解OFDM  （图不错）    
[16]. 知乎：一文详解 OFDM 系统：https://zhuanlan.zhihu.com/p/646179637（偏学术，不好理解）    
[17]. 杂网站:【通信篇】OFDM技术（一）:https://www.eet-china.com/mp/a201038.html (ppt,挺好理解）    
[18]. https://filterbankmulticarrier.projekte.fh-hagenberg.at/ofdm.html    正交频分复用    
[19]. https://liquidsdr.org/doc/ofdmflexframe/ OFDM灵活帧结构（ofdmflexframe）    
[20]. 深入探讨 GNURadio 中的 OFDM 实现：https://esrh.me/posts/2022-07-25-gnuradio-ofdm    
[21]. 从头到尾：GNU Radio 与 CorteXlab 使用 USRP：https://www.cortexlab.fr/doku.php?id=from_gnuradio_to_cortxlab    



[#1]:https://wiki.gnuradio.org/index.php/Packet_Header_Generator_(Default)    
[#2]:https://www.gnuradio.org/doc/doxygen/classgr_1_1digital_1_1packet__header__ofdm.html#ad6e9a54a7f368dffb5cdbf7badc524e4    

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_and_crc32.jpg    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_modulate.jpg    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_header_format.jpg    
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_header_debug.jpg    
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_as_trucking.jpg    
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_carrier_allocator_gr_block.jpg    
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_carrier_debug.jpg    
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_carrier_debug_data.jpg    
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_fft.jpg    
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_fft_ifft.jpg    
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_cyclic_prefixer.jpg    
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_cyclic_prefixer_as_car.jpg    
[p13]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_package_cyclic_prefixer_principle.jpg    
[p14]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_gnuradio.jpg    
[p15]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ofdm_tx_gnuradio_rendering.jpg    






