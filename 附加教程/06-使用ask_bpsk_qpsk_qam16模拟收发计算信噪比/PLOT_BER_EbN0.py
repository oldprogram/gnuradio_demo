#!/usr/bin/env python
# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import matplotlib.ticker as ticker

# ================= 1. 基础配置 =================
ebn0_db = np.linspace(-4, 26, 800)
ebn0_lin = 10**(ebn0_db / 10)

def Q(x):
    return 0.5 * erfc(x / np.sqrt(2))

# ================= 2. 调制方式定义 =================
mod_list = [
    {'name': 'BPSK',   'cat': 'psk', 'M': 2,   'mkr': 'o', 'clr': 'navy',    'off': 0},
    {'name': 'QPSK',   'cat': 'psk', 'M': 4,   'mkr': 's', 'clr': 'blue',    'off': 20},
    {'name': '8PSK',   'cat': 'psk', 'M': 8,   'mkr': '^', 'clr': 'skyblue', 'off': 40},
    {'name': '16PSK',  'cat': 'psk', 'M': 16,  'mkr': 'v', 'clr': 'cyan',    'off': 60},
    {'name': '32PSK',  'cat': 'psk', 'M': 32,  'mkr': '<', 'clr': 'teal',    'off': 80},
    {'name': 'DBPSK',  'cat': 'dpsk','M': 2,   'mkr': '*', 'clr': 'orange',  'off': 10},
    {'name': 'DQPSK',  'cat': 'dpsk','M': 4,   'mkr': 'p', 'clr': 'red',     'off': 30},
    {'name': '4QAM',   'cat': 'qam', 'M': 4,   'mkr': 'h', 'clr': 'magenta', 'off': 50},
    {'name': '16QAM',  'cat': 'qam', 'M': 16,  'mkr': 'D', 'clr': 'green',   'off': 70},
    {'name': '64QAM',  'cat': 'qam', 'M': 64,  'mkr': 'P', 'clr': 'olive',   'off': 90},
    {'name': '256QAM', 'cat': 'qam', 'M': 256, 'mkr': 'X', 'clr': 'black',   'off': 110},
]

# ================= 3. 绘图 =================
plt.figure(figsize=(12, 9))

for mod in mod_list:
    M = mod['M']
    k = np.log2(M)
    if mod['cat'] == 'psk':
        ber = Q(np.sqrt(2 * ebn0_lin)) if M <= 4 else (2/k) * Q(np.sqrt(2 * k * ebn0_lin) * np.sin(np.pi/M))
    elif mod['cat'] == 'qam':
        ber = (4/k) * (1 - 1/np.sqrt(M)) * Q(np.sqrt(3*k / (M-1) * ebn0_lin))
    elif mod['cat'] == 'dpsk':
        ber = 0.5 * np.exp(-ebn0_lin) if M == 2 else Q(np.sqrt(ebn0_lin * k * (2 - np.sqrt(2))))

    plt.plot(ebn0_db, ber, label=mod['name'], color=mod['clr'], 
             marker=mod['mkr'], markevery=(mod['off'], 80), 
             markersize=6, linewidth=1.2, markerfacecolor='none')

# ================= 4. 美化图表 (修正版) =================
# 必须先设置对数坐标
plt.yscale('log')

ax = plt.gca()

# X 轴精细化：每 1dB 一个主线，0.5dB 一个次线
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))

# Y 轴精细化：设置对数轴的次刻度 (2,3,4,5,6,7,8,9)
# numticks 设置得足够大，防止刻度在高动态范围下消失
ax.yaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=15))
ax.yaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=15))

# 绘制网格
# major: 实线，颜色深
ax.grid(which='major', linestyle='-', linewidth=0.7, color='gray', alpha=0.5)
# minor: 虚线，颜色浅但可见
ax.grid(which='minor', linestyle=':', linewidth=0.5, color='gray', alpha=0.3)

# 强制开启次刻度显示（某些版本默认不显示对数轴次刻度网格）
ax.tick_params(which='both', width=1)
ax.tick_params(which='minor', length=4)

plt.ylim(1e-10, 1)
plt.xlim(-4, 26)
plt.xlabel('$E_b/N_0$ (dB)', fontsize=12)
plt.ylabel('Estimated BER', fontsize=12)
plt.title('BER Waterfall Curves (High-Density Grid)', fontsize=14)

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()
