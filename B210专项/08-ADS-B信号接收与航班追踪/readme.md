### 一、前言
第十集：ADS-B信号接收与航班追踪

介绍ADS-B协议和1090MHz频段。

使用USRP和dump1090等工具接收和解码航班信息。

在地图上实时显示航班位置。

</br>

### 二、gr-air-modes

gr-air-modes 是一个开源的软件定义无线电（SDR）接收器，用于解析飞机的 Mode S 应答器信号，包括 ADS-B 报告。它基于 Gnuradio 框架，支持 USRP 和 RTLSDR 等设备，可将信号处理后以多种格式输出。

项目地址：https://github.com/bistromath/gr-air-modes/tree/master


#### 2.1 环境构建

由于是老 gnuradio 项目，因此需要用 docker，项目提供了 dockerfile 文件，因此直接可以构建：

```
# 构建的命令
systemctl start  docker
docker build -t ubuntu:gr-air-modes . 

# 以后每次启动的命令
systemctl start  docker
xhost -          
xhost +local:docker 
docker run -it --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/bus/usb/:/dev/bus/usb/ \
    -v /home/btfz/Desktop/B210:/home/gnuradio/B210 \
    --privileged \
ubuntu:gr-air-modes  bash 

export UHD_IMAGES_DIR=/home/gnuradio/B210/B210_images/
uhd_find_devices
```

安装好之后可以用 `modes_rx --help` 来看看是否安装成功。

</br>

#### 2.2 经典案例

**案例 1：基础模式 - 接收并在终端显示航班数据**

这是最基本的用法，通过 USRP B210 接收 1090MHz ADS-B 信号，并在终端实时显示解析后的航班信息。

```
modes_rx -s uhd -f 1090000000 -g 40 -l 30.24661575,119.95823993
```

参数说明：

-s uhd：指定使用 USRP 设备（uhd 是 USRP 硬件驱动的标识）
-f 1090000000：设置接收频率为 1090MHz（ADS-B 信号的标准频率）
-g 40：设置 RF 增益为 40dB（USRP B210 增益范围建议 0-76dB，可根据信号强度调整）
-l 35.14218,133.55393：设置接收地点的 GPS 坐标（示例为杭州，需替换为你的实际位置）

运行后，终端会实时输出附近飞机的信息（如航班号、高度、速度、经纬度等）。

输出格式的基本结构：

```
(信号强度 时间戳) 消息类型描述 [附加信息]
```

1. No handler for message type 24 from XXXXX

(-47 24.68509747) No handler for message type 24 from 620783

- 含义：接收到了类型为 24 的 Mode S 消息，但当前版本的 gr-air-modes 不支持解析这种类型。
- 原因：Mode S 消息有多种类型（0-31），部分类型（如 24）可能用于特殊用途（如军用或特定航空公司自定义），开源工具可能未实现解析逻辑。
- 620783：发送该信号的飞机的 ICAO 地址（全球唯一的六进制标识符，类似飞机的 "身份证号"）。

2. Type 4 (short surveillance altitude reply) from XXXXX at XXXft [附加信息]

(-47 27.77715472) Type 4 from 3b10a2 at 18775ft (SPI)

- 含义：这是类型 4 的 Mode S 短报文，主要用于报告飞机的高度。
- 关键信息：
    - 3b10a2：飞机 ICAO 地址
    - 18775ft：飞机当前高度（英尺，1 英尺 ≈ 0.3048 米）
    - (SPI)：附加状态（SPI = Special Position Identification，特殊位置识别，通常是飞行员手动触发，用于向地面管制标识自己的位置）

3. Type 0 (short A-A surveillance) from XXXXX at XXXft [附加信息]

(-46 36.21386772) Type 0 from 9ff8f2 at 106700ft (speed 300-600kt)

- 含义：类型 0 的 Mode S 短报文，主要用于 飞机间（A-A = Air to Air）监视，通常由 TCAS（空中防撞系统）发出，用于避免碰撞。
- 关键信息：
    - 106700ft：高度（注意：这个高度远超民航客机常规巡航高度，可能是数据误差或特殊飞行器）
    - (speed 300-600kt)：速度范围（kt = 节，1 节 ≈ 1.852 公里 / 小时）
    - 其他常见附加信息：
        - (Vertical TCAS resolution only)：仅使用垂直防撞措施（如爬升 / 下降避让）
        - (aircraft is on the ground)：飞机在地面（未起飞）

4. Type 5 (short surveillance ident reply) from XXXXX with ident XXXX [附加信息]

(-50 41.09071772) Type 5 from 76d8bf with ident 4510 (GROUND ALERT)

- 含义：类型 5 的 Mode S 短报文，用于 身份识别应答（飞行员在管制要求下发送，确认自己的身份）。
- 关键信息：
    - ident 4510：识别码（飞行员手动输入的 4 位数字，用于地面管制快速识别）
    - (GROUND ALERT)：附加状态（可能表示地面告警，如滑行道冲突等）


5. Type 20 (link capability report) from 231f72: ACS: 0x5e863, BCS: 0xae6b, ECS: 0x6b, continues 6 at 95400ft

(-46 193.36927622) Type 20 link capability report from 231f72: ACS: 0x5e863, BCS: 0xae6b, ECS: 0x6b, continues 6 at 95400ft

- 含义：类型 20 的 Mode S 扩展电文，即 “链路能力报告”，用于向地面管制和其他飞机广播本机的通信、导航、监视（CNS）能力，确保空中数据交互兼容。
- 关键信息：
    - 231f72：发送消息的飞机的 ICAO 地址（全球唯一的六进制标识符）
    - ACS: 0x5e863：机载能力集（19 位二进制编码的十六进制表示），用于标识飞机支持的 ADS-B、Mode S 等监视功能（如高度 / 位置 / 速率报告能力）
    - BCS: 0xae6b：广播能力集，用于说明飞机支持的 Mode S 广播消息类型及传输频率
    - ECS: 0x6b：扩展能力集，补充标识飞机的特殊功能（如是否支持军用模式、特定导航系统等）
    - continues 6：表示该消息是分片传输的长消息，此为第 6 个分片
    - at 95400ft：飞机当前高度为 95400 英尺（约 29080 米，远超民航常规巡航高度，可能是高空特殊飞行器或数据误差）

6. Type 21 TCAS report from 4e1e53:  (no handler for TTI=0) ident d80
(-45 111.68943897) Type 21 TCAS report from 4e1e53:  (no handler for TTI=0) ident d80

- 含义：类型 21 的 Mode S 消息，属于空中防撞系统（TCAS）报告，用于飞机间传递防撞相关信息，帮助避免空中碰撞。
- 关键信息：
    - 4e1e53：发送该消息的飞机的 ICAO 地址（全球唯一标识符）
    - (no handler for TTI=0)：表示当前版本的解析工具不支持处理 TTI=0 的信息（TTI 可能是 TCAS 消息中的特定类型标识或参数）
    - ident d80：飞机的识别码（此处为十六进制表示的识别信息，用于身份标识）

</br>

**案例 2：输出数据到 Google Earth（KML 文件）**

如果需要在 Google Earth 中可视化飞机位置，可将数据输出为 KML 文件：

```
modes_rx -s uhd -f 1090000000 -g 45 -l 30.24661575,119.95823993 -K aircrafts.kml
```

参数说明：

- -K aircrafts.kml：指定 KML 输出文件（Google Earth 可直接打开该文件显示实时飞机位置）
- 其他参数同上（增益调整为 45dB，坐标示例为杭州）

1）需要在 aircrafts.kml 同目录下放置一个 airports.png 图片，表示飞机，同时修改 `kml.py` 文件对应的条目，为 `./airports.png`（当然也可以手动编辑 `/usr/local/lib/python3.6/dist-packages/air_modes/kml.py` 将其中的 `\n\t\t\t<Icon><href>airports.png</href></Icon>` 去掉，采用默认的图标）。此外，[网页端的 google earth][#3] 似乎不支持自定义的 png 图标，桌面端的需要仔细和对图标的朝向，才能达到想要的效果，下图是个例子。

![][p1]

2）我研究了 [kml 的语法][#2]，写出一个自动刷新的脚本给 google earth 网页端，发现不支持 networklink，最终得出结论：[网页端不支持动态刷新，因此需要使用桌面版][#1] `yay -S google-earth-pro`(这是 arch linux 安装命令，根据你的平台安装命令自行安装）

安装好之后按照下图所示创建一个 Network Link：

![][p2]

并设置动态刷新 aircrafts.kml：

![][p3]

之后就可以拖动地球找到我们对应的坐标点，观察搜索到的飞机信息：

![][p4]    

</br>

**案例 3：指定 USRP B210 硬件参数（进阶配置）**

USRP B210 支持多种子设备（subdev）和天线选择，可通过参数精细配置：

```
modes_rx -s uhd -f 1090000000 -g 60 -l 30.24661575,119.95823993 -K aircrafts.kml \
  -R A:B -A TX/RX -D "num_recv_frames=512"
```

参数说明：

- -R A:B：选择 USRP 的子设备（B210 有 A 和 B 两个通道，A:B 表示使用 B 通道）    
- -A TX/RX：指定使用的天线（B210 支持 TX/RX 和 RX2 天线，根据实际连接选择）    
- -D "num_recv_frames=512"：向 USRP 驱动传递额外参数（这里设置接收缓冲区大小，优化高数据量场景）    
- 坐标示例为杭州，增益 60dB（适用于信号较弱区域）    

</br>

**案例 4：启动 SBS-1 兼容服务器（供其他软件连接）**

许多飞行跟踪软件（如 [Virtual Radar Server][#7]）支持 SBS-1 协议，可通过 -P 参数启动兼容服务器：

```
modes_rx -s uhd -f 1090000000 -g 60 -l 30.24661575,119.95823993 -P -t 5000
```

参数说明：

- -P：在端口 30003 启动 SBS-1 兼容服务器（供外部软件连接）
- -t 5000：额外在端口 5000 启动一个 TCP 服务器，用于自定义数据接收
- 坐标示例为杭州，增益 60dB（适用于信号较弱区域）  

启动后，其他软件（如飞行跟踪工具）可通过 localhost:30003 或 localhost:5000 接收数据。

</br>

Virtual Radar Server is an open-source .NET application that runs a local web server，其在 linux 上安装理论上会很麻烦，不过有个 [github 开源项目][#8]支持一键安装（适配的平台超多）：

```
bash -c "$(wget -qO - https://github.com/mypiaware/virtual-radar-server-installation/raw/master/virtual_radar_server_install.sh)"
```

在安装过程中可以顺带配置下 Receiver（我们这里是 B210 SDR）：

```
Receiver name:         B210                     # 任意名称
Receiver source type:  BaseStation              # 对应 SBS-1 
Receiver address:      192.168.101.192          # ADS-B 接收器设备的 IP 地址。如果 VRS 与接收器安装在同一设备上，输入统一台电脑的 ip
Receiver port:         30003                    # 输入提供飞机消息的 ADS-B 接收器的端口值
```

安装完之后 `vrs -gui` 以 GUI 方式启动 VRS（先启动 modes_rx），同时可以选中 B210 进行调整配置：

![][p6]    

当我们看到 `modes_rx` 的 log 中显示 connect 时，表明我们 vrs 已经连接上了接收者，此时打开 `http://127.0.0.1:8090/VirtualRadar` 链接，就能在网页中看到实时的飞机信息了：

![][p7]


</br>

**案例 5：禁用终端输出，仅保存数据到文件**

如果不需要在终端显示，可禁用输出并专注于数据保存：

```
modes_rx -s uhd -f 10900000 -g 50 -l 30.24661575,119.95823993 \
  -n -K aircrafts.kml -P -t 5000
```

参数说明：

- -n：禁用终端输出（减少干扰，专注于后台数据处理）
- 同时启用 KML 文件输出和 SBS-1 服务器，适合无人值守场景

</br>

[[1]. 豆包 —— 咨询 gr-air-modes 的用法(个人)][#4]   
[[2]. Gemini —— 咨询网页端的 google earth networklink 为啥不行(个人)][#1]    
[[3]. Github —— gr-air-modes][#5]      
[[4]. B210专项 —— 03-环境搭建与驱动安装][#6]        

[#1]:https://gemini.google.com/app/0f92dddf5acff112?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all   
[#2]:https://developers.google.com/kml/documentation/kmlreference?hl=zh-cn       
[#3]:https://earth.google.com/web/       
[#4]:https://www.doubao.com/chat/20295479965559810        
[#5]:https://github.com/bistromath/gr-air-modes/tree/master        
[#6]:https://github.com/oldprogram/gnuradio_demo/blob/main/B210专项/03-环境搭建与驱动安装/readme.md         
[#7]:https://www.virtualradarserver.co.uk/    
[#8]:https://github.com/mypiaware/virtual-radar-server-installation    

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/airports14120412.png    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/google_earth_add_networklink.png    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/google_earth_add_networklink_config.png      
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/google_earth_airports_show.png       
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202411/hackrf_dev.png    
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/vrs_config.png    
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202509/vrs_web.png



