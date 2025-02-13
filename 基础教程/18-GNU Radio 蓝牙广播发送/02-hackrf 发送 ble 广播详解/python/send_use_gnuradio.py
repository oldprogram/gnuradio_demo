#!/usr/bin/env python
# coding=utf-8
from gnuradio import gr
from gnuradio import blocks
import osmosdr
import pmt

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        # 设置参数
        self.tx_freq = 2402000000  # 发送频率
        self.samp_rate = 4e6       # 采样率
        self.IF = 26               # 中频增益

        # HackRF Sink
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + 'hackrf=0'
        )
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.osmosdr_sink_0.set_center_freq(self.tx_freq, 0)
        self.osmosdr_sink_0.set_if_gain(self.IF, 0)
        self.osmosdr_sink_0.set_gain(0, 0)

        # 文件源
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, 
            './normalization_sample.bin', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.intern("Begin"))

        # 连接文件源到 HackRF Sink
        self.connect((self.blocks_file_source_0, 0), (self.osmosdr_sink_0, 0))

    def start_transmission(self):
        # 启动流图
        self.start()

    def stop_transmission(self):
        # 停止流图
        self.stop()
        self.wait()

def main():
    tb = top_block()
    tb.start_transmission()

    try:
        input("Press Enter to stop transmission...\n")
    finally:
        tb.stop_transmission()

if __name__ == '__main__':
    main()

