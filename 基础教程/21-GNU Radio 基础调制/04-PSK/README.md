
### 一、基础知识

PSK 调制（Phase Shift Keying）：一中通过调制载波的相位来传输数字信息的调制方式，常见的有 BPSK（Binary PSK）、QPSK（Quadrature PSK）等

</br>


### 二、流程图介绍

#### 1.1 对 vector 进行分别调制，看出来的数据是否OK

这里的原理图采用 BPSK、QPSK、8PSK、16QAM，对 4*3个 [0x55,0,0x01,0,0x55,0,0x11,0,0x55,0,0x51,0] 字节（4*3*8=96 bits）进行调制，因为星座转换器具备自动 RRC 滤波效果，为了方便观察，这里再加一个 RRC，用来减小 ISI：

![][p1]

根据《星座图通信原理：https://zhuanlan.zhihu.com/p/594337231》，不同 PSK 调制有如下星座分布：

![][p2]

同时注意到：samp_rate = 32k，sps = 4    
因此：symbol_rate = 32k/4 = 8k -> one symbol 0.125ms    

- when BPSK, 1 bit one symbol, 1byte -> 1ms    
- when QPSK, 2 bits one symbol, 2bytes -> 1ms    
- when 16QAM, 4 bits one symbol, 4bytes -> 1ms    
- when 8PSK, 3 bits one symbol, 3bytes -> 1ms    

</br>

**因此：**
BPSK：

![][p3]

QPSK：

![][p4]

QAM16：

![][p5]

8PSK：

![][p6]

</br>

#### 1.2 使用多相时钟同步，获取最好采样点，打印星座图

为了直观看到到底是哪种 PSK 调制，一般使用星座图，但是如果直接将星座转换器输出的数据进行星座图绘制，会出现采样点偏差采样，导致采样的数据不清晰等问题。此时使用多相时钟同步块进行完美采样，这样星座图会更清晰：

![][p7]

**注意到**，我们失能了 vector 输入，改为随即输入，这是为了获取更多、更均匀的数据点，才能使星座铺满，运行效果如下：

![][p8]

![][p9]

![][p10]

![][p11]

</br>

### 参考链接

[[1]. GNU Radio —— QPSK_Mod_and_Demod][#1]       
[[2]. GNU Radio —— Simulation_example:_BPSK_Demodulation][#2]    
[[3]. GNU Radio —— Guided_Tutorial_PSK_Demodulation&redirect][#3]    
[[4]. BLOG —— PSK调制解调][#4]    
[[5]. ZHIHU —— 数字调制-PSK][#5]    
[[6]. WIKI —— Phase-shift keying][#6]    



[#1]:https://wiki.gnuradio.org/index.php?title=QPSK_Mod_and_Demod    
[#2]:https://wiki.gnuradio.org/index.php/Simulation_example:_BPSK_Demodulation    
[#3]:https://wiki.gnuradio.org/index.php?title=Guided_Tutorial_PSK_Demodulation&redirect=no    
[#4]:https://blog.csdn.net/gemengxia/article/details/115599104    
[#5]:https://zhuanlan.zhihu.com/p/378180502?eqid=bf5f2b27000113430000000564868dbd    
[#6]:https://en.wikipedia.org/wiki/Phase-shift_keying    


[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_grc1.jpg    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_xingzuo.jpg    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_bpsk_data.png    
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_qpsk_data.png    
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_qam16_data.png    
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_8psk_data.png    
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_grc2.png    
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_bpsk_xingzuo.png    
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_qpsk_xingzuo.png    
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_8psk_xingzuo.png    
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/psk_16qam_xingzuo.png    









