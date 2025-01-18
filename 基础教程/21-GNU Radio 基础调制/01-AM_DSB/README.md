
### 一、基础知识

在AM调制中，载波的振幅根据调制波而变化。这可以通过调制方程来描述：

```
AM = Ac*[1+m*cos(wm*t)]*cos(wc*t) 
   = Ac*cos(wc*t) +Ac*m*cos(wm*t)*cos(wc*t) 
   = Ac*cos(wc*t)+Am*cos(wm*t)*cos(wc*t)
```

- 调制波形 = Am*cos(wm*t)
- 载波 = Ac*cos(wc*t)
- m = 调制指数 = Am/Ac <=1


当 m＝1（100%）时，mod 波形的振幅等于载波振幅，这导致 mod 载波到达 2xAc 的最深调制：

```
cos(wm*t)*cos(wc*t)  = 1/2[cos((wm+wc)*t)) + cos((wc-wm)*t)]
```

此时：调制的频谱在（wc+wm）和（wc-wm）处具有USB和LSB分量。在100%调制时，边带下降10log（1/4）=-6dB。在50%调制时，边带下降10log（m^2/4））=10*log（1/16）=-12dB。

</br>

### 二、流程图详解

根据第一节中的 AM 调制公式，绘制如下流程图：

![][p1]

使用两个信号源，一个用于调制波形，另一个用于载波。为了简单我们使用浮点数（所有块和所有变量都设置为浮点），然后使用加法和乘法块来实际构建 Mod 方程。设置：

- m 从 0～1 变化
- mod 频率 300～2700
- 载波频率 5k~15k

</br>

### 三、实验观察：

mod_index = 1 时：

- 时域图（左边）观察到：载波振幅在 2*Ac 处达到峰值，并下降到 0（注意，当 m >1 时，会发生过调制，这会产生严重的非线性）。你可以在载波的振幅中看到低频调制波形的形状。
- 频谱图（右边）观察到：10KHz + 1KHz = 11Kz 的 USB 和 10KHz - 1KHz = 9KHz 的 LSB。与 10Khz 的电平差为 (-14.5dB – (-20.5))= 6dB

![][p3]

m=0.5 或 50% 调制时：

- 载波振幅在 1.5*Ac 处达到峰值，并下降到 0.5Ac。你可以在载波的振幅中看到低频调制波形的形状。
- 频谱图中，10KHz + 1KHz = 11Kz 的 USB 和 10KHz - 1KHz = 9KHz 的 LSB。与 10Khz 的电平差为 (-14.5dB – (-26.5))= 12dB。

![][p4]

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/grc_am_dsb.png    
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/grc_am_dsb_result1.png    
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/grc_am_dsb_m1_result.png    
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=202501/grc_am_dsb_m0_5_result.png    



