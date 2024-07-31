
## 一、BLE（Bluetooth low energy）协议栈简介

### 1.1 协议栈组成

BLE 协议栈由控制器（Controller）、主机控制接口（HCI）和主机（Host）组成。如下图：


![][p1]


其中：
- 控制器（Controller）
	- 物理层（Physical Layer，PHY），工作在免费的2.4G频段，采用高斯频移键控
	- 链路层（Link Layer，LL），控制设备的射频状态，让设备处于这五种状态之一：
		- Standby：默认状态，不进行收发。
		- Advertising：广播状态，在3个广播信道广播数据包，同时监听和回复扫描者发送的扫描数据包。
		- Scanning：扫描状态，在3个广播信息监听广播数据包，同时发送扫描数据包。
		- nitiating：初始化状态，在广播信道监听广播数据包，从而发起连接。
		- Connection：连接状态。
- 主机控制接口（HCI）：主机控制接口（Host-Controller Interface，HCI）提供了Host与Controller之间的通道。该接口层的实现可以是软件接口，也可以是标准硬件接口，比如UART，SPI或USB。
- 主机（Host）
	- 逻辑链路控制和适配器协议（Logical Link Control and Adaption Protocol，L2CAP）为上层提供了多路复用、数据分段与重组服务，并且支持逻辑端对端的数据通信。
	- 安全管理层（Security Manager，SM）定义了配对和密钥分发的方法，并为其他层提供了与对端设备进行安全连接和数据交换的功能。
	- 通用访问规范层（Generic Access Profile，GAP）是 BLE 协议栈与 Application 和 Profiles 的直接接口。它负责设备发现以及连接相关的各项服务，包括工作模式和访问模式。BLE的工作模式有4种：广播、扫描、周边外设和主设备。访问模式包括设备发现、连接模式、认证和服务发现等。
	- 属性协议层（Attribute Protocol，ATT）使本地设备可以暴露一些数据或属性给对端设备。它区分两种角色：客户机和服务器。客户机和服务器通过逻辑信道通信。
	- 通用属性配置文件层（Generic Attribute Profile，GATT）定义使用ATT的一系列子过程。两个BLE设备之间的数据通信是由这些子过程来处理的。GATT Services和Applications可以直接使用GATT。

</br>

### 1.2 BLE协议栈各层功能机制/体系结构

如上图所述，要实现一个BLE应用，首先需要一个支持BLE射频的芯片，然后还需要提供一个与此芯片配套的BLE协议栈，最后在协议栈上开发自己的应用。可以看出BLE协议栈是连接芯片和应用的桥梁，是实现整个BLE应用的关键。那BLE协议栈具体包含哪些功能呢？简单来说，BLE协议栈主要用来对你的应用数据进行层层封包，以生成一个满足BLE协议的空中数据包，也就是说，把应用数据包裹在一系列的帧头（header）和帧尾（tail）中。具体来说，BLE协议栈主要由如下几部分组成：

PHY层（Physical layer物理层）。PHY层用来指定BLE所用的无线频段，调制解调方式和方法等。PHY层做得好不好，直接决定整个BLE芯片的功耗，灵敏度以及selectivity等射频指标。

LL层（Link Layer链路层）。LL层是整个BLE协议栈的核心，也是BLE协议栈的难点和重点。像Nordic的BLE协议栈能同时支持20个link（连接），就是LL层的功劳。LL层要做的事情非常多，比如具体选择哪个射频通道进行通信，怎么识别空中数据包，具体在哪个时间点把数据包发送出去，怎么保证数据的完整性，ACK如何接收，如何进行重传，以及如何对链路进行管理和控制等等。LL层只负责把数据发出去或者收回来，对数据进行怎样的解析则交给上面的GAP或者ATT。

HCI（Host controller interface）。HCI是可选的，HCI主要用于2颗芯片实现BLE协议栈的场合，用来规范两者之间的通信协议和通信命令等。

GAP层（Generic access profile）。GAP是对LL层payload（有效数据包）如何进行解析的两种方式中的一种，而且是最简单的那一种。GAP简单的对LL payload进行一些规范和定义，因此GAP能实现的功能极其有限。GAP目前主要用来进行广播，扫描和发起连接等。

L2CAP层（Logic link control and adaptation protocol）。L2CAP对LL进行了一次简单封装，LL只关心传输的数据本身，L2CAP就要区分是加密通道还是普通通道，同时还要对连接间隔进行管理。

SMP（Secure manager protocol）。SMP用来管理BLE连接的加密和安全的，如何保证连接的安全性，同时不影响用户的体验，这些都是SMP要考虑的工作。

ATT（Attribute protocol）。简单来说，ATT层用来定义用户命令及命令操作的数据，比如读取某个数据或者写某个数据。BLE协议栈中，开发者接触最多的就是ATT。BLE引入了attribute概念，用来描述一条一条的数据。Attribute除了定义数据，同时定义该数据可以使用的ATT命令，因此这一层被称为ATT层。

GATT（Generic attribute profile ）。GATT用来规范attribute中的数据内容，并运用group（分组）的概念对attribute进行分类管理。没有GATT，BLE协议栈也能跑，但互联互通就会出问题，也正是因为有了GATT和各种各样的应用profile，BLE摆脱了ZigBee等无线协议的兼容性困境，成了出货量最大的2.4G无线通信产品。

</br>

## 二、Hackrf 如何发送 BLE 广播包（数据包合成）

通过阅读 BLE 协议栈发现，只要实现物理层和部分 LL 层，即可发出蓝牙广播包（本文以蓝牙 4.0/4.1/4.2 为例），下面是分步知识点和细节：

### 2.1 物理层

1）信道

![][p5]

我们如果想要发送 BLE 广播数据，只要关注：37、38、39 三个信道，起频率分别为：2400KHz、2426KHz、2480KHz

注：例如流程图中 RTL-SDR Source 默认的频率为 2.426GHz,意味着默认采集 38 信道的数据
注：编码方式采用 GFSK

</br>

### 2.2 数据链路层
#### 2.2.1 角色

在 37、28、39 信道发送信息的叫做 advertiser ; 接收信息的叫做 scanner。

![][p6]

</br>

#### 2.2.2 数据包格式

这有份 BLE 数据链路层超全的格式说明：https://github.com/nbtool/auto_test_tool/blob/master/app/app_sdr_ble_adv_rx/BT.xlsx

我们以 4.0/4.1/4.2 版本为例：

![][p2]

其中广播 PDU 如下：

![][p3]

因此一个广播数据包在 LL 层如下：


AA D6 BE 89 8E （preamble + access address)
42 26 06 05 04 03 02 01  (PDU-Header + PDU-Payload-Adva)
19 09 53 44 52 2F 42 6C 75 65 74 6F 6F 74 68 2F 4C 6F 77 2F 45 6E 65 72 67 79 (PDU-Payload-AdvData)
E8 7D 36 (CRC)

注意：PDU-Header 要倒着看：

```
0x42 0x26 --> 0x2642 -> 0010 0110 0100 0010 
                     ->                0010 PDU-Type（ADV_NONCONN_IND）  	
					 ->           ..00 RFU 保留
					 ->           .1.. TxAdd
					 ->           0... RxAdd
					 -> ..10 0110 Length(这个是 PDU Payload 长度)
					 -> 00.. RFU
```

被 nrf-connect APP扫描到的效果如下：

![][p4]

</br>

### 2.3 加密相关

这里有个至关重要的流程，需要看蓝牙协议栈 《[CoreSpecification_v5.0.pdf][#3]》：

![][p7]

#### 2.3.1 Cyclic Redundancy Check(循环冗余检查)



循环冗余校验作用于数据链路层 **PDU 部分**

If the PDU is encrypted, the CRC is calculated after encryption.

这里的 CRC 多项式是一个 24 bit 多项式：`x^24+x^10+x^9+x^6+x^4+x^3+x^1+x^0` 其物理上对应一个线性反馈移位寄存器 (LFSR) with XOR taps at bit 0, 1, 3, 4, 6, 9, 10, and 24.

数据从最低有效位开始移位到移位寄存器。移位寄存器用已知的共享值或 0x555555 进行初始化。

![][p8]

线性反馈移位寄存器中的CRC编码示例，预设为0x555555（10101010101010101010）—— Animation by Mark Hughes

当接收到数据包时，在CRC之后检查访问地址。如果其中一个不正确，则数据包将被拒绝，并停止处理。

</br>

#### 2.3.2 Data Whitening

数据白化防止重复位（00000000或11111111）的长序列。它被应用于发射机的 CRC 之后的链路层的 **PDU 和 CRC** 字段。在接收器中的 CRC 之前执行去白化。白化器和去白化器都使用在比特 4 和比特 7 处具有抽头的7比特线性反馈移位寄存器（LFSR）。

The shift register is initialized with a sequence that is derived from the channel index：

- 位置 0 设置为 1
- 位置 1 到 6 被设置成 the channel index of the channel used when transmitting or receiving, with the MSB in position 1 and the LSB in position 6

Bits are shifted along the shift register from 0→1, 1→2, 2→3, 4→5, 5→6, 6→0. Bit 3 and bit 6 are processed with the XOR ⊕ operator to determine bit 4 (0⊕0=0,0⊕1=1,1⊕0=1,1⊕1=0)

![][p9]

图示用通道26 = 0x1A (1011010)初始化的数据白化线性反馈移位寄存器内部的逻辑图像 —— **Animation by Mark Hughes**

**1011010**
https://www.allaboutcircuits.com/uploads/articles/CoreSpecification_v5.0.pdf  [3.2 DATA WHITENING]
通道 26 = 00[<font color=#FF000>**0**</font>1 101<font color=#000FF>**0**</font>]
position0 = 1(固定的）
position 1 = <font color=#FF000>**0**</font>(通道的最高有效位MSB）
position 2 = 1
position 3 = 1
position 4 = 0
position 5 = 1
position 6 = <font color=#000FF>**0**</font>（通道最低有效位LSB）

第一次移位寄存器为：
1011 010 （取position6 和 position3 进行异或得到下次的 position 4数据）
0101 101
1010 010
0101 001
...

</br>

**算法实现：**

- 1）channel bit 左右反转，右数第二位置1 （00[<font color=#FF000>**0**</font>1 101<font color=#000FF>**0**</font>] -> [<font color=#FF000>**0**</font>1011<font color=#000FF>**0**</font>]10）形成 lfsr
- 2）对于每一字节的输入，bits 左右反转成 d，循环 8 次：
	- 从左往右取出 lfsr 和 d 的每一 bit，亦或运算赋值给 d 的对应 bit
	- <font color=#FF000> 取position6 和 position3 进行异或得到下次的 position 4数据 </font>
	- <font color=#FF000> 注：下面代码里用了比较巧妙的方式，做到了上面两点） </font>

</br>

**PYTHON 代码为：**

```python
# Swap bits of a 8-bit value
# ➜  sdr4iot-ble-rx git:(master) ✗ python test_swap.py 
# 0b11010101
# 0b10101011
def swap_bits(value):
    return (value * 0x0202020202 & 0x010884422010) % 1023

# (De)Whiten data based on BLE channel
def dewhitening(data, channel):
    ret = []
    lfsr = swap_bits(channel) | 2

    for d in data:
        d = swap_bits(ord(d[:1]))
        for i in 128, 64, 32, 16, 8, 4, 2, 1:
            if lfsr & 0x80:
                lfsr ^= 0x11
                d ^= i

            lfsr <<= 1
            i >>= 1
        ret.append(swap_bits(d))

    return ret
```

**测试代码：**

```python
for xx in self.gr_buffer[pos:pos + BLE_PDU_HDR_LEN]:
    print(hex(ord(xx)),end=' ')
print('<--PRE (%d)', self.current_ble_chan)

ble_header = dewhitening(
   self.gr_buffer[pos:pos + BLE_PDU_HDR_LEN], self.current_ble_chan)
            
for xx in ble_header:
    print(hex(xx),end=' ')
print('<--AFTER')
```

**输入输出：**

```bash
0xcd 0xf7 <--PRE (%d) 37
0x40 0x25 <--AFTER
0xcd 0xf7 <--PRE (%d) 37
0x40 0x25 <--AFTER
0x3a 0x79 <--PRE (%d) 37
0xb7 0xab <--AFTER
0x93 0xf7 <--PRE (%d) 37
0x1e 0x25 <--AFTER
0x85 0x9f <--PRE (%d) 37
0x8 0x4d <--AFTER
0x60 0x15 <--PRE (%d) 37
0xed 0xc7 <--AFTER
0x6b 0xdf <--PRE (%d) 37
0xe6 0xd <--AFTER
0xea 0x95 <--PRE (%d) 37
0x67 0x47 <--AFTER
0xaa 0x6d <--PRE (%d) 37
0x27 0xbf <--AFTER
0xaa 0x86 <--PRE (%d) 37
0x27 0x54 <--AFTER
0xdb 0xb3 <--PRE (%d) 37
0x56 0x61 <--AFTER
0xd5 0x96 <--PRE (%d) 37
0x58 0x44 <--AFTER
0xa3 0xf4 <--PRE (%d) 37
0x2e 0x26 <--AFTER
0xcd 0xf8 <--PRE (%d) 37
```

</br>

### 2.4 合成 LL 数据包总结

综上，整个组包逻辑就比较简单了：（这里有特别要注意的是 CRC 覆盖的范围、白化覆盖的范围、PDU-Header 部分的大小端）

```python
def create_ll_payload(mac, adv_data, channel):
    '''
    AA D6 BE 89 8E （preamble + access address)
    42 26 06 05 04 03 02 01  (PDU-Header + PDU-Payload-Adva)
    19 09 53 44 52 2F 42 6C 75 65 74 6F 6F 74 68 2F 4C 6F 77 2F 45 6E 65 72 67 79 (PDU-Payload-AdvData)
    E8 7D 36 (CRC)
    '''

    ll_payload = [0xAA,0xD6,0xBE,0x89,0x8E] #  preamble + access address
                                            #  PDU-Header        
    '''                                     
    0x42 0x26 --> 0x2642 -> 0010 0110 0100 0010
                         ->                0010 PDU-Type（ADV_NONCONN_IND）
                         ->           ..00 RFU 保留
                         ->           .1.. TxAdd
                         ->           0... RxAdd
                         -> ..10 0110 Length(这个是 PDU Payload 长度)
                         -> 00.. RFU
    '''
    # 组装广播 PDU
    pdu_adv = []
    pdu_adv.extend([0x42, (len(adv_data)+6) & 0xFF])    # PDU-Header
    pdu_adv.extend(reversed(mac))                       # PDU-Payload-Adva(实际 MAC 的的反转)
    pdu_adv.extend(adv_data)                            # PDU-Payload-AdvData

    # 生成 CRC(基于PDU)
    crc = bsp_algorithm.bt_crc(pdu_adv, len(pdu_adv))    # CRC 只对 PDU 进行
    
    # 加白(基于PDU+CRC)
    pdu_adv_crc = pdu_adv + crc
    pdu_adv_crc_wt = bsp_algorithm.bt_dewhitening(pdu_adv_crc,channel)

    # 最终组装
    ll_payload.extend(pdu_adv_crc_wt)

    # 打印
    bsp_string.print_data_list_hex("> pre_wt_adv_pdu:", pdu_adv)
    bsp_string.print_data_list_hex("\n> ll data final:", ll_payload)


    return ll_payload

# 示例输入
mac = [1,2,3,4,5,6]
adv_name = "btfz's gnu-radio course"
adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
channel = 37
ll_datas = create_ll_payload(mac, adv_datas, channel)
```

</br>

## 三、Hackrf 如何发送 BLE 广播包（采样、调制、SDR 相关）

第二节我们已经能够组成 BLE 广播数据包了，本节我们将介绍如何将其进行采样、调制、利用 SDR 发射出去。

1）将数据包按照小端模式 1 字节变 8 bit：ll_datas_bit = bsp_string.bytes_to_bits_lsb(ll_datas)
2）构建 sample_per_symbol = 4 的采样数据：采样数据是在 ll_datas_bit 前后各插入 15 个 0，中间的 ll_datas_bit 每 bit 后面跟 3 个 0，同时 ll_datas_bit 每 bit 的 0 变 -1
3）对采样数据实施高斯滤波
4）对高斯滤波后的数据实时 FSK-IQ 调制

看代码一下就明白了：

```python
def gen_sample_from_phy_bit(bit):
    # Constants
    MAX_NUM_PHY_BYTE = 47
    SAMPLE_PER_SYMBOL = 4
    LEN_GAUSS_FILTER = 4
    MAX_NUM_PHY_SAMPLE = ((MAX_NUM_PHY_BYTE*8*SAMPLE_PER_SYMBOL)+(LEN_GAUSS_FILTER*SAMPLE_PER_SYMBOL)) 


    # 1、tmp_phy_bit_over_sampling 是前塞 15 个0，中间对每 bit 数据后面插入 3 个0，同时对于原来数据是 0 的变为 -1，为 1 的变为 1
    num_bit = len(bit)
    tmp_phy_bit_over_sampling = [0]*((num_bit * SAMPLE_PER_SYMBOL) + 2*LEN_GAUSS_FILTER*SAMPLE_PER_SYMBOL);

    for i in range(num_bit * SAMPLE_PER_SYMBOL):
        if i % SAMPLE_PER_SYMBOL == 0:
            tmp_phy_bit_over_sampling[i + LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 1] = (bit[i // SAMPLE_PER_SYMBOL]) * 2 - 1
        else:
            tmp_phy_bit_over_sampling[i + LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 1] = 0

    # bsp_string.print_data_list_hex("> tmp_phy_bit_over_sampling is:", tmp_phy_bit_over_sampling)

    # 2、sample 是高斯滤波器 + IQ 调制（数据量是
    num_sample = (num_bit * SAMPLE_PER_SYMBOL) + (LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL)
    sample = [0,0] * num_sample  # 初始化 sample 列表
    cos_table_int8, sin_table_int8 = bsp_signal.sample_cosine_and_sine()
    gauss_coef_int8 = [0, 0, 0, 0, 2, 11, 32, 53, 60, 53, 32, 11, 2, 0, 0, 0]

    tmp = 0
    sample[0] = cos_table_int8[tmp]
    sample[1] = sin_table_int8[tmp]

    for i in range(num_sample - 1):
        acc = 0
        for j in range(3, LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 4):
            acc += gauss_coef_int8[LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - j - 1] * tmp_phy_bit_over_sampling[i + j]

        tmp = (tmp + acc) & 1023
        sample[(i + 1) * 2] = cos_table_int8[tmp]
        sample[(i + 1) * 2 + 1] = sin_table_int8[tmp]

    return sample
```

</br>

注：**这里浅介绍下 IQ 调制**：

进行高频传输需要调制频率为 f0 的高频载波（carrier），模拟传输最常见的调制是：调幅（AM）、调相（PM）和调频（FM）。

对于模拟AM，调制信号 m（t）是载波c（t）和基带信号a（t）的数学乘积。相应的硬件是混频器，其体系结构和数学表示是乘法器。

$$
m(t)=a(t)c(t)=a(t)cos(2\pi f_0t)，周期 f_0，频率 F0 = 1/f_0
$$

我们称 a(t) 为基带信号是因为它的频谱（spectrum）在低频范围（例如：HiFi 音频信号为 \[0-20kHz]）

对于常见数字调制：
调制 | 表达式 
---|---
FSK | $$$s(t)=Acos(2\pi F_mt+ϕ)$$$ | ![][p10]
ASK | $$$s(t)=A_mcos(2\pi Ft+ϕ)$$$ | ![][p11]
PSK | $$$s(t)=Acos(2\pi Ft+ϕ_m)$$$ | ![][p12]

</br>

将 PSK 和 ASK 公式结合，并利用 $$$cos(α+β) = cosα*cosβ-sinα*sinβ$$$ 对其进行展开：

![][p14]

表示在坐标系中为：

![][p15]

因此：相位调制实质是选择多组不同的相位，幅度调制实质是选择不同的半径，无论是不同的相位还是不同的半径集合，在坐标系中都是一些点集（我们常使用星座图来观察他们），下面是几个常见调制的星座图：

![][p13]

可以看出：

BPSK：使用 0，π 度两个相位
QPSK：使用 π/4 , π3/4, π5/4, π7/4 四个相位
16QAM：使用了 16 个点
...

</br>

对于 FSK 有点特殊，我们假设是 FSK 调制（有 F0 和 F1 两种频率（$$$F_c=(F_0+F_1)/2$$$））：

$$
s(t)= \begin{cases}
cos(2\pi F_0t) & bit = 0 \\
cos(2\pi F_1t) & bit = 1 \\
\end{cases}
$$

当该信号过 IQ 接收器时（下面是 IQ 接收器示意图）：

![][p16]

上路（I路）：

$$
cos(2\pi F_0t)*cos(2\pi F_ct) = 1/2*[cos(2\pi (F_0-F_c)t)+cos(2\pi (F_0+F_c)t)] \\
cos(2\pi F_1t)*cos(2\pi F_ct) = 1/2*[cos(2\pi (F_1-F_c)t)+cos(2\pi (F_1+F_c)t)]
$$

经过 LPF 低通滤波后 $$$cos(2\pi (F_0+F_c)t)$$$ 和 $$$cos(2\pi (F_1+F_c)t)$$$ 将会被滤除，I 路收到的信号 yI(t) 为：

$$
y_I(t)= \begin{cases}
1/2*cos(2\pi (F_0-F_c)t) & bit = 0\\
1/2*cos(2\pi (F_1-F_c)t) & bit = 1\\
\end{cases}
$$

这里我们定义：$$$F_{b1} = F_1-F_c$$$ AND $$$F_{b0} = F_0-F_c$$$
根据 $$$F_1、F_0、F_c$$$ 的定义，可知：$$$F_{b1}=-F_{b0}$$$

同样的 Q 路的也能算出来：

$$
y_Q(t) = 
\begin{cases}
     \dfrac{1}{2} cos(2 \pi (F_1-F_c) t) =  \dfrac{1}{2} cos(2 \pi (F_{b1}-\dfrac{\pi}{2}) t) = \dfrac{1}{2} sin( 2\pi F_{b1} t) & \text{for bit 1} \\
     \dfrac{1}{2} cos(2 \pi (F_0-F_c) t)=  \dfrac{1}{2} cos(2 \pi (F_{b0}-\dfrac{\pi}{2}) t) = \dfrac{1}{2} sin( 2\pi F_{b0} t) & \text{for bit 0}
\end{cases}
$$

现在如果我们定义最终的信号为：$$$y_1(t) = y_{I1}(t)+jy_{Q1}(t) = e^{j 2\pi F_{b1} t}$$$，这样因为我们的信号是复数信号，我们能在频域区分出 $$$F_{b0}$$$ 和 $$$F_{b1}$$$，正是如此，我们也能设计所需要的滤波器和检测器。


</br>


[[1].「应用笔记」BLE 低功耗蓝牙技术｜协议栈简介][#1]
[[2]. SDR 教程实战 —— 利用 GNU Radio + HackRF 手把手深入了解蓝牙协议栈（从电磁波 -> 01数据流 -> 蓝牙数据包）][#2]
[[3]. 蓝牙之BLE学习小结][#6]
[[4]. 蓝牙BLE的CRC24校验代码C语言][#5]
[[5]. CRC（循环冗余校验）在线计算][#4]
[[6]. Custom IQ - FSK 常见无线通信的调制方式对比][#7]
[[7]. 维基百科 IQ 调制][#8]
[[8]. BOOK —— I/Q 信号 101：既不复杂也不复杂(详细)][#9]
[[9]. 论坛 —— FSK Modulation using I/Q(详细+GOOD)][#10]
[[10]. 论坛 —— FSK and IQ modulation(细)][#11]
[[11]. GnuRadio —— IQ Complex 教程][#12]
[[12]. CSDN —— Markdown编辑分段函数][#13]



[#1]:https://baijiahao.baidu.com/s?id=1757801963196042080&wfr=spider&for=pc
[#2]:https://www.cnblogs.com/zjutlitao/p/17698384.html
[#3]:https://www.allaboutcircuits.com/uploads/articles/CoreSpecification_v5.0.pdf
[#4]:http://www.ip33.com/crc.html
[#5]:https://blog.csdn.net/weixin_38366885/article/details/134547545
[#6]:https://blog.csdn.net/bai_tao/article/details/106873015
[#7]:https://helpfiles.keysight.com/csg/n7608/Content/Main/Custom_IQ_FSK.htm
[#8]:https://en.wikipedia.org/wiki/In-phase_and_quadrature_components
[#9]:https://wirelesspi.com/i-q-signals-101-neither-complex-nor-complicated/
[#10]:https://electronics.stackexchange.com/questions/653434/fsk-modulation-using-i-q
[#11]:https://dsp.stackexchange.com/questions/34023/fsk-and-iq-modulation
[#12]:https://wiki.gnuradio.org/index.php/IQ_Complex_Tutorial
[#13]:https://blog.csdn.net/zhengjihao/article/details/77799816


[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/8b/64bcbbcf224373ec86324f47dc1b85.png
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=/9a/8a09c70e8a837624d30281d310ad8a.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=/7e/8b63ee7e076a3713b23d1d5527ab76.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=/20/d2e176f45b354a62208c6a94721ac1.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=/f5/28763c8adb941c1ec7a2ba8d6c515e.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=/70/2f71edbafeb8aeb96a68344ecde27d.png
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=/ca/0b49e91b7ade9ac5da6231650f5b66.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=/1b/7fbeaa2f297723726b1a6fd82d43a3.gif
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=/6d/db028629dcd96613a0d80a13ce781f.gif
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=/df/177aa31e6f6f879880f9a3adf8894c.png
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=/77/c410d3225151758317b2c73f5c1df6.png
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=/4b/1c92e5eb84427f71e24c061818c661.png
[p13]:https://tuchuang.beautifulzzzz.com:3000/?path=/48/15cfe7cfdd4cd179f09838d0feb2d0.png
[p14]:https://tuchuang.beautifulzzzz.com:3000/?path=/01/5b48a910e8213714ecf117361fb9d9.png
[p15]:https://tuchuang.beautifulzzzz.com:3000/?path=/2c/cc63027ee0734013ead4670e6a69d1.png
[p16]:https://tuchuang.beautifulzzzz.com:3000/?path=/9e/fb6c8a175950d2d38301271ad6810b.png
