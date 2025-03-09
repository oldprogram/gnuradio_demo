
### 前言

之前我已经陆续出了 3 篇蓝牙收和 2 篇蓝牙发的视频，将蓝牙 BLE 广播收发的协议栈讲的非常清楚了：

![][p1]

<sup>图片来源：https://www.beautifulzzzz.com/gnuradio/</sup>

[![][p2]][#1] [![][p3]][#2] [![][p4]][#3] [![][p5]][#4] [![][p6]][#5]

**这里将其单独拎出来组成一个 BLE + SDR 的专题，用于汇总关于蓝牙协议栈在 SDR 上实现的各种技术点。**

</br>

### [一、开题之作][#9]   

为了方便后续代码构建，我将之前零零散散的关于 BLE+SDR 的相关工程代码，全部合并到一个独立仓库中 [auto_test_tool][#6]。

<sup>**PS：** 这个仓库是之前我的一个很老的仓库，用于编写一些简单的自动化测试的 python 串口工具，因为里面有些组件整合适合 BLE 广播包的解析与发送，因此就在这里附加了。</sup>

为了防止后续的课程对代码修改导致老课程不方便复现，我这里每个课程都会生成一个 tag，这样每个课程都可以拉取对应的 tag 来还原现场。比如，我们这个开题之作采用的是 `ble_course_1`，因此可以使用下面三种方式拉取代码：

方法 | 命令 | 备注
---|---|---
https | `git clone --branch ble_course_1  https://github.com/nbtool/auto_test_tool.git` | 小白懂 git 但不懂 ssh
ssh | `git clone --branch ble_course_1 git@github.com:nbtool/auto_test_tool.git` | 既懂 git 又懂 ssh
点击下载 | https://github.com/nbtool/auto_test_tool/releases/tag/ble_course_1 | 啥都不懂

</br>

OK，开题相关的铺垫到此结束，那么硬核的东西也不能少：

![][p7]

如上图，我将之前的所有 BLE 广播包接收教程的代码全部重新整理，形成上图所示能兼容 hackrf、plutosdr、limesdr 和 zmq 等不同 SDR 源的蓝牙广播接收解析系统（抓包器）。

具体的教程细节见：[app/app_sdr_ble_adv_rx][#7]

</br>

### 二、动态发送 BLE 广播包

上节我们将 BLE 广播包接收代码进行全部整理，本节我们将 BLE 广播包发送代码进行全部整理，实现每隔 1S 更换广播内容，并从零开始合成 BLE 广播 IQ 数据，然后调用 SDR 发送，实现 BLE 动态广播能力：

![][p8]

具体的教程细节见：[app/app_sdr_ble_adv_tx][#8]


[#1]:https://www.bilibili.com/video/BV1ta4y157VV/?spm_id_from=333.1387.collection.video_card.click    
[#2]:https://www.bilibili.com/video/BV18h4y1Y7mf/?spm_id_from=333.1387.collection.video_card.click    
[#3]:https://www.bilibili.com/video/BV1Q84y1D7tZ/?spm_id_from=333.1387.collection.video_card.click    
[#4]:https://www.bilibili.com/video/BV1VT421k7cA/?spm_id_from=333.1387.collection.video_card.click    
[#5]:https://www.bilibili.com/video/BV1WWv1emEvA/?spm_id_from=333.1387.collection.video_card.click    
[#6]:https://github.com/nbtool/auto_test_tool    
[#7]:https://github.com/nbtool/auto_test_tool/tree/master/app/app_sdr_ble_adv_rx    
[#8]:https://github.com/nbtool/auto_test_tool/tree/master/app/app_sdr_ble_adv_tx    
[#9]:https://www.bilibili.com/video/BV1bARMYLEGX/?vd_source=84f94348691c2906fc1038d54989b7e0    

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/history_ble_video.png     
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/video1.png    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/video2.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/video3.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/video4.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/video5.png   
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/jia_gou.png    
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202503/BLE_ADV__jia_gou.png



 
