### 一、准备环境

为了统一环境，我们使用 docker构建统一的系统环境，这里采用  ubuntu 24.04 的 GNURadio 3.10.9.2 (Python 3.12.3) 版本
如果你使用的系统本身就是  ubuntu 24.04 ，可以不用 docker，当然你也可以选择使用虚拟机中跑 ubuntu 24.04 

如果你也准备使用 docker，我这边有创建好的 Dockerfile：

```
sudo systemctl start docker # 启动 docker

# 拉取 docker file，并构建一个名为 `ubuntu:gnuradio-310` 的镜像
git clone git@github.com:btfz-sdr/docker-gnuradio.git 
cd docker-gnuradio/gnuradio-releases-310/
docker build -t ubuntu:gnuradio-310 .
```

如果想要直接在 ubuntu 上构建，强烈建议使用 Ubuntu 24.04，这样可以保持一致，具体安装哪些东西可以参考 dockerfile:

```
# 安装其他软件包
RUN apt-get update
RUN apt-get install -y gnuradio gnuradio-dev cmake git libboost-all-dev libcppunit-dev liblog4cpp5-dev python3-pygccxml pybind11-dev liborc-dev python3-pip libgsl-dev clang-format gr-osmosdr hackrf libhackrf-dev libhackrf0 vim zsh wget gedit libuhd-dev uhd-host
```

</br>

### 二、运行
#### 2.1 启动电脑

如果使用 docker 可以直接用下面命令运行：

~~`xhost + # 开机后只需一次`~~    
~~`docker run --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --device /dev/snd -v /home/btfz/Desktop/B210:/home/gnuradio/B210 --device /dev/dri -v /dev/bus/usb/:/dev/bus/usb/ --privileged --group-add=audio -it ubuntu:gnuradio-310 bash`~~


```
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
```

只需要将 `/home/btfz/Desktop/B210` 换为你主机中的 B210 工作空间，上述命令会将主机的工作空间映射到 docker 中的 `/home/gnuradio/B210`。

</br>

#### 2.2 给 B210 下载镜像

我们需要将设备通过 USB 连接到电脑上，然后首次运行 `uhd_find_devices` 进行查找设备：

```
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex

Using images directory: <no images directory located>

Set the environment variable 'UHD_IMAGES_DIR' appropriately or follow the below instructions to download the images package.

Please run:

 "/lib/x86_64-linux-gnu/uhd/utils/uhd_images_downloader.py"

No UHD Devices Found
```

报上面错误表明我们没有指定 UHD_IMAGES_DIR，我们进行指定下：

```
sudo mkdir -p /home/gnuradio/B210/B210_images
sudo chmod +666 /home/gnuradio/B210/B210_images

# 特别注意，这个只对当前窗口有用，并且只对非 sudo 有用，如果想要之后用 sudo 运行 uhd_xx 命令，需要 sudo -E uhd_xx
export UHD_IMAGES_DIR=/home/gnuradio/B210/B210_images/  
```

然后运行脚本进行下载镜像（上面 No UHD Devices Found 的 LOG 中说的 uhd_images_downloader.py 路径不对）：

```
/usr/libexec/uhd/utils/uhd_images_downloader.py
```

本教程使用闲鱼唐朝击剑鱼丸的带有 GPS 校时能力的性价比超高的国产 USRP B210，烧录到 B210 的镜像和官方的有区别，因此我们需要我们使用鱼丸给的资料中的 `USRP_B210资料/需替换BIN文件/usrp_b210_fpga.bin` 替换 `B210_images` 下的同名文件：

```
cp USRP_B210资料/需替换BIN文件/usrp_b210_fpga.bin B210_images/usrp_b210_fpga.bin 
```

此时再运行 `uhd_find_devices` 就能看到我们的设备了：

```
➜  B210 uhd_find_devices
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: 30AA038
    name: Custom_SDR_B210
    product: B210
    type: b200
```

</br>

#### 2.3 熟悉常用命令


| 命令                      | 功能说明                                              | 示例命令                        |                                                            
| ----------------------- | ------------------------------------------------- | ------------------------------------------ |       
| `uhd_config_info`       | 查看 UHD 驱动的配置信息，包括版本、支持的设备类型、编译选项等。                | `uhd_config_info --version` （查看 UHD 版本）|                                                                              
| `uhd_find_devices`      | 扫描并列出当前系统中可识别的 USRP 设备，显示设备型号、序列号、IP 等信息。         | `uhd_find_devices` （默认扫描所有接口）      |                                                                                 
| `uhd_fft`               | 基于 UHD 的实时频谱分析工具，可接收 USRP 信号并以图形化界面显示频谱。          | `uhd_fft --freq 2.45e9 --gain 30 --samp-rate 1e6` （分析 2.45GHz 频段，采样率 1MHz）  |                                            
| `uhd_image_loader`      | 向 USRP 设备加载固件（FPGA 镜像、固件文件），通常用于设备初始化或升级。         | `uhd_image_loader --args "type=b200,serial=12345678" --fw-path /usr/share/uhd/images/usrp_b200_fpga.bin`         |
| `UHD_IMAGES_DIR`        | 环境变量，指定 UHD 固件 / 镜像文件的默认存储路径，供其他命令自动读取。           | `echo $UHD_IMAGES_DIR` （查看当前设置的路径）   |                                                                                   
|                         |                                                   | `export UHD_IMAGES_DIR=/opt/uhd/images` （临时设置新路径）           |                                                            
| `uhd_images_downloader` | 自动下载 UHD 支持的各类 USRP 设备所需的最新固件和 FPGA 镜像文件。         | `uhd_images_downloader` （默认下载到系统默认路径）|                                     
|                         |                                                   | `uhd_images_downloader --install-location /opt/uhd/custom_images` （指定下载目录）   |
| `uhd_rx_nogui`          | 无图形界面的 USRP 接收工具，可通过命令行参数配置接收参数，适合服务器环境。          | `uhd_rx_nogui -f 93e6 -g 30 -o 48000 -m FM -O hw:0,0` （接收 FM 93MHz 信号，无界面输出）(源码有错误，需要修改对应行，将 float 转 int `vim /usr/bin/uhd_rx_nogui`)                           |
| `uhd_siggen`            | 无图形界面的 USRP 信号发生器，可生成正弦波、方波等基础信号并通过 USRP 发射。      | `uhd_siggen --freq 2.4e9 --gain 10 --amplitude 0.5` （发射 2.4GHz 正弦波，幅度 0.5）                        |
| `uhd_siggen_gui`        | 图形化界面的 USRP 信号发生器，支持可视化配置信号参数（频率、幅度、波形类型等）。       | `uhd_siggen_gui -f 2.4e9` （启动图形界面，在界面中设置发射参数后点击 “Start”）                                                                    |
| `uhd_usrp_probe`        | 详细探测 USRP 设备的硬件信息，包括通道数、支持的频率范围、增益范围、采样率等。        | `uhd_usrp_probe` （探测第一个识别到的 USRP 设备） |    


