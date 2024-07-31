#!/usr/bin/env python
# coding=utf-8
import numpy as np

class bsp_signal:
    @staticmethod
    def sample_cosine_and_sine():
        num_samples = 1025  # 实际只取 1024 一个周期左闭右开
        amplitude = 127
        x_values = np.linspace(0, 2 * np.pi, num_samples)
        cos_samples = np.round(amplitude * np.cos(x_values)).astype(int)
        sin_samples = np.round(amplitude * np.sin(x_values)).astype(int)
        return cos_samples[0:1024], sin_samples[0:1024]

