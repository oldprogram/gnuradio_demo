   


### 一、雷达背景知识
#### 1.1 按照频段划分

频段分类 | 波段 | 优点 | 缺点 | 应用领域
---|---|---|---|---
米波段 | 包括 HF、VHF 和 UHF 频段 | 简单可靠、容易获得高辐射功率、容易制造、动目标显示性能好、不受大气传输的影响、造价低等优点 | 该波段雷达的主要缺点是目标的角分辨率低 | 在对空警戒雷达、电离层探测器、超视距雷达中有广泛的应用    
分米波段 | 包括 L 和 S 波段 | 与米波频段雷达相比，分米波段雷达具有较好的角度分辨率、外部噪声干扰小、天线和设备尺寸适中等优点 | 该波段雷达的辐射功率不如米波段的高，大气回波和大气衰减对其有一定的影响 | 在对空监视雷达中得到广泛使用。当要求一部雷达兼有对空探测和目标跟踪两种功能时，S 波段雷达最为合适。S 波段雷达是介于分米波和厘米波段之间的一种折中选择，可以成功地实现对目标的监视和跟踪，广泛地使用于舰载雷达
厘米波段 | 包括C、X、Ku 和 K 波段 | 厘米波段雷达主要用于武器控制系统，它具有体积小、重量轻、跟踪精度高、可以得到足够大的信号带宽等优点 | 该波段雷达的主要缺点是辐射功率不高、探测距离较近、大气回波和大气衰减影响较大、气象杂波等外部噪声干扰大等。但气象雷达主要是探测气象杂波，因此多工作在这个频段 | 在机载火控雷达、机载气象雷达、机载多普勒导航雷达、地面炮瞄雷达、民用测速、防撞雷达中被广泛使用
毫米波段 |  | 毫米波段雷达具有天线尺寸小、目标定位精度高、分辨率高、信号频带宽、抗电磁波干扰性能好等优点 | 但毫米波段雷达具有辐射功率更小、机内噪声较高、气象杂波等外部噪声干扰大、大气衰减随频率的增高而迅速增加等缺点，又几乎掩盖了其优点 |  由于大气的衰减随频率的增高并不是单调地增加，而是存在着一些大气衰减较小的窗口，除非某些特定的应用（例如汽车防撞雷达）​，毫米波段雷达大多仅限于工作在这些窗口上。
激光波段 |  | 激光波段雷达具有良好的距离和角度分辨率等优点，在测距和测绘系统中常被选用 | 其缺点是辐射功率小、波束太窄、搜索空域周期长、不能在复杂气象条件下工作等 | 目前，激光雷达已经广泛应用于三维高分辨率成像测绘等。

</br>

![][p5]

</br>

#### 1.2 按照功能划分

按照用途分类：

```
地面雷达 | 早期预警雷达（超远程雷达） | 机载预警雷达  | 无线电高度表 | 军用雷达 |
舰载雷达 | 搜索和警戒雷达           | 机载截击雷达  | 雷达引信    | 民用雷达 | 
机载雷达 | 指挥引导雷达（监视雷达）   | 机载护尾雷达   
星载雷达 | 火控雷达                | 机载导航雷达
        | 制导雷达                | 机载火控雷达
```

按照工作体制分类：

```
扫描雷达      | 脉冲雷达    | 圆锥扫描雷达 | 单基地雷达 | 有源雷达
相控阵雷达    | 连续波雷达   | 单脉冲雷达   | 双基地雷达 | 无源雷达
频扫雷达      | 线性调频雷达 | 隐蔽锥扫雷达 | 多基地雷达 |
合成孔径雷达   | 编码雷达    |
逆合成孔径雷达 | 噪声雷达    |
```

其他分类：

```
按照信号处理方式分类       | 按工作波长分类 | 用波段的名称 | 按测量目标坐标参数 | 按某种特殊用途命名 |
------------------------|-------------|------------|-----------------|-----------------|
脉冲多普勒（PD）雷达       | 米波雷达     | L 波段雷达   | 两坐标雷达       | 扫描边跟踪雷达      |
动目标显示（MTI）雷达      | 分米波雷达    | S 波段雷达  | 三坐标雷达        | 目标特征信号测量雷达 |
频率分集雷达              | 厘米波雷达    | X 波段雷达  | 超视距雷达        | 探地雷达           |
极化分集雷达              | 毫米波雷达    |            | 测速雷达         | 二次雷达          |
相参或非相参积累雷         | 激光/红外雷达  |           | 测高雷达
合成孔径雷达和逆合成孔径雷达 |              |           | 成像雷达 
```

**PS：** 脉冲雷达，测量从发射到接收的时间来估算距离；连续波雷达（CW），测量发射波和接收波之间的频差来直接计算目标的径向速度；脉冲多普勒雷达（PD），它既能利用脉冲技术测量目标的距离，又能利用多普勒效应测量目标的速度；调频连续波雷达（FMCW），通过发射频率随时间线性变化的连续波来精确测量目标的距离和速度 <sup>[20][#20]</sup>。    

![][p7]

**PS：** FMCW 为了同时测量距离和速度，通常会采用 **上下扫频（Up-down Chirp）或两个连续扫频（Two-Chirp）** 的方式。

- 上扫频（Up-Chirp）: 发射频率线性增加。当目标向雷达移动时，多普勒效应会使回波频率比静止时更高；当目标远离时，回波频率会更低。这个多普勒频移会叠加在距离产生的频率差上。
- 下扫频（Down-Chirp）: 发射频率线性减小。此时多普勒效应的影响方向正好相反。

通过对上扫频和下扫频得到的两个频率差进行处理，就可以将距离引起的频率差和速度引起的多普勒频移分离开来，从而同时解算出目标的距离和径向速度。

![][p6]


</br>

### 二、环境构建

使用 ubuntu 24.04 的 GNURadio `3.10.9.2 (Python 3.12.3)` 版本 (22.04 和 arch linux 都会因为 osmos 版本过老、过新导致 hackrf 不能用）

可以使用我创建好的 Dockerfile 构建 GR 环境：

```
git clone git@github.com:btfz-sdr/docker-gnuradio.git
cd docker-gnuradio/gnuradio-releases-310/
docker build -t ubuntu:gnuradio-310 .
```

之后就可以直接使用上面构建的环境了：

```
➜  Desktop xhost + # 只需一次
➜  Desktop docker run --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --device /dev/snd -v /home/btfz/Desktop/WORK_GNURADIO/gnuradio_demo/综合教程/09-雷达/GNU-Radio:/home/gnuradio/lidar --device /dev/dri -v /dev/bus/usb/:/dev/bus/usb/ --privileged --group-add=audio -it ubuntu:gnuradio-310 bash

# 进入 docker 之后
gnuradio@127:~$ zsh     
➜  ~ sudo gnuradio-companion   # passwd: gnuradio

# 想要再开一个终端，需要 `docker ps`，然后：
# - `docker exec -it 52597dcede29  bash`
# - `docker exec -it 52597dcede29 gnuradio-companion`
```

</br>

### 三、实验尝试

基于 github 上一个回波和多普勒频移的 [gnuradio demo][#1]，基于 `CW_Radar.grc` 连续波雷达，将 plutosdr 改为 hackrf（因为使用 plutosdr 发现 TX1, RX1 离的比较近会相互影响，使用两个 hackrf 可以拉开距离）；

同时，增加由于物体运动导致频率变化的变化值给计算出来，采用[基础教程的 db_cal 计算频谱][#2]，并计算频谱峰值对应的横坐标，然后根据参数计算出频率。

![][p1]

然后使用一个可乐罐子+2.4G棒状天线作为发（想当作定向天线），然后用一个淘宝购买的 wifi 2.4G 定向增强天线作为收，调节 tone_freq 让 RX_AFT_LPF 回波峰值在 500Hz，这样后面的带阻滤波器能过滤稳定波，很好的让多普勒频偏波通过。

经过很多测试发现，当有金属物体（锅盖）靠近和远离时，频率有波动 10Hz 左右，但是和理论值（如果物体向着SDR移动，频率会略微升高；如果物体远离SDR移动，频率会略微降低。1m/S 会产生 16Hz 的频偏）靠近、远离策略有偏差，倒是会有频偏偏移。

后来发现：自己做的可乐+棒状天线的方向性不好，或者说收发信号质量差，而商业的 2.4G 定向增强器却效果很好，于是[淘宝上再买一个][#4]，待后续测试。

![][P2]

</br>

### 四、进阶优化

等新的 2.4G 定向天线来了后，测试效果仍然不好，怀疑是变化太快，肉眼不太方便看出来变化，因此做了个小算法来放大变化：

![][p3]

核心思路是：使用 `QT GUI Msg Push Button` 来触发，让 `Freq Offset Cal` 记录稳定时的频偏，然后当实际由于多普勒产生频偏时，计算实时频偏与稳定频偏的差值，然后再根据多普勒公式，计算物体移动速度和方向；同时为了让瞬间的变化能够被长时间观察到，在 `Freq Offset Cal` 增加 3S 的最大差值维护，如果 3S 内没有比该差值大的值就保留该差值作为 3S 内的输出，如果有则更新该差值和平滑 3S 窗口。

经过上述处理，数据能比较清晰的看出来了。


</br>

### 五、完整操作

1）两个 hackrf 全部连接到电脑，一个做为发送，一个作为接收        
2）调节 hackrf 的收发功率，让接收数据振幅不要超过 1（在反射物在最近的情况下）       
3）调节 tone_freq 让带阻滤波器频谱的峰值出现在 600Hz（这里直接跳过带阻滤波器，使用自己的方法测算频偏）    
4）以反射方式摆放发射与接收天线，前面放置一个障碍物，防止被其他运动物体影响      
5）让一个小车靠近远离，进行观察雷达测速     


</br>

### 参考链接

[[1]. GitHub —— 一个回波和多普勒频移的 gnuradio demo][#5]     
[[2]. GitHub —— 一个单频连续波多普勒雷达的 gnuradio demo, 有点老，博客都没了][#6]     
[[3]. GNURadio —— gr-lidar 详细、资料丰富][#7]    
[[4]. Book —— 《雷达系统及其信息处理-许小剑 黄培康》][#19]     
[[5]. gnu radio 的一个博客][#8]        
[[6]. gnu radio 的一个博客][#9]    
[[7]. gnu radio 的一个论文《Real-Time FMCW Radar System for Waveform Optimization using SDRs》][#10]    
[[8]. 一个论文《A GNU Radio Based Software-Defined Radar》][#11]      
[[9]. gnu radio 的一个论文《Application of Software Radios for Sensing & Instrumentation at ORNL》][#12]    
[[10]. 《Development of L-Band FMCW Radar on SDR using GNU RADIO》][#13]       
[[11]. 《A GNU Radio Based Software-Defined Radar》][#14]     
[[12]. 《GSoC过去项目》][#15]    
[[13]. 《GNU-Radio Simulation Application for Impulse Radar Technique on Ground Object Detection》][#16]      
[[14]. 《GNU Radio 和 Python FMCW 雷达工具包的实现》][#17]     
[[15].《Study of the use of a SDR Passive RaDAR for the safe outdoor operation of an atmospheric LiDAR》][#18]    
[[16]. BLOG —— 利用雷达探测空气中的火山灰][#19]    
[[17]. 均一教育平台 —— 多普勒科普视频][#22]    



[#1]:https://github.com/tmytek/GNU-Radio    
[#2]:https://www.bilibili.com/video/BV1pxYye6Eav/?vd_source=84f94348691c2906fc1038d54989b7e0    
[#3]:https://gemini.google.com/app/247ce80368c054f8?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all    
[#4]:https://item.taobao.com/item.htm?from=cart&id=616441766177&skuId=5027056309918&spm=a1z0d.6639537%2F202410.item.d616441766177.884a7484tKeTxV
[#5]:https://github.com/tmytek/GNU-Radio      
[#6]:https://github.com/luigifcruz/software-radar         
[#7]:https://github.com/luigifcruz/software-radar   
[#8]:https://www.gnuradio.org/grcon/grcon17/presentations/hacking_the_wireless_world_4_0/Balint-Seeber-Hacking-the-Wireless-World-4.0.pdf        
[#9]:https://gnuradio-fr-19.sciencesconf.org/263065/FP_GnuDays2019_v3.pdf     
[#10]:https://events.gnuradio.org/event/24/contributions/640/attachments/209/520/SD_grconf24_finalpaper.pdf    
[#11]:https://corescholar.libraries.wright.edu/etd_all/91/    
[#12]:https://www.gnuradio.org/grcon/grcon18/presentations/SDR_Sensing_at_ORNL/4-James-Humphries-SDR_Sensing_at_ORNL.pdf      
[#13]:https://ieeexplore.ieee.org/document/10493476      
[#14]:https://scispace.com/pdf/a-gnu-radio-based-software-defined-radar-5m8215fcze.pdf     
[#15]:https://wiki.gnuradio.org/index.php/GSoCPastProjects     
[#16]:https://ieeexplore.ieee.org/document/8666440       
[#17]:https://ujcontent.uj.ac.za/esploro/outputs/conferencePaper/Implementation-of-a-GNU-Radio-and/9912736407691       
[#18]:https://www.researchgate.net/publication/332072486_Study_of_the_use_of_a_SDR_Passive_RaDAR_for_the_safe_outdoor_operation_of_an_atmospheric_LiDAR  
[#19]:https://weread.qq.com/web/reader/aa032d105a0199aa002633e#outline?noScroll=1    
[#20]:https://gemini.google.com/app/2ee7097d84c554a7?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all    
[#21]:https://www.sciencedirect.com/topics/engineering/pulsed-radar    
[#22]:https://www.junyiacademy.org/junyi-science/science-high/main-seni-phy/senior-high-physics-book0/t10-physics/t-physics-high-unit4/v/Dyl9Rmvuqog?v=Dyl9Rmvuqog

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202507/db_cal_max_index.png  
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202508/2.4G_10dbi_lidar.png    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202508/duopule_sdr.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202508/freq_part04110609.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202508/fmcw_Radar.jpg
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202508/cw_p_pd_fmcw.jpg

  
 
