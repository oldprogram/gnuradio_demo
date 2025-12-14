### 一、项目概览与实验目标

#### 1.1 🛠️ 项目背景：软件定义无线电 (SDR) 测向基础

本次实验旨在利用 **软件定义无线电 (SDR)** 硬件平台，特别是 **Ettus Research USRP B210**，来探索多通道接收系统的核心特性，并将其应用于基础的**信号测向技术**。

信号测向，如**到达角 (Angle of Arrival, AOA) 定位**，是无线电监测、雷达和通信定位系统中的关键技术。它的实现高度依赖于多天线阵列接收通道间的**相位关系**的精确测量与控制。    

<img src="https://tuchuang.beautifulzzzz.com:3000/?path=202512/b210_aoa.png" width="600" style="display:block;"></img>

#### 1.2 实验目的

本系列实验分为两个主要目标：

1.  **B210 双收通道相位特性分析与校准：**
    * 验证 B210 硬件在双路同时接收（MIMO-RX）时，由于共用时钟带来的**相位差的稳定性和可预测性**。
    * 掌握在 **GNU Radio Companion (GRC)** 中，使用**复数共轭相乘**等标准 DSP 方法，对双路接收信号的固有相位差进行**实时测量与校准**的技术。

2.  **基于双通道的到达角 (AOA) 定位原理演示：**
    * 理解 AOA 技术中**信号入射角**、**天线间距**与**接收相位差**之间的几何和数学关系。
    * 通过实际操作，演示如何通过改变信号源的相对位置，观察并利用测量到的实时相位差，来验证 AOA 测向的基本原理。

#### 1.3 💻 硬件与软件环境

* **SDR 接收设备：** Ettus Research USRP B210 (具备双路接收能力)。
* **SDR 发射设备 (信号源)：** Great Scott Gadgets HackRF One (作为稳定的窄带信号发射源)。
* **软件环境：** Docker 容器化的 Ubuntu 环境，预装 **GNU Radio 3.10** 及 UHD 驱动。

</br>

### 二、启动 Docker 并准备环境

按照之前的流程，正常启动专为 B210 开发准备的 docker 环境：

```
systemctl start  docker
xhost -                 # 清理旧的 xhost 设置
xhost +local:docker     # 授予特定的 xhost 访问权限
docker run -it --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/bus/usb/:/dev/bus/usb/ \
    -v /home/btfz/Desktop/B210:/home/gnuradio/B210 \
    --privileged \
    --group-add=audio \
    ubuntu:gnuradio-310 bash
zsh
export UHD_IMAGES_DIR=/home/gnuradio/B210/B210_images/  
uhd_find_devices
```

由于本案例会用到 hackrf，因此下面是准备 hackrf 环境的操作：

```
sudo apt install usbutils
➜  ~ lsusb
Bus 001 Device 008: ID 1d50:6089 OpenMoko, Inc. Great Scott Gadgets HackRF One SDR
Bus 003 Device 003: ID 2500:0020 Ettus Research LLC USRP B210

sudo chmod 666 /dev/bus/usb/001/008
hackrf_info 
```

</br>

### 三、实验一：B210 双收相位差实时校准
#### 3.1 物理基础

B210 的硬件特性导致其双路同时接收时**相位差是稳定可预测**的：两个射频通路的关键在于它们共用一个主时钟 (Reference Clock)，这个时钟确保了两个通道的采样操作是同步的。即使使用共同时钟，由于射频电缆长度、滤波器和放大器组件的温度差异，两个通道的起始相位可能存在一个固定的、非零的偏差。

我们实验一就是使用一个 hackrf 的一个通道作为发，一个 B210 的两个通道作为收，来**观察相位差的可预测性**。并且在此基础上利用巧妙的数学原理**实现相位差实时纠正**：

![][p2]

</br>

#### 3.2 数学基础

我们在 GNU Radio 中计算两个复数信号 $S_1$ 和 $S_2$ 的相位差 $\Delta\phi = \phi_1 - \phi_2$，最优雅且标准的 DSP 方法是：

**1）复数共轭相乘 (Complex Conjugate Multiplication)。**

将其中一个信号（例如 $S_2$）取共轭，然后与另一个信号 $S_1$ 相乘。

* **数学原理：**
    假设 $S_1 = A_1 e^{j\phi_1}$ 和 $S_2 = A_2 e^{j\phi_2}$。
    $$\text{Result} = S_1 \times S_2^*$$
    $$\text{Result} = (A_1 e^{j\phi_1}) \times (A_2 e^{-j\phi_2})$$
    $$\text{Result} = (A_1 A_2) e^{j(\phi_1 - \phi_2)}$$

* **结果：** 得到的复数结果的**相位**就是 $\Delta\phi = \phi_1 - \phi_2$，其**幅度**是两个原信号幅度的乘积。

**2）提取相位角 (Argument/Phase Extraction)。**

从上一步得到的复数结果中，提取出其相位角。

* **所需模块：**
    * `Complex to Arg` (模块分类：Math Operators)

* **数学原理：**
    该模块计算复数的反正切函数 (arctangent, $\text{atan2}(Q, I)$)，将相位结果 $\Delta\phi$ 以**弧度 (Radians)** 为单位输出。通常范围是 $[-\pi, \pi]$。

</br>

#### 3.3 实验效果

我们的流程图实现了 B210 第一路接收向第二路接收的相位纠正，因此在 time sink 图中可以清晰看到 signal3（第二路接收） 和 signal5（相位纠正后的信号） 实现相位同步。

并且我们应一个独立的 time sink 展示实时的相位差（已经转换为度数）。我们会发现：当我们调节发送基带数据的频率、发射功率时该相位差没有明显变化：

![][p1]

备注：这里仍然有一些小波动，可能是**温度漂移 (Thermal Drift)**、**本振噪声 (LO Noise)** 等因素引起，属于合理范围。

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202512/b210_mino_test1_result.gif
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202512/b210_mino_test1_grc.png     


