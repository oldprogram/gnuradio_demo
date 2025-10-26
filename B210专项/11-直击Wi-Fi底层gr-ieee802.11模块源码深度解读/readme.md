## 一、背景知识

关于802.11协议，以下是详细的介绍，包括其主流版本、特点、年份以及其基本架构。

### 1.1 主流版本、特点和年份

**IEEE 802.11** 协议是 **WLAN（无线局域网）** 的技术标准，我们通常称之为 **Wi-Fi**。它定义了无线通信的物理层（PHY）和数据链路层的 MAC 子层，旨在提供一个类似于以太网的无线连接。

以下是几个主要的 802.11 协议版本，以及它们的发布年份和关键特性：

| Wi-Fi代号 | 802.11协议 | 发布年份 | 主要频段 | 理论最大速率 | 关键技术和特点 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wi-Fi 1** | **802.11b** | 1999 | 2.4 GHz | 11 Mbps | 早期普及的标准，工作在 2.4 GHz，容易受干扰，但兼容性好。 |
| **Wi-Fi 2** | **802.11a** | 1999 | 5 GHz | 54 Mbps | 与 802.11b 同期发布，工作在 5 GHz，干扰较少，但传输距离相对较短。 |
| **Wi-Fi 3** | **[802.11g][#4]** | 2003 | 2.4 GHz | 54 Mbps | 结合了802.11a的速度和802.11b的2.4 GHz频段，实现了向后兼容性。 |
| **Wi-Fi 4** | **802.11n** | 2009 | 2.4 GHz, 5 GHz | 600 Mbps | 引入 **MIMO**（多输入多输出）和 **信道绑定** 技术，显著提高了传输速率和距离。 |
| **Wi-Fi 5** | **802.11ac** | 2013 | 5 GHz | 6.9 Gbps | 主要工作在 5 GHz 频段，引入了 **MU-MIMO**（多用户MIMO）和更宽的信道带宽，大幅提升了多设备连接时的性能。 |
| **Wi-Fi 6** | **802.11ax** | 2019 | 2.4 GHz, 5 GHz | 9.6 Gbps | 专为高密度场景设计，通过 **OFDMA**（正交频分多址）技术，允许多个设备同时传输，提高了网络效率和容量。 |
| **Wi-Fi 6E** | **802.11ax** | 2020 | 2.4 GHz, 5 GHz, **6 GHz** | 9.6 Gbps | 在 Wi-Fi 6 的基础上扩展了 6 GHz 新频段，提供了更宽的信道和更少的干扰，但需要特定硬件支持。 |
| **Wi-Fi 7** | **802.11be** | 2024 | 2.4 GHz, 5 GHz, 6 GHz | 46 Gbps | 引入了 **320 MHz超宽信道**、**多链路操作（MLO）** 等技术，旨在实现更高的吞吐量、更低的时延和更好的可靠性。 |

</br>

### 1.2 802.11协议的架构

802.11 协议是根据 **OSI模型（开放系统互连模型）** 设计的，它主要定义了模型中的最底层——**物理层（PHY）** 和第二层——**数据链路层** 的 **MAC（媒体访问控制）** 子层。

* **物理层 (PHY)**：
    物理层是负责数据在无线信道上传输的“硬件”部分。它定义了如何使用射频信号（无线电波）来传输数据。这包括：
    * **调制和编码**：将数字数据转换成适合无线传输的模拟信号。
    * **频率和信道**：决定了无线网络使用的频段（如 2.4 GHz、5 GHz）和信道划分。
    * **传输速率**：决定了数据传输的最高速度。
    * **天线技术**：如 MIMO、波束成形等，这些技术在物理层上显著提升了网络的性能和覆盖范围。
    
* **MAC 子层 (媒体访问控制)**：
    MAC 子层是数据链路层的一部分，它负责控制和管理物理层，确保多个设备可以共享同一个无线信道而不会发生冲突。它的主要职责包括：
    * **帧格式**：定义了无线数据包（帧）的结构，包括地址、控制信息等。
    * **信道访问机制**：802.11 使用 **CSMA/CA（载波侦听多路访问/冲突避免）** 机制。这与有线以太网的 CSMA/CD 不同，因为它无法有效检测冲突，所以采用“避免”冲突的策略，例如发送数据前先进行侦听，并在需要时使用 **RTS/CTS（请求发送/允许发送）** 机制来预约信道。
    * **安全性**：负责处理加密和认证，确保无线通信的安全性。
    * **功率管理**：定义了设备如何进入省电模式以节省电量。

总的来说，802.11 协议的架构就像一个“**翻译官**”。MAC 子层处理逻辑上的通信规则（例如，谁能说话，怎么说话），而物理层则负责将这些“话语”真正转换成可以通过空气传播的无线电信号，并在接收端进行反向转换。

![][p1]

</br>

## [二、gr-ieee802-11 研究][#2]
### 2.1 环境准备

和之前一样，我们用 [B210 的 docker 开发环境][#6]：

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

然后参考 [github 上的 readme][#2] 依次编译安装 gr-foo 和 gr-ieee802-11（这俩仓库当前时间默认拉下来就是 maint-3.10，和我们 docker 中的 gnuradio 是一个版本，因此不用再切换）。

然后调大共享内存：`sudo sysctl -w kernel.shmmax=2147483648`

最后进入 gr-ieee802-11/examples 下，运行 `gnuradio-companion wifi_phy_hier.grc` 打开 `wifi_phy_hier.grc`，然后点击 RUN->Generate 将子模块安装到用户空间。

最后关闭刚才打开的 gnuradio，然后重新启动 gnuradio 就能够选择 examples 下的其他非子模块的 demo 了：

```
➜  examples git:(maint-3.10) ls
CMakeLists.txt     wifi_phy_hier.grc  wifi_transceiver.grc
wifi_loopback.grc  wifi_rx.grc        wifi_tx.grc
```

**PS：** 为了防止每次打开容器后都要重复上面操作，可以仿照《[10-超强雷达工具包gr-radar详解][#7]》的 1.1 的 PS 部分（在宿主机中打开新终端）：

```
docker ps     # 获取当前运行容器的 ID                                  
docker commit CONTAINER_ID ubuntu:gnuradio-ieee802-11
docker image list 
```

之后启动 docker 直接将 `ubuntu:gnuradio-310` 替换为 `gnuradio-ieee802-11` 即可继续当前的环境。

</br>

### 2.2 流程图解析
#### 2.2.1 wifi_loopback.grc

`wifi_loopback.grc` 首先可以用来验证下我们上面的环境是否设置好，如果没问题，该流程图能正常运行，并且会在终端中输出 log。

![][p2]

因为 WiFi PHY Hier 模块集成度较高，因此整个收发 loopback 的流程图非常简洁，演示了 MAC 层 + 物理层的数据收发，用户可以通过模拟调节信噪比等参数观看对传输的影响，同时可以选择不同的调制和编码技术来看看对传输的影响：

![][p3]

</br>

#### 2.2.2 wifi_transceiver.grc

这个和上面很像，只是采用实际的 B210 设备自收发：

![][p4] 

</br>

### 2.3 核心子块解析
#### 2.3.1 发

在 `wifi_phy_hier.grc` 中 wifi 物理层发送流程图如下：

![][p6]

主要涉及两部分：一部分是 OFDM 前的数据合成，一部分是标准 OFDM 三件套。下面我们针对这两部分进行详细介绍：

**1）数据合成部分详解**

这里有两个块是 OOT (gr-ieee802-11) 实现的（`WiFi Mapper`，`Chunks to Symbols`），我们得先分析下这两个，然后整体就比较好理解了：

**a. WiFi Mapper**

阅读 OOT 代码来了解某一个模块，一般只要看两个文件：

- `ieee802_11_mac.block.yml` 块描述文件
- `mapper_impl.cc` 块的功能实现文件

下面是 `ieee802_11_mac.block.yml` 的代码：

```
id: ieee802_11_mapper
label: WiFi Mapper           # 名字
category: '[IEEE802.11]'     # 分类 

parameters:                  # 参数（2 个）
-   id: encoding             # 1）编码方式
    label: Encoding
    dtype: raw
    default: ieee802_11.BPSK_1_2
-   id: debug                # 2）是否开启 Debug
    label: Debug
    dtype: bool
    default: 'False'
    options: ['True', 'False']
    option_labels: [Enable, Disable]

inputs:                     # 输入，message 类的信息
-   domain: message
    id: in

outputs:                    # 输出，字节流
-   domain: stream
    dtype: byte
    multiplicity: '1'

templates:                  # 与功能函数关联（make 函数和回调函数）
    imports: import ieee802_11
    make: ieee802_11.mapper(${encoding}, ${debug})
    callbacks:
    - set_encoding(${encoding})

file_format: 1
```
</br>

**模块概述**

-----

这个 `mapper_impl` 类是 GNU Radio 的 **`gr::block`** 的一个派生类，它充当一个 **消息驱动（message-driven）** 的流块。

  * **输入：** 通过 **消息端口** 接收 IEEE 802.11 **PSDU**（MAC 层数据包）。
  * **输出：** 通过 **流端口** 输出 **符号数据**（每个输出 `char` 代表一个调制符号，即一个子载波上的复数星座点）。

它的核心功能是实现 **IEEE 802.11 OFDM PHY** 的数据字段（DATA field）处理链，包括：

1.  添加服务字段和填充位 (`generate_bits`)。
2.  扰码 (`scramble`)。
3.  添加尾部零位 (`reset_tail_bits`)。
4.  卷积编码 (`convolutional_encoding`)。
5.  打孔 (`puncturing`)。
6.  交织 (`interleave`)。
7.  符号映射（将编码比特映射到星座点，这里用 `split_symbols` 完成）。

-----

详情见附录一

</br>

**b. Chunks to Symbols**

也是个 OOT，主要将 bit 映射为 Symbols，代码比较简单。

**整体下来就是**：Pad Source 输入经过 WiFi Mapper（填充服务字段->扰码->加尾零位->卷积->打孔->交织->符号映射），之后分两路：一路生成头部信息，然后实施 BPSK 编码；另一路根据编码方式（BPSK/QPSK...) 实施编码。
 
</br>

**2）OFDM 部分详解**

OFDM 三大件（之前有教程详细介绍过）：

- [[29]. GNU Radio 系列教程（二九）—— OFDM 正交频分复用收发 DEMO 演示][#8]     
- [[30]. GNU Radio 系列教程（三十）—— OFDM TX 详解][#9] [<i class="fas fa-file-alt"></i>][#10]      

**a. OFDM Carrier Allocator**

OFDM 频率分配参数总结：

| 参数名称 (Parameter) | 描述 (Description) | 详细信息 (Details) |
| :--- | :--- | :--- |
| **Occupied Carriers (占用载波)** | 用于传输数据的载波（包括数据~~和导频~~）的索引集合。 | **载波索引:** `[-26, -21) + [-20, -7) + [-6, 0) + [1, 7) + [8, 21) + [22, 27)` |
| **Pilot Carriers (导频载波)** | 用于信道估计和同步的载波的索引。 | **载波索引:** `(-21, -7, 7, 21)` |
| **Pilot Symbols (导频符号)** | 导频载波上使用的符号值序列。 | **结构:** 一个包含 117 个元组的列表。每个元组有 4 个元素，对应 4 个导频载波上的符号值。符号值为 $\pm 1$。 |
| **Sync Words (同步字)** | 用于同步和/或信道估计的特殊符号序列。 | **结构:** 一个包含4个同步字的元组。 |
| | | **Sync Word 1 & 2:** 包含复数值 $(\pm 1.47\dots \pm 1.47\dots j)$ 和 $0.0$。主要能量集中在少数几个载波上，其余为 $0.0$。 |
| | | **Sync Word 3:** 包含实部和虚部为 $\pm 1$ 或 $0$ 的复数值。 |
| | | **Sync Word 4:** 包含实部为 $\pm 1$ 或 $0$ 的实数值（虚部为 $0$）。 |
| **Length tag key** | 用于标记数据包长度的键。 | `"packet_len"` |
| **Shift Output** | 是否对输出进行频移操作。 | **Yes** (是) |

**额外观察:**
* **DC 载波 (索引 0):** 在占用载波列表中被跳过（即 $0$ 载波未被占用），通常作为保护或设为 $0$。
* **对称性:** 载波分配大致以 $0$ 载波为中心对称。
* **总载波范围:** 
    * **占用数据载波数量（Occupied Carriers）**：
        * $(-26, -21)$：6个
        * $(-20, -7)$：14个
        * $(-6, 0)$：6个
        * $(1, 7)$：6个
        * $(8, 21)$：14个
        * $(22, 27)$：6个
        * **数据载波总数:** $6 + 14 + 6 + 6 + 14 + 6 = 52$ 个。
    * **导频载波数量 (Pilot Carriers)**: 4个。
    * **总占用载波数量 (数据 + 导频)**: $52 + 4 = 56$ 个。
 
</br>

**b. FFT**

该模块是一个 IFFT 运算器，具有 $64$ 个点的尺寸，用于将 $64$ 个子载波上的复数频率数据（已进行中心化频移）转换成时域信号，并应用了均匀的幅度缩放因子 $1/\sqrt{52}$。

</br>

**c. OFDM Cyclic Prefixer (循环前缀添加器)**

这个模块在 OFDM 发射链路中紧接在 IFFT（逆快速傅里叶变换）之后，它的主要作用是在每个时域的 OFDM 符号前添加一个循环前缀 (Cyclic Prefix, CP)，这是 OFDM 技术中用于抵抗多径衰落的关键步骤。

这个模块配置了一个标准的 OFDM 符号结构：一个长度为 64 的有效符号，带有 16 个采样点的循环前缀，使其总长度为 80 个采样点。它用于发射机的 OFDM 时域符号处理阶段。

</br>

#### 2.3.2 MAC+PHY 包分析

PLCP 会在 MPDU 上附加物理层专用的前导码和报头字段，这些字段包含物理层发送器和接收器所需的信息。802.11 标准将这种组合帧（带有额外 PLCP 前导码和报头的 MPDU）称为 PLCP 协议数据单元（PPDU）。MPDU 也被称为 PLCP 服务数据单元（PSDU），在涉及物理层操作时，通常会使用这一名称。

我们的 gr-ieee802.11 使用的是 ERP-OFDM PPDU (802.11a/g)，其包格式为：<sup>[5][#11]</sup>

![][p8]

> DSSS（直接序列扩频）技术；ERP-OFDM（扩展速率物理层 - 正交频分复用）技术

- 其中 **PLCP Preamble** 是巧妙的放在 OFDM 同步字字段；
- 其中 **Sigbal** 字段是通过 Packet Header Generator 形成的（`ieee802_11.signal_field().formatter()`)，这里用到了 OOT 的 `signal_field_impl.cc`。
    - `signal_field()` 构造函数直接创建了一个 `packet_header_default(48, "packet_len"){}`，长度 48 字节的默认包头
    - `header_formatter` 初始化 ofdm 和 frame，然后调用 `generate_signal_field((char*)out, frame, ofdm)`
    - `generate_signal_field` 中就是按照 PLCP-Header 方式进行组包，然后卷积编码和交织

![][p9]   

- 其中 **Data** 部分来源于 Message Storbe -> WiFi MAC -> WiFi Mapper：
    - Message Storbe 用来定时发送一个 PDU
    - WiFi MAC 是基于 `mac.cc`，看 `app_in`，从 `PDU` 从获取 `msg_len` 和 `msdu`，然后调用 `generate_mac_data_frame(msdu, msg_len, &psdu_length)` 来生成 MAC 帧 <sup>[6][#12]</sup>，最后向 "phy out" 发出 key 为 "crc_included", value 为 `pmt::make_blob(d_psdu, psdu_length)`：    
     ![][p10]
    - 最后送到 WiFi Mapper 进行处理（我们上面已经介绍过了）

</br>

#### 2.3.3 收

**1）短训练序列同步**

**IEEE 802.11 Wi-Fi 接收机**流程图（或信号处理图）的**前导同步部分**。目的是对接收到的 Wi-Fi 信号进行**采样、处理和初步的同步**，以便后续进行解调和解码。

这里涉及一个核心的原理 <sup>[10][#15]</sup>：**自相关（Autocorrelation）计算（用于短训练序列同步）**：Wi-Fi 短训练序列（Short Training Sequence, STS）的特点是每隔 16 个采样点具有重复性。这种重复性通常用于粗略定时同步。

![][p7]

**a. 上半路：**    
1）延迟 16 计算共轭信号得到：$\text{conj}(x[n-16])$    
2）将原始信号与延迟 16 的共轭信号相乘：$C[n] = x[n] \cdot \text{conj}(x[n-16])$    
3）对乘积项进行长度为 48 的滑动平均（窗口求和）。这通常是为了平滑自相关结果并增加信噪比：$C_{MA}[n]$    
4）计算平滑后的自相关结果的幅度：$|C_{MA}[n]|$     

**b. 下半路：**    
1）对于输入信号，计算幅度平方（Complex to Mag$^2$）得到： $|x|^2$    
2）对信号功率（幅度平方）进行长度为 64 的滑动平均。这得到的是信号在某个窗口内的能量（或平均功率）：$P_{MA}[n]$

**ab. 除法：**
执行 $\frac{|C_{MA}[n]|}{P_{MA}[n]}$。这是对自相关结果进行**归一化**。这个比值被称为 **Moorhead 算法** 或 **Schmidl & Cox 算法** 中的**同步度量函数**（Synchronization Metric Function）。当 STS 到来时，这个比值会有一个明显的**峰值**。

**c. 短训练序列同步（STS 发现）:**

**备注：** 其他地方介绍的都不清楚，但是《[基于XILINX_FPGA的OFDM通信系统基带设计.史治国.pdf][#17]》中的 2.3.2 物理层协议数据单元（PPDU）帧结构将短训练序列和长训练序列介绍的极为清楚（一对比就会发现就是 OFDM 中的同步字字段），此外这本书对非常详细介绍了如何徒手在 FPGA 上实现 ieee802.11。

**备注：** `gr-ieee802-11/utils/sync_words.py` 这个 python2 版本的程序可以生成同步字。

这是核心的同步判定模块。它根据输入（同步度量）的峰值来确定 Wi-Fi 短训练序列 (STS) 的开始位置：

- in 口输入：原始数据流 Delay 16
- abs 口输入：复共轭乘积平滑后的值 $C_{MA}[n]$    
- cor 口输入：除法之后的 $\frac{|C_{MA}[n]|}{P_{MA}[n]}$

> Threshold: 560m (0.56): 用于判定峰值是否足以触发同步的门限值    
> Min Plateau: 2: 触发同步后，它可能需要寻找至少2个连续的短训练符号（STS）    

该模块是通过 OOT 实现的：`ieee802_11_sync_short.block.yml` 和 `sync_short.cc`。

该模块使用一个简单的状态机来管理同步过程：

状态 | 枚举值 | 描述
---|---|---
SEARCH | 0 | 模块的**初始状态**，不断扫描输入数据流，寻找帧的起始点
COPY | 1 | **已发现帧起始点**，进入数据复制模式，将后续数据样本作为接收到的帧的一部分输出

```
// 循环遍历归一化同步度量 (in_cor) 样本，检查其是否超过设定的门限 (d_threshold, 即 0.56)
// 并且判断是不是连续 MIN_PLATEAU 次大于阈值
// 如果超过判定为同步成功（找到帧头），切换到 COPY 模式   
case SEARCH: {
    int i;
    for (i = 0; i < ninput; i++) {
        if (in_cor[i] > d_threshold) {
            if (d_plateau < MIN_PLATEAU) {
                d_plateau++;
            } else {
                d_state = COPY;
                d_copied = 0;
                d_freq_offset = arg(in_abs[i]) / 16;//估计频偏
                d_plateau = 0;
                insert_tag(nitems_written(0), d_freq_offset, nitems_read(0) + i);
                dout << "SHORT Frame!" << std::endl;
                break;
            }
        } else {
            d_plateau = 0;
        }
    }
    consume_each(i);//消耗掉已经处理的 i 个样本
    return 0;
}
```

**备注：** 频偏（Fractional Carrier Frequency Offset, CFO）估计是利用短训练序列的周期性（周期为16）

- $C_{MA}[n] = \sum x[k] \cdot \text{conj}(x[k-16]) \approx \sum |x[k]|^2 \cdot e^{j \cdot 2\pi \cdot \Delta f \cdot 16 T_s}$
- $\text{arg}(C_{MA}[n])$ 的相位是 $2\pi \cdot \Delta f \cdot 16 T_s$，其中 $T_s$ 是采样周期
- 因此，频偏 $\Delta f \propto \frac{\text{arg}(C_{MA}[n])}{16}$

```
// 此状态负责将接收到的数据样本输出，并同时应用短训练序列估计的频偏进行实时校正
// 
case COPY: {
    int o = 0;
    // 循环复制: 循环将输入样本复制到输出缓冲区，直到输入/输出耗尽或已复制的样本数 (d_copied) 达到
    // 最大帧长 (MAX_SAMPLES, 约 43,200 个样本，对应约 12ms 的最大帧时间)
    while (o < ninput && o < noutput && d_copied < MAX_SAMPLES) {
        // 帧尾再搜索，继续检查 in_cor[o] 是否再次超过门限
        // 如果再次超过门限，并且已经复制的样本数 d_copied 大于 MIN_GAP (480，即一个帧之间最小间隔的保护时间)，
        // 则判定为下一个帧的起始，重复频偏估计和插入标签的操作，并重置 d_copied。这允许模块连续捕获多帧
        if (in_cor[o] > d_threshold) {
            if (d_plateau < MIN_PLATEAU) {
                d_plateau++;
                // there's another frame
            } else if (d_copied > MIN_GAP) {
                d_copied = 0;
                d_plateau = 0;
                d_freq_offset = arg(in_abs[o]) / 16;
                insert_tag(
                    nitems_written(0) + o, d_freq_offset, nitems_read(0) + o);
                dout << "SHORT Frame!" << std::endl;
                break;
            }
        } else {
            d_plateau = 0;
        }

        // 实时频偏校正
        out[o] = in[o] * exp(gr_complex(0, -d_freq_offset * d_copied));
        o++;
        d_copied++;
    }

    if (d_copied == MAX_SAMPLES) {
        d_state = SEARCH;
    }

    dout << "SHORT copied " << o << std::endl;

    consume_each(o);
    return o;
}
```

**备注：(实时频偏校正)** 将当前样本 in[o] 乘以一个旋转因子 $e^{-j \cdot \Delta f \cdot d_{copied}}$，这个旋转因子实时抵消了估计的小数频偏 $\Delta f$ 对信号引入的相位旋转。d_copied 代表从帧头开始计数的时间样本数。    

**注意：** `insert_tag` 函数负责在帧开始的样本上添加一个流标签（Stream Tag），key 是 "wifi_start"，value 是 d_freq_offset (估计的小数频偏)。下游的 长训练序列 (LTS) 模块 或 解调模块 可以读取这个标签，获取帧的起始位置和估计的频偏值，以便执行进一步的精细同步和信道估计。

**备注：** 接收链路的首要任务是准确检测 OFDM 帧的起始位置。每个 IEEE 802.11a/g/p 帧都以一个短前导序列开头，该序列由一个包含 16 个样本的模式重复 10 次构成（目前 OFDM Carrier Allocator 的同步字的第一个（和第二个）$\text{tuple}$ 对应于 $\text{L-STF}$ 符号的频域序列）

![][p11]

</br>

**2）长训练序列同步**

接收链路中的下一个模块是 “OFDM 同步长序列”（OFDM Sync Long）模块，它负责进行频偏校正和符号对齐。由于发射机和接收机的本地振荡器工作频率可能存在微小差异，因此必须进行频偏校正。频偏矫正和短序列同步介绍的一样，这里我们重点看符号对齐。

符号对齐工作：每个 OFDM 符号包含 80 个样本，其中包括 16 个样本的循环前缀和 64 个样本的数据部分。符号对齐的任务是确定符号的起始位置、提取数据符号，并将其传输给执行快速傅里叶变换（FFT）的算法。这种对齐操作借助长训练序列完成，该长训练序列由一个 64 样本长的模式重复 2.5 次构成。由于该模块只需对输入样本流的一个子集进行处理，且对齐精度要求极高，因此我们采用了匹配滤波技术来实现这一操作。

下图展示了输入流与已知序列的相关性典型变化曲线。图中两个特征峰非常显著且尖锐，从而能够实现极高精度的符号对齐：

![][p12]

我们计算相关性最高的三个峰值的索引，其中 $N_{preamble}$ 表示短前导序列和长前导序列的总长度，LT 表示长训练序列中 64 样本长的重复模式，$argmax_{3}$ 函数返回使表达式取值最大的前 3 个索引。

![][p13]       

由于匹配滤波输出的最后一个峰值位于长训练序列结束前 64 个样本处，因此第一个数据符号的起始位置对应的样本索引为：

![][p14]    

在确定了第一个数据符号的相对位置后，该模块能够提取出所有数据符号，并将对应于单个符号的数据样本块传输到流图中的后续模块。每个 OFDM 帧的第一个符号都会被添加标签，以便后续模块能够识别帧的起始位置。

在已知数据符号起始位置的情况下，我们可以通过对数据流进行子集提取，并将对应于各个数据符号的样本分组，从而去除循环前缀：

![][p15]    

</br>


**3）WiFi 帧均衡器**

长训练序列同步后的数据经过 Stream to Vector 变为有 64 个元素的向量，然后执行 FFT（这是 OFDM 的基本操作），然后送入 WiFi Frame Equallzer 中。

frame_equalizer_impl.cc 文件定义了 GNU Radio gr-ieee802.11 模块中的帧均衡器（Frame Equalizer）的实现，它是一个 GNU Radio 块（Block），负责在接收到的 IEEE 802.11 OFDM 符号 上执行信道均衡、残余频率偏移（Residual Frequency Offset, RFO）补偿，并处理 Signal 字段 的解码，以获取帧的长度和调制编码方案（Modulation and Coding Scheme, MCS）。

**核心功能概述**

`frame_equalizer_impl` 块作为 OFDM 接收链路的一部分：

1.  **输入**：接收 64 个复数（`gr_complex`）的 **OFDM 符号**。
      * 输入项大小：`64 * sizeof(gr_complex)`。
2.  **输出**：输出解码后的 8 比特数据。
      * 输出项大小：48 字节（`uint8_t`，对应 48 个数据子载波上的比特）。
3.  **均衡与补偿**：
      * 接收到 `wifi_start` 标签时，重置帧状态，并从标签中获取初始的频率偏移信息。
      * 对每个符号执行**采样偏移补偿**。
      * 利用**导频子载波**（Pilot Subcarriers）估计并补偿**残余频率偏移（RFO）**。
      * 使用预设的均衡器算法（如 LS、LMS、Comb 等）进行**信道均衡**。
4.  **Signal 字段处理**：
      * 对于帧的第三个 OFDM 符号（`d_current_symbol == 2`），该符号是 **Signal 字段**。
      * 对 Signal 字段的比特进行 **解交织（Deinterleave）** 和 **维特比解码（Viterbi Decode）**。
      * **解析 Signal 字段**，从中提取 **帧的字节长度（`d_frame_bytes`）**、**调制编码方案（MCS）**，并计算出整个数据部分的 **符号总数（`d_frame_symbols`）**。
5.  **标签与消息输出**：
      * Signal 字段成功解析后，会在数据输出流上添加 **标签（Tag）**，包含帧长度、编码、信噪比（SNR）、频率偏移等重要元数据。
      * 均衡后的符号（48个复数）会通过消息端口（`symbols`）以 PMT 格式发送出去。

</br>

**4）WiFi Decode MAC**

WiFi Frame Equallar 的 out 口将数据流送入 WiFi Decode MAC。

该模块是 gr-ieee802.11 接收路径的关键部分，它执行 **PLCP (Physical Layer Convergence Procedure) 的数据解处理**，从 OFDM 符号数据中恢复出 MAC 层的数据包。它依赖于上游模块（如 `WiFi Frame Equallar`）传递的元数据（标签），并执行解映射、解交织、Viterbi 译码和解扰等复杂的物理层后处理，最终通过 CRC 校验验证数据有效性，并将有效的 MAC 帧通过消息传递机制发送给后续的 MAC 层处理模块。

**核心工作流程**

1.  **标签（Tag）检查**:
    * 模块在输入流中查找 **标签**。标签通常由上游模块（如 **`decode_ofdm`**）添加，用于标记一个 **新 802.11 帧的开始**。
    * 如果发现标签（`tags.size()` 不为零），则表明一个新帧开始。

2.  **新帧处理**:
    * 如果 `d_frame_complete == false`，表示上一个帧尚未接收完，此时收到新帧的开始信号，会打印警告并中断上一个帧的接收。
    * 从标签中提取 **元数据（Metadata）**，包括：
        * **`frame bytes`**: 帧的 PSDU 长度（即 MAC 净荷长度 `len_data`）。
        * **`encoding`**: 调制编码方案（MCS）。
    * 根据提取的 `len_data` 和 `encoding` 计算 **帧参数** (`d_frame`) 和 **OFDM 参数** (`d_ofdm`)，包括所需的 OFDM 符号数量 `frame.n_sym`。
    * 检查帧长度是否超过最大允许值 (`MAX_SYM`, `MAX_PSDU_SIZE`)。如果有效，则更新模块的帧参数并重置 `copied = 0`。

3.  **符号收集**:
    * `while` 循环遍历输入项。
    * `if (copied < d_frame.n_sym)`: 只有在帧尚未接收完整时，才会执行符号的复制操作。
    * `std::memcpy(d_rx_symbols + (copied * 48), in, 48);`: 将当前输入的 48 字节（一个符号）复制到内部的符号缓冲区 `d_rx_symbols` 中。
    * `copied++`: 符号计数器加一。

4.  **帧解码触发**:
    * `if (copied == d_frame.n_sym)`: 当接收到的符号数量达到预期值 (`d_frame.n_sym`) 时，表明一个完整的帧已收集完毕。
    * 调用 **`decode()`** 函数进行完整的解码操作。
    * 设置 `d_frame_complete = true`，标记帧接收完成。
    * `break`: 退出 `while` 循环，准备 `consume`。

5.  **消耗输入**:
    * `consume(0, i);`: 消耗已处理的输入项（符号）。

</br>

## 附录一：wifi_mapper OOT 代码详解
### 1. 构造函数与初始化 (`mapper_impl`)

```cpp
mapper_impl(Encoding e, bool debug)
    : block("mapper",
            gr::io_signature::make(0, 0, 0),
            gr::io_signature::make(1, 1, sizeof(char))),
    // ... 成员变量初始化
{
    message_port_register_in(pmt::mp("in"));
    set_encoding(e);
}
```

  * **基类初始化：**
      * `block("mapper", ...)`：设置模块名为 "mapper"。
      * `gr::io_signature::make(0, 0, 0)`：**没有流输入端口**（0 个最小输入，0 个最大输入，0 字节大小）。
      * `gr::io_signature::make(1, 1, sizeof(char))`：**有一个流输出端口**，输出项大小为 `sizeof(char)`（1 字节）。这个 `char` 实际上用于承载调制后的符号数据，后续通常会被一个解映射（demapper）模块转换为复数类型。
  * **消息端口：** `message_port_register_in(pmt::mp("in"));` 注册了一个名为 **"in"** 的消息输入端口，用于接收待处理的 MAC 数据包。
  * **编码：** 接收 `Encoding e` 参数，用于确定 **调制和编码方案（MCS）**，并调用 `set_encoding` 进行设置。

</br>

### 2. 核心工作函数 (`general_work`)

`general_work` 是 GNU Radio 模块的核心数据处理函数。在这个模块中，它负责：**接收消息 -\> 执行 PHY 层处理 -\> 将生成的符号数据推送给流输出。**

#### 2.1 消息接收与处理循环

```cpp
while (!d_symbols_offset) {
    pmt::pmt_t msg(delete_head_nowait(pmt::intern("in")));

    if (!msg.get()) {
        return 0; // 没有新消息，返回
    }
    
    // ... 处理消息
}
```

  * `while (!d_symbols_offset)`：只要当前没有正在发送的符号数据（`d_symbols_offset` 为 0），就尝试从消息队列中获取一个新消息。
  * `delete_head_nowait(pmt::intern("in"))`：非阻塞地从 "in" 消息端口获取一个消息。
  * **数据提取：** 如果消息是一个 **PMT pair**，则提取 PSDU 数据 (`psdu`) 和长度 (`psdu_length`)。

</br>

#### 2.2 PHY 层处理（编码/调制链）

这是代码的核心部分，实现了 802.11 OFDM 的发送数据链：

1.  **参数计算：**
    ```cpp
    frame_param frame(d_ofdm, psdu_length);
    // frame 结构体根据 PSDU 长度和 MCS 确定了帧所需的所有参数，如符号数 (n_sym)、数据位数 (n_data_bits)、编码位数 (n_encoded_bits) 等。
    ```
2.  **内存分配：** 为各个处理步骤（`data_bits`, `scrambled_data`, `encoded_data`, `punctured_data`, `interleaved_data`, `symbols`）分配临时缓冲区。
3.  **处理步骤：** 依次调用 `generate_bits`、`scramble`、`reset_tail_bits`、`convolutional_encoding`、`puncturing`、`interleave` 和 `split_symbols` 函数。这些函数（定义在 `utils.h` 或其他地方）实现了 **IEEE 802.11 规范中对数据字段（DATA field）的全部处理步骤**。(*详情见附录二，包含这些函数的具体实现*)
4.  **符号存储：**
    ```cpp
    d_symbols_len = frame.n_sym * 48; // 总符号数 * 每个OFDM符号的数据子载波数量
    d_symbols = (char*)calloc(d_symbols_len, 1);
    std::memcpy(d_symbols, symbols, d_symbols_len); // 将生成的符号数据复制到模块的成员变量 d_symbols 中
    ```

</br>

#### 2.3 添加标签（Tags）

```cpp
// ... 添加标签代码
add_item_tag(0, nitems_written(0), key, value, srcid);
```

  * 在流的 **第 0 个端口**、**当前已写入项数** 的位置，添加元数据标签（`packet_len`, `psdu_len`, `encoding`）。
  * 这些标签非常重要，它们将 **数据包的边界和元信息** 传送到下游模块（如 **OFDM 调制器**），以便下游模块知道如何处理这批符号。

</br>

#### 2.4 内存释放与流输出

```cpp
// 释放临时缓冲区
// ...

// 将符号数据写入输出流
int i = std::min(noutput, d_symbols_len - d_symbols_offset);
std::memcpy(out, d_symbols + d_symbols_offset, i);
d_symbols_offset += i;
```

  * 将 `d_symbols` 中剩余的数据（从 `d_symbols_offset` 开始）复制到输出缓冲区 `out` 中。`i` 是本次可以输出的项数（取 **请求输出数 `noutput`** 和 **剩余符号数** 的最小值）。
  * `d_symbols_offset += i;` 更新偏移量。

</br>

#### 2.5 完成发送后的清理

```cpp
if (d_symbols_offset == d_symbols_len) {
    d_symbols_offset = 0;
    free(d_symbols);
    d_symbols = 0;
}

return i; // 返回实际输出的项数
```

  * 如果所有符号都已发送完毕，则 **重置偏移量** 并 **释放 `d_symbols` 内存**，等待下一个消息。

</br>

### 3. 私有成员变量

```cpp
private:
    uint8_t d_scrambler;      // 扰码器状态
    bool d_debug;             // 调试标志
    char* d_symbols;          // 存储待发送的完整符号数据缓冲区
    int d_symbols_offset;     // 当前已发送的符号偏移量
    int d_symbols_len;        // 符号数据总长度
    ofdm_param d_ofdm;        // 当前使用的OFDM参数（与MCS相关）
    gr::thread::mutex d_mutex; // 互斥锁，用于保护共享变量（如 d_ofdm, d_symbols）
```

</br>

### 4. 总结

这段代码是一个典型的 **GNU Radio 消息驱动的源模块** 结构。它通过消息接收数据包，在 `general_work` 内部一次性完成复杂的信号处理链（即 802.11 编码、交织和符号映射），然后将生成的符号数据分批推送到流输出端口。这种 **消息驱动 + 内部缓冲/流输出** 的设计模式在处理具有固定数据包结构（如 WiFi/LTE）的通信系统时非常常见。

</br>

## 附录二：utils.cc 代码详解

这段代码 (`utils.cc` 的内容) 定义了 GNU Radio IEEE 802.11 **`mapper`** 模块所需的核心实用工具类和物理层（PHY）处理函数。这些函数实现了将 MAC 层数据包 (PSDU) 转换为待发送的 OFDM 符号数据流所需遵循的 IEEE 802.11a/g 规范步骤。

### 1. 数据结构类解析
#### 1.1 `ofdm_param` 类 (OFDM 参数)

这个类存储了基于不同 **调制和编码方案（MCS）** 所需的 IEEE 802.11 OFDM 物理层参数。

| 成员变量 | 含义 | 对应规范值 (以 BPSK\_1\_2 为例) |
| :--- | :--- | :--- |
| `encoding` | 调制和编码方案枚举值 | `BPSK_1_2` |
| `n_bpsc` | **每个子载波的比特数 (Bits per Subcarrier)** | 1 (BPSK) |
| `n_cbps` | **每个 OFDM 符号的编码比特数 (Coded Bits per Symbol)** | 48 (48个数据子载波 $\times$ 1 bit/载波) |
| `n_dbps` | **每个 OFDM 符号的数据比特数 (Data Bits per Symbol)** | 24 (48个编码比特 $\times$ 1/2 编码率) |
| `rate_field` | **RATE 字段** 的值（用于 PLCP 报头） | `0x0D` (表示 6 Mbps) |

**构造函数 `ofdm_param(Encoding e)`：**
根据传入的 `Encoding`（如 `BPSK_1_2`, `QPSK_3_4` 等），初始化上述所有参数，这些数值直接来源于 IEEE 802.11 规范（如 Table 17-3）。

</br>

#### 1.2 `frame_param` 类 (帧参数)

这个类存储了针对**特定 PSDU 长度**和**特定 MCS** 所需的整个数据帧的参数。

**构造函数 `frame_param(ofdm_param& ofdm, int psdu_length)`：**
根据 OFDM 参数 (`ofdm`) 和 MAC 数据包长度 (`psdu_length`) 计算帧的整体大小：

* `psdu_size`: 接收到的 MAC 数据包的字节数。
* **`n_sym` (OFDM 符号数):**
    $$n\_{sym} = \lceil \frac{16 + 8 \times psdu\_{size} + 6}{n\_{dbps}} \rceil$$
    其中：
    * $16$: **Service Field** 的比特数（2字节）。
    * $8 \times psdu\_{size}$: **PSDU** 的总比特数。
    * $6$: **Tail Bits** 的比特数（6个零）。
    * $\lceil \dots \rceil$: 向上取整，确保所有数据都能装入整数个 OFDM 符号。
* `n_data_bits`: **总数据比特数**（包括 Service Field, PSDU, Tail Bits 和填充位）：$$n\_{sym} \times n\_{dbps}$$
* `n_pad`: **填充比特数**：$$n\_{pad} = n\_{data\_bits} - (16 + 8 \times psdu\_{size} + 6)$$
* `n_encoded_bits`: **总编码比特数**（未打孔）：$$n\_{sym} \times n\_{cbps}$$

</br>

### 2. 物理层处理函数解析

这些函数实现了 `mapper_impl::general_work` 中调用的发送数据链。输入/输出数据通常是 `char*`，其中每个 `char` 代表一个 **比特**（值为 `0` 或 `1`）。

#### 2.1 `generate_bits`

**功能：** 准备 DATA 字段的原始比特流。
**步骤：**
1.  将 **Service Field** 的 16 个比特设置为 **0**。
2.  将 **PSDU**（MAC 数据包）的每个字节转换为 8 个比特，追加到 Service Field 之后。

</br>

#### 2.2 `scramble` (扰码)

**功能：** 使用 **加扰器** 对数据比特进行异或操作，以平滑数据流中的“0”和“1”的分布，提高同步和均衡性能。
**机制：**
* 使用一个 **长度为 7 的伪随机序列（PN 序列）** 发生器，基于 $G(z) = z^{-7} \oplus z^{-4} \oplus 1$ （即 LFSR 的第 4 位和第 7 位进行异或）。
* `initial_state` (初始状态) 由 MAC 层通过信号量（在这里是 `d_scrambler`）提供，通常是 7-bit 种子，用于区分不同的数据包。
* **反馈计算 (`feedback`):** $$feedback = (state\text{ 的第 7 位}) \oplus (state\text{ 的第 4 位})$$ （代码中 `64` 是 $2^6$，即第 7 位；`8` 是 $2^3$，即第 4 位）。
* **输出比特：** $$out[i] = feedback \oplus in[i]$$
* **状态更新：** 状态左移一位，并将新的反馈比特移入最低位。

</br>

#### 2.3 `reset_tail_bits` (尾部比特归零)

**功能：** 在 Service Field 和 PSDU 之后，紧接着的 **6 个比特** 必须是 **0**（即 **Tail Bits**），以将卷积编码器的状态重置为全零，方便接收端解码。
**实现：**
* 定位到 Tail Bits 的起始位置：`scrambled_data + frame.n_data_bits - frame.n_pad - 6`。
* 使用 `memset` 将这 6 个比特设置为 0。

</br>

#### 2.4 `convolutional_encoding` (卷积编码)

**功能：** 实现 $\mathbf{R=1/2}$ 的 **卷积编码**，将 1 个输入比特编码成 2 个输出比特。
**机制：**
* **约束长度 K=7**。
* **生成多项式 (Generator Polynomials):**
    * $g_0$: $133_8 = 1011011_2 \implies z^{-0} \oplus z^{-2} \oplus z^{-3} \oplus z^{-5} \oplus z^{-6}$
    * $g_1$: $171_8 = 1111001_2 \implies z^{-0} \oplus z^{-1} \oplus z^{-2} \oplus z^{-3} \oplus z^{-6}$
* 代码中用八进制数 `0155`（即 $133_8$）和 `0117`（即 $171_8$）来表示生成多项式的连接，并利用 `ones` 函数计算**异或和**（即校验位）。
    * $out[2i]$ 对应 $g_0$。
    * $out[2i+1]$ 对应 $g_1$。
* **`ones(n)` 函数：** 计算一个字节中 **1 的个数**（实现异或和）。
* **编码：** $$out[2i] = (\text{state} \text{ \& } 0155)\text{ 中 1 的个数} \pmod 2$$ $$out[2i+1] = (\text{state} \text{ \& } 0117)\text{ 中 1 的个数} \pmod 2$$

</br>

#### 2.5 `puncturing` (打孔)

**功能：** 根据编码率 ($R$) 移除部分编码比特，以提高总的码率（如 $R=2/3$ 或 $R=3/4$）。
**机制：**
* **R=1/2 (BPSK/QPSK/QAM16\_1\_2):** 不打孔，所有编码比特都被保留。
* **R=2/3 (QAM64\_2\_3):** 移除每 4 个编码比特中的第 4 个。
* **R=3/4 (其他 3/4 码率):** 移除每 6 个编码比特中的第 4 个和第 5 个。

</br>

#### 2.6 `interleave` (交织)

**功能：** 重新排列编码比特，以分散突发错误对单个 OFDM 符号的影响。交织在**符号维度**和**子载波维度**上进行。
**机制：**
1.  **比特交织：** 深度为 $s = \max(n\_{bpsc}/2, 1)$。
    * $first[j]$ 定义了第一层置换。
2.  **符号交织：** 深度为 16。
    * $second[i]$ 定义了第二层置换。
3.  **交织过程：** 对**每个 OFDM 符号**内的 $n\_{cbps}$ 个比特进行两次置换。
    * `reverse` 参数表示该函数也可用于解交织。

</br>

#### 2.7 `split_symbols` (比特到符号的映射)

**功能：** 将交织后的比特流转换为调制符号数据，这是 **比特到星座图点** 映射的前一步。
**机制：**
* 将 $n\_{bpsc}$ 个比特（例如 BPSK 为 1 个，QPSK 为 2 个）打包成一个 `char`（字节）。
* 这个字节（`out[i]`）代表一个**数据子载波**上的调制符号。
* **注意：** 这里的 `char` 存储的是**调制前的比特组**，例如 QPSK 的 `char` 包含 2 个比特，稍后会被一个 **Mapper** 模块（如 `gr::ieee802_11::symbol_mapper`）转换为复数 I/Q 值。


</br>

[[1]. BLOG —— IEEE 802.11架构（介绍的很细，通俗易懂）][#1]    
[[2]. GitHub —— GNU Radio 的 IEEE 802.11 a/g/p 收发器][#2]         
[[3]. WiKi —— IEEE 802.11（太全了，适合当字典）][#3]    
[[4]. BLOG —— WiFi protocol stack][#5]    
[[5]. PDF —— IEEE 802.11 MAC 和 PHY 层详细介绍][#11]    
[[6]. Blog —— IEEE 802.11 Mac帧][#12]    
[[7]. Blog —— Wi-Fi: Overview of the 802.11 Physical Layer and Transmitter Measurements][#13]          
[[8]. Blog —— IEEE 802.11架构][#14]    
[[9]. 论文 —— An IEEE 802.11a/g/p OFDM Receiver for GNU Radio（就是 gr-ieee802.11 出处的论文）][#15]     
[[10]. 论文 —— On the design of OFDM signal detection algorithms for hardware implementation（gr-ieee802.11 的短侦测算法基于的论文）][#16]       
[[11]. BOOK —— 基于XILINX_FPGA的OFDM通信系统基带设计.史治国][#17]    


[#1]:https://www.geeksforgeeks.org/computer-organization-architecture/ieee-802-11-architecture/
[#2]:https://github.com/bastibl/gr-ieee802-11    
[#3]:https://en.wikipedia.org/wiki/IEEE_802.11    
[#4]:https://en.wikipedia.org/wiki/IEEE_802.11g-2003     
[#5]:https://www.futurelearn.com/info/courses/cybercrime-prevention-and-protection/0/steps/340104       
[#6]:https://github.com/oldprogram/gnuradio_demo/blob/main/B210%E4%B8%93%E9%A1%B9/03-%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA%E4%B8%8E%E9%A9%B1%E5%8A%A8%E5%AE%89%E8%A3%85/readme.md
[#7]:https://github.com/oldprogram/gnuradio_demo/blob/main/B210%E4%B8%93%E9%A1%B9/10-%E8%B6%85%E5%BC%BA%E9%9B%B7%E8%BE%BE%E5%B7%A5%E5%85%B7%E5%8C%85gr-radar%E8%AF%A6%E8%A7%A3/readme.md    
[#8]:https://www.bilibili.com/video/BV1AXc3ecETY/?vd_source=84f94348691c2906fc1038d54989b7e0    
[#9]:https://www.bilibili.com/video/BV1B8c6eBERW/?vd_source=84f94348691c2906fc1038d54989b7e0    
[#10]:https://github.com/oldprogram/gnuradio_demo/blob/main/%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B/20-GNU%20Radio%20OFDM/02-OFDM_TX%E8%AF%A6%E8%A7%A3/README.md    
[#11]:https://media.techtarget.com/searchMobileComputing/downloads/CWAP_ch8.pdf    
[#12]:https://www.geeksforgeeks.org/computer-networks/ieee-802-11-mac-frame/     
[#13]:https://www.tek.com/en/documents/primer/wi-fi-overview-80211-physical-layer-and-transmitter-measurements     
[#14]:https://www.geeksforgeeks.org/computer-organization-architecture/ieee-802-11-architecture/      
[#15]:https://conferences.sigcomm.org/sigcomm/2013/papers/srif/p9.pdf     
[#16]:https://www.semanticscholar.org/paper/On-the-design-of-OFDM-signal-detection-algorithms-Liu/22e1dc18d34f4bda38fdb7385e626893c7bff3dc     
[#17]:https://web.xidian.edu.cn/jpma/files/66cef35b471f7.pdf     


[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/wifi_stack.png    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/wifi_loopback_grc.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/wifi_loopback_grc_gui.gif
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/wifi_transceiver_grc.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/wifi_tx_grc.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/wifi_phy_hier_grc_send.png    
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/wifi_phy_hier_grc_receive_pre.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/erp_ofdm_ppdu_payload.png    
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/wifi_phy_hier_from_source_to_ofdm.png    
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ieee_802_11_mac_frame_structure.png     
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ofdm_short_sync.png    
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ofdm_long_sync.png      
[p13]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ofdm_long_sync_Np.png    
[p14]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ofdm_long_sync_np.png    
[p15]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/ofdm_long_sync_s.png    



