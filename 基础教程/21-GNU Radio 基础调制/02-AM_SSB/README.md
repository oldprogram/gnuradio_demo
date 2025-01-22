
### 一、基础知识

在无线电通信中，**单边带调制（SSB）** 或 **单边带抑制载波（SSB-SC）**，是一种可以更加有效的利用电能和带宽的调幅技术。调幅技术输出的调制信号带宽为源信号的两倍。单边带调制技术可以避免带宽翻倍，同时避免将能量浪费在载波上，不过因为设备变得复杂，成本也会增加。

三种振幅调制 AM、DSB、SSB https://blog.csdn.net/qq_44431690/article/details/105478661

维基百科：单边带调制 https://zh.wikipedia.org/wiki/%E5%8D%95%E8%BE%B9%E5%B8%A6%E8%B0%83%E5%88%B6

![][p1]

</br>

#### 1.1 分类

![][p2]

分类 | 中文 | 公式 | 波形
---|---|---|---
AM | 普通调幅 | ![][p3] | ![][p4] </br>m 越大调幅越深</br>![][p5]</br></br>频谱：</br>![][p6] | ![][p7] </br>调幅和单边带信号频谱示意图。
DSB | 抑制载波的双边带调幅 | 将 AM 信号中的载波分量抑制掉就形成了 DSB,它可以用载波和调制信号直接相乘得到：</br></br>![][p8] | ![][p9]</br>![][p10] | 相比于基带，下边带（LSB）频谱是反相的。</br></br>举例来说，一个 2kHz 的音频基带信号调制到一个 5MHz 的载波上，</br>如果是上边带（USB）的话会产生 5.002MHz 的频率，下边带就会是 4.998 MHz。
SSB | 单边带调制 | ![][p11] | ![][p12] | 

</br>


### 二、SSB 实现

方法 | 细节 | x
---|---|---
滤波法 | ![][p13] | ![][p14]
相移法 | ![][p15] | ![][p16]
相移滤波法 | ![][p17] | ![][p18]

</br>

#### 2.1 带通滤波器法

滤波器法比较简单（参考[第四个链接][#4]）：

![][p13]

流程图如下：

![][p19]

</br>

![][p20]

</br>

#### 2.2 相移法

参考[第二个链接][#2]：

![][p21]

</br>

![][p22]


注：这里用到了希尔伯特变换器： https://wiki.gnuradio.org/index.php/Hilbert


</br>

### 参考链接

[[1].WiKi —— Simulation example: Single Sideband transceiver][#1]    
[[2].BLOG —— SSB Modulation on GNU Radio][#2]    
[[3].BLOG —— RTL-SDR for SSB on GNU Radio][#3]    
[[4].BLOG —— 基于GNU Radio 无线电平台实现各种常规通信信号的模拟][#4]     
[[5].BLOG —— Building a Remote SSB Receiver with an RTL-SDR, OrangePi and GNU Radio][#5]    
[[6].BLOG —— GNURadio SSB Receiver and Recording IQ Data][#6]    
[[7].GITHUB —— gnuradio-grc-exsamples][#7]    
[[8].GITHUB —— Simple SSB Receiver in GNU Radio Companion][#8]    
[[9].论文 —— Understanding the 'Phasing Method' of Single Sideband Demodulation][#9]    


[#1]:https://wiki.gnuradio.org/index.php/Simulation_example:_Single_Sideband_transceiver    
[#2]:https://jeremyclark.ca/wp/telecom/ssb-modulation-on-gnu-radio/    
[#3]:https://jeremyclark.ca/wp/telecom/rtl-sdr-for-ssb-on-gnu-radio/      
[#4]:https://blog.csdn.net/weixin_37728585/article/details/122055255        
[#5]:https://www.rtl-sdr.com/building-a-remote-ssb-receiver-with-an-rtl-sdr-orangepi-and-gnu-radio/    
[#6]:http://play.fallows.ca/wp/radio/software-defined-radio/gnuradio-ssb-receiver/    
[#7]:https://github.com/antonjan/gnuradio-grc-examples/tree/master    
[#8]:https://www.oz9aec.net/radios/gnu-radio/simple-ssb-receiver-in-gnu-radio-companion    
[#9]:https://wwwusers.ts.infn.it/~milotti/Didattica/Segnali/SSB-Lyons.pdf     

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_kind.jpg    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_define.jpg    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_am_func.png    
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_am_1.png    
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_am_2.png    
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_am_3.png    
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_am_4.png    
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_dsb_func.png    
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_dsb_1.png    
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_dsb_2.png    
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_ssb_func.png    
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/signal_ssb_1.png    
[p13]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way1.png    
[p14]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way1_1.png    
[p15]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way2.png    
[p16]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way2_1.png    
[p17]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way3.png    
[p18]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way3_1.png    
[p19]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way1_grc.png    
[p20]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way1_grc_result.png    
[p21]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way2_grc.png    
[p22]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/ssb_way2_grc_result.png    






















