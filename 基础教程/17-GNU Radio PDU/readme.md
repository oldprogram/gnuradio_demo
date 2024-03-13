
## 1 PDU 概述

在电信领域，**协议数据单元（PDU）[^[1]^][#1]** 是指在计算机网络的对等实体之间传输的单个信息单元。它由协议特定的 **控制信息** 和 **用户数据** 组成。在通信协议栈的分层架构中，每一层都实现针对特定类型或数据交换模式定制的协议。

例如，传输控制协议（TCP）实现了面向连接的传输模式，该协议的 PDU 被称为段，而用户数据协议（UDP）则使用数据包作为 PDU 进行无连接通信。在互联网协议族的较底层，即互联网层，PDU 被称为数据包，而不考虑其有效载荷类型。

本文将以一些列的例子来了解 GNU Radio 的 PDU 相关操作。为我们使用数字调制传输文件、音频、视频等数据打好基础。


</br>

## 2 Demo 详解
### 2.1 Random PDU Generator

该块在启动时发送一次随机 PDU，然后每次收到消息时发送，第一个 demo 如下 `pdu_simple_demo1_random.grc`：[^[2]^][#2]

</br>

![][p1]

运行后，每隔 2S 产生一个 PDU：

```
message_debug :info: The `print_pdu` port is deprecated and will be removed; forwarding to `print`.
***** VERBOSE PDU DEBUG PRINT ******
()
pdu length =        110 bytes
pdu vector contents = 
0000: 69 e4 6c f5 94 8c 28 23 c3 26 3a 41 cf d7 fd 41 
0010: 55 d0 4c 3e 03 ed 37 59 e8 32 d9 40 f4 9d c7 79 
0020: fc 5a 11 d4 cb 95 98 8c bb ea b1 49 ae c1 64 c0 
0030: 8f 61 35 91 87 13 67 0d 5a 87 97 c7 5b ef f7 21 
0040: 27 91 65 78 63 03 ba 56 63 29 ed cb 6f 4f dc 87 
0050: 9e 2a 1e 9a 78 43 57 a7 87 b0 b7 bf fd 73 b8 15 
0060: e9 3a 81 e9 8e 27 80 d3 76 89 8b ff 72 14 
************************************
```

其四个参数分别影响：PDU 长度范围最少为 15，最大为 150 字节，mask 与 pdu 每一字节做 AND 操作，总长度必须是 `Length Modulo` 的倍数。

</br>

### 2.2 Async CRC32

在 3.10 版本该块已经被 `CRC_Append` 和 `CRC_Check` 替换。[^[4]^][#4]

该块用于处理异步消息的字节流，可以选择 create 模式和 check 模式：

- create：在 pdu 数据后面多加 4 字节，即输入数据的 CRC32
- check：计算输入数据的 LEN(PDU)-4 的 CRC32 和 PDU 最后 4 字节是否相等，相等输出去除 CRC32 的数据，不相等没有输出。

例子如下 `tx_stage1.grc`：

![][p5]

输出 LOG：

```
Press Enter to quit: ***** VERBOSE PDU DEBUG PRINT ******
()
pdu length =         44 bytes
pdu vector contents = 
0000: 22 e7 d5 20 f8 e9 38 a1 4e 18 8c 47 30 8c fe f5 
0010: ff f7 f7 28 b9 f8 fb f5 1c 7c cc cc 4c 24 01 6b 
0020: 1c ea a3 ca e0 f5 80 a7 cc 09 5c d9 
************************************
***** VERBOSE PDU DEBUG PRINT ******
()
pdu length =         48 bytes
pdu vector contents = 
0000: 22 e7 d5 20 f8 e9 38 a1 4e 18 8c 47 30 8c fe f5 
0010: ff f7 f7 28 b9 f8 fb f5 1c 7c cc cc 4c 24 01 6b 
0020: 1c ea a3 ca e0 f5 80 a7 cc 09 5c d9 db 73 02 76 
************************************
```

</br>

### 2.3 Protocol Formatter (Async)

一个数据帧一般由 `帧头 + 内容 + 校验（帧尾）` 构成，这个例子介绍如何添加帧头 `tx_stage3.grc`：

![][p8]


**1）Default Header Format Obj**

Default Header Format Obj [^[14]^][#14] 用于 PDU 格式化的默认标头格式化程序。用于处理默认的数据包头。默认标头由访问代码和数据包长度组成。长度被编码为重复两次的 16 位值：

```
 | access code | hdr | payload |
```

当 access code <= 64 bits 时 hdr 为:

```
 |  0 -- 15 | 16 -- 31 |
 | pkt len  | pkt len  |
```

访问代码和标头按照网络字节顺序进行格式化。

该标头生成器不会计算 CRC 或将 CRC 附加到数据包中。在添加标头之前，请使用 CRC32 异步块。

**因此：** 流程图中的设置意义如下：

- Access Code：'10101010111101010101'，最长为 64 bits，用于其他块去查找包的起始位置（**测试发现，最终输出的 Aceesss Code 总是 8bits 倍数，从右向左数 8 倍数个 bits**）
- Threshold：（临界点）访问代码中有多少位可能是错误的，但仍然算作正确
- Payload Bits per Symbol：有效负载调制器中使用的每个符号的位数

</br>

**2）Protocol Formatter (Async)**

Protocol Formatter (Async) [^[15]^][#15] 块可以将一个 a header format object 附加到 PDU 上。然后标头的长度将测量有效负载加上 CRC 长度（CRC32 为 4 个字节）。

该块接收 PDU 并创建 header，通常用于 MAC 级处理。每个收到的 PDU 被认为是它自己的  frame，因此任何 fragmentation 要在上游或之前的流程图中处理完毕。

该块的 'header' message port 会输出在该块中创建的 header。标头完全基于对象，该对象是从 header_format_base 类派生的对象。所有这些 packet header format objects 都是相同的：他们接收 payload 数据以及有关 PDU 可能的 metadata 信息。

对于不同的数据包头格式化需求，我们可以定义继承自 header_format_base 块并重载 header_format_base::format 函数的新类。

</br>

因此，运行后输出结果为：

```
***** VERBOSE PDU DEBUG PRINT ******
()
pdu length =          6 bytes
pdu vector contents = 
0000: af 55 00 30 00 30 
************************************
***** VERBOSE PDU DEBUG PRINT ******
()
pdu length =         48 bytes
pdu vector contents = 
0000: 22 e7 d5 20 f8 e9 38 a1 4e 18 8c 47 30 8c fe f5 
0010: ff f7 f7 28 b9 f8 fb f5 1c 7c cc cc 4c 24 01 6b 
0020: 1c ea a3 ca e0 f5 80 a7 cc 09 5c d9 db 73 02 76 
************************************
```


</br>

### 2.4 将 header 和 payload 合并输出

上面三个例子终于合成了一个完整数据帧，接下来我们尝试将其 header 和 payload 部分合并输出：`tx_stage4.grc`

![][p9]

上面例子基于 2.3 中的合成信息，分别对 header 和 payload PDU 转换为 Stream，然后每 1 bit 输出 1bytes 数据（其实就是 bit 0 -> byte 0; bit 1 -> byte 1），接着 Map 其实就是执行 output[i] = map[input[i]]，然后借助 Chunks to Symbols[^[21]^][#21][^[22]^][#22] 将 bytes 转变为复数（采用星座图转换），最后使用 Tagged Steam Mux 将两股输入合并输出。运行后看 time sink 图能看出 header (0xaf 0x55 ... -> 10101111 01010101 ...) 对应：1 -1 1 -1 1 1 1 1 -1 1 ....

**备注：** 该流程图中涉及星座图的知识，可以参考 [[16]][#16] [[17]][#17] [[18]][#18] [[19]][#19] [[20]][#20] [[21]][#21] [[22]][#22]

</br>

### 2.5 对 PDU 实施突发填充和渐变

burst shaper block 用于应用突发填充和斜坡的突发整形器块，通过在每个脉冲的前后添加一些补偿，使得脉冲更加稳定和清晰。它有两种补偿方式：

- 一种是在脉冲的前后添加一些零值，也就是没有信号的空白，这样可以避免脉冲之间的干扰，也可以调节脉冲的间隔。
- 另一种是在脉冲的前后添加一些相位符号，也就是交替的+1/-1的信号，这样可以使得脉冲的上升和下降更加平滑，也可以调节脉冲的形状。

如果使用定相符号，则在每个突发之前和之后将插入长度为ceil（N/2）的+1/-1个符号的交替模式，其中 N 是抽头矢量的长度。斜上/斜下形状将应用于这些相位符号。

如果不使用相位符号，则渐变将直接应用于每个突发的头部和尾部。


burst shaper block 的参数有以下几个：

- 窗口系数（Window Taps）：这是一组用来控制脉冲的上升和下降的系数，它可以用来改变脉冲的波形，例如将方波变为正弦波，或将模拟信号变为数字信号 [^[23]^][#23] [^[24]^][#24]。

- 前补偿长度（Pre-padding Length）：这是在每个脉冲前面添加的零值的个数，它可以用来调节脉冲的间隔，也可以用来避免脉冲之间的干扰。

- 后补偿长度（Post-padding Length）：这是在每个脉冲后面添加的零值的个数，它可以用来调节脉冲的间隔，也可以用来避免脉冲之间的干扰。

- 插入相位符号（Insert Phasing Symbols）：这是一个布尔值，表示是否在每个脉冲的前后添加相位符号，如果为真，那么会在每个脉冲的前后添加交替的+1/-1的信号（ceil(N/2) 用于上翼侧，ceil(N/2) 用于下翼侧，如果 taps.size 为奇数，中间的 tag 将用作上翼侧的最后一个，和下翼侧的第一个），如果为假，那么不会添加相位符号，而是直接对脉冲的头尾进行补偿。

- 长度标签名称（Length Tag Name）：这是用来标记每个脉冲的长度的标签的名称，它可以用来控制脉冲的发送和接收，也可以用来分析脉冲的性能。

burst shaper block 的输出是一个经过整形和补偿的脉冲序列，它的长度标签会更新为包含补偿的长度，而且会放在输出的开头。其他的标签会根据它们的位置，放在相应的输出上，以保持与脉冲的关联。

备注：窗函数（英语：window function）在信号处理中是指一种除在给定区间之外取值均为0的实函数。譬如：在给定区间内为常数而在区间外为0的窗函数被形象地称为矩形窗。任何函数与窗函数之积仍为窗函数，所以相乘的结果就像透过窗口“看”其他函数一样。窗函数在频谱分析、滤波器设计、波束形成、以及音频数据压缩（如在Ogg Vorbis音频格式中）等方面有广泛的应用。[^[23]^][#23] [^[24]^][#24]

一个简单的例子如下：`burst_tagger.grc`

![][p10]

运行后效果如下：

![][p11]

其中 Vector Source 是 8 个 1，8 个 -1，在 Stream to Tagged Stream 中将 160 个采样打包加长度标签（即 10 组向量），然后将数据送到两个配置不同的 Burst shaper 块中（一个使能定向符号，一个不使能，两个都使用海宁窗，N=50）：

- 因此第一个输出的数据为：上翼 25 个1,-1交替信号（作用海宁窗），然后 160 个采样数据，然后 25 个下翼 1,-1交替信号，最后 padding 20 个 0 信号。因此最终数据总长度为：25+160+25+20 = 230

- 因此第二个输出的数据为：海宁窗直接作用 160 个采样数据的前 25 个形成上翼，作用后 25 个形成下翼，中间 110 个不实施作用，最后 padding 20 个 0 信号。因此最终数据总长度为：160+20=180

进一步，我们可以在 2.4 的完整数据帧基础上，加入 burst shaper（前后各填充 10 个 0，采用海宁窗，使能定向符号）-> `tx_stage5.grc`：

![][p12]


</br>

# 参考链接

[[1].维基百科 —— PDU][#1]    
[[2].GNU Radio —— Random PDU Generator][#2]     
[[3].GNU Radio —— PDU Set][#3]   
[[4].GNU Radio —— Async CRC32][#4]   
[[5].GNU Radio —— FEC Async Encoder][#5]   
[[6].GNU Radio —— Repetition Encoder Definition][#6]     
[[7].GNU Radio —— CC Encoder Definition][#7]     
[[8].周武旸 —— 中国科学技术大学 个人通信与扩频实验室《编码论第四章》（超详细介绍卷积编码）][#8]
[[9].知乎 —— 卷积码（有些错误，对于理解 8 有帮助）][#9]     
[[10].国外问答论坛 —— 旅行者号上面如何实现卷积码的提问][#10]  
[[11].美国国防信息安全中心][#11]
[[12].维基百科 —— 卷积码][#12]
[[13].GNU Radio —— CCSDS Encoder Definition][#13]  
[[14].GNU Radio —— Default Header Format Obj][#14]  
[[15].GNU Radio —— Protocol Formatter (Async)][#15]  
[[16].清华大学学报 —— OFDM星座旋转调制自适应交织器设计][#16]  
[[17].知乎 —— 星座图通信原理（相比 18 更多例子和图）][#17]  
[[18].CSDN —— 详解IQ调制以及星座图原理（相比 20 更详细）][#18]  
[[19].中国科技核心期刊 —— 基于星座图的数字信号调制方法综述][#19]  
[[20].CSDN —— 星座图的原理和应用（简单介绍 IQ 调制和星座图）][#20]
[[21].GNU Radio —— Chunks to Symbols][#21]  
[[22].GNU Radio —— Constellation Object][#22]  
[[23].CSDN —— 一文读懂FFT，海宁窗（hann）和汉明窗（hamming）的区别，如何选择窗函数][#23]  
[[24].维基百科 —— 窗函数 Window function][#24]    
[[25].GNU Radio —— Burst Shaper][#25]    



[#1]:https://en.wikipedia.org/wiki/Protocol_data_unit
[#2]:https://wiki.gnuradio.org/index.php?title=Random_PDU_Generator
[#3]:https://wiki.gnuradio.org/index.php/PDU_Set
[#4]:https://wiki.gnuradio.org/index.php?title=Async_CRC32
[#5]:https://wiki.gnuradio.org/index.php?title=Repetition_Encoder_Definition
[#6]:https://wiki.gnuradio.org/index.php?title=Repetition_Encoder_Definition
[#7]:https://wiki.gnuradio.org/index.php/CC_Encoder_Definition
[#8]:http://staff.ustc.edu.cn/~wyzhou/course.htm
[#9]:https://zhuanlan.zhihu.com/p/525899740
[#10]:https://space.stackexchange.com/questions/54054/what-voyager-spacecraft-hardware-performed-transmitted-data-coding-in-such-a-com
[#11]:https://discover.dtic.mil/tr_redirect/
[#12]:https://en.wikipedia.org/wiki/Convolutional_code
[#13]:https://wiki.gnuradio.org/index.php?title=CCSDS_Encoder_Definition
[#14]:https://wiki.gnuradio.org/index.php?title=Default_Header_Format_Obj.
[#15]:https://wiki.gnuradio.org/index.php/Protocol_Formatter_(Async)
[#16]:http://jst.tsinghuajournals.com/article/2014/1000-0054/1000-0054-54-4-458.html
[#17]:https://zhuanlan.zhihu.com/p/594337231
[#18]:https://blog.csdn.net/weixin_44586473/article/details/104066625
[#19]:http://www.c-s-a.org.cn/html/2022/12/8838.html
[#20]:https://blog.csdn.net/qq_39543984/article/details/122585350
[#21]:https://wiki.gnuradio.org/index.php?title=Chunks_to_Symbols
[#22]:https://wiki.gnuradio.org/index.php?title=Constellation_Object
[#23]:https://blog.csdn.net/s09094031/article/details/105744859
[#24]:https://en.wikipedia.org/wiki/Window_function
[#25]:https://wiki.gnuradio.org/index.php?title=Burst_Shaper


[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/72/a3dca86f10f741749115a53bc56214.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=/0c/86aff87219e47050c99884c5a8822d.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=/7a/53eeb9a23d68896ac31420948e71d1.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=/69/6a4c4d685884419a79adcdc9ddea3c.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=/1b/bd7843a2e63f113d3ea0b621b29b6b.png
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=/ec/8e5110af8fe0e92ac8caceac333901.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=/75/53a9f61e945ecd8fb72ffb10518b69.png
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=/82/dddf2fb400db46cf125fbad8626c41.png
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=/b0/536a1f073ce04d5984470b85a9b028.png
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=/de/4ed9776f6d1880f5782024be3425ce.png
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=/e3/a0fb7ee0c8e151dac83d6d0ca29c50.png










