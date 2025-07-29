### 1、前言

本文将介绍如何在 GNU Radio 中创建和运行第一个流程图。


</br>


### 2、启动 GNU Radio

GNU Radio Companion （GRC）是用于创建和运行流程图的视觉编辑器。GRC 使用 .grc 文件，然后会转换为 python .py 流程图。

打开终端，运行：

```
sudo gnuradio-companion
```

GRC 窗口如下：

![][p2]

</br>

双击 Options 块，可以通过修改 ID 和 Title 来重命名流程图：

![][p3]

- ID 就是 Python 流程图的名字：sineWaveFlowgraph.py
- Title 用来描述该流程图

</br>

点击 `File` 按钮，点击 Svae 进行保存 GRC 流程图：

![][p4]

输入 `sineWaveGRC.grc` 作为 .grc 文件的名称，以将其与 .py 流程图区分开：

![][p5]


</br>

### 3、新增块

添加块以创建第一个流程图。Gnu Radio 有大量信号处理的块，你可以在 GRC 右侧看到，也可以直接用 ` CTRL + F` 进行搜索：

![][p6]

</br>

搜索 `Signal Source` 块，将其拖入 FRC 工作空间：

![][p7]

</br>

相同操作，将 `Throttle`、`QT GUI Frequency Sink`、`QT GUI Time Sink` 拖入工作空间：

![][p8]

- Signal Source 用于产生复杂的正弦波
- QT GUI Frequency Sink 用于显示频谱
- QT GUI Time Sink 用于显示时间阈
- Throttle 用于流量控制

</br>

将这些块按照下图方式连接起来（如果块的名字还是红色，表示还有问题）：

![][p10]

</br>

### 4、运行

按下面红框框住的按钮，即可启动：

![][p12]

你会看到一个新的窗口，显示了时域和频域信号：

![][p11]

</br>

### 参考链接

[[1]. GNU Radio 系列教程（一） —— 什么是 GNU Radio][#1]
[[2]. Your First Flowgraph][#2]



[#1]:https://www.cnblogs.com/zjutlitao/p/16648432.html
[#2]:https://wiki.gnuradio.org/index.php?title=Your_First_Flowgraph

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=/5c/34db9ac63096ee25239f3e0ba89163.png
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=/5d/f8fb88892101aa1eebe252176f679c.png
[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=/98/c2cfc67ae24505cdbf9821b52fccc9.png
[p4]:https://tuchuang.beautifulzzzz.com:3000/?path=/18/de9d78b7b3ee8eb2c47c31444da52a.png
[p5]:https://tuchuang.beautifulzzzz.com:3000/?path=/f1/3e813dc1075acac47234445cc3f90a.png
[p6]:https://tuchuang.beautifulzzzz.com:3000/?path=/db/8124d6d51147369f4e7cb47a0cffde.png
[p7]:https://tuchuang.beautifulzzzz.com:3000/?path=/fd/4fb0995cf8ac5fa3296a2a3a49152e.png
[p8]:https://tuchuang.beautifulzzzz.com:3000/?path=/02/9e3cbaa2a46e9c25ce4b845e810c41.png
[p9]:https://tuchuang.beautifulzzzz.com:3000/?path=/55/c9ce33c3ad4e525fb98f5174f726d3.png
[p10]:https://tuchuang.beautifulzzzz.com:3000/?path=/9c/a25cdeac6f7e699c169e8eb2c5c679.png
[p11]:https://tuchuang.beautifulzzzz.com:3000/?path=/e1/c283d3ac31a321f12c68948aee4571.png
[p12]:https://tuchuang.beautifulzzzz.com:3000/?path=/3c/ff4632f934272c94896f52b680c923.png
[px]:https://tuchuang.beautifulzzzz.com:3000/?path=/7b/24abbb1cf6f0bee204045d1f3bdb34.png

