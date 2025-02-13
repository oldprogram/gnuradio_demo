
在 `gnuradio_demo/基础教程/18-GNU Radio 蓝牙广播发送/02-hackrf 发送 ble 广播详解/python/main.py` 增加能够生成 `normalization_sample_hackrf.iq` 的逻辑，这样就可以用 hackrf_transfer 直接发送 ble 广播包了：

```
# hackrf_transfer -t normalization_sample_hackrf.iq -f 2402000000 -s 4000000 -R -x 47
```

同时在同级目录增加 `send_use_gnuradio.py` 是 GNU Radio 流程图使用 hackrf 发送 ble 的精简版，主要用于了解发送代码的核心。
