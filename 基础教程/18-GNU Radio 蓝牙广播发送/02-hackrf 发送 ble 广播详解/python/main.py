#!/usr/bin/env python
# coding=utf-8
import numpy as np
import struct

from bsp_algorithm import bsp_algorithm
from bsp_string import bsp_string
from bsp_signal import bsp_signal


def gen_sample_from_phy_bit(bit):
    # Constants
    MAX_NUM_PHY_BYTE = 47
    SAMPLE_PER_SYMBOL = 4
    LEN_GAUSS_FILTER = 4
    MAX_NUM_PHY_SAMPLE = ((MAX_NUM_PHY_BYTE*8*SAMPLE_PER_SYMBOL)+(LEN_GAUSS_FILTER*SAMPLE_PER_SYMBOL)) 


    # 1、tmp_phy_bit_over_sampling 是前塞 15 个0，中间对每 bit 数据后面插入 3 个0，同时对于原来数据是 0 的变为 -1，为 1 的变为 1
    num_bit = len(bit)
    tmp_phy_bit_over_sampling = [0]*((num_bit * SAMPLE_PER_SYMBOL) + 2*LEN_GAUSS_FILTER*SAMPLE_PER_SYMBOL);

    for i in range(num_bit * SAMPLE_PER_SYMBOL):
        if i % SAMPLE_PER_SYMBOL == 0:
            tmp_phy_bit_over_sampling[i + LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 1] = (bit[i // SAMPLE_PER_SYMBOL]) * 2 - 1
        else:
            tmp_phy_bit_over_sampling[i + LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 1] = 0

    # bsp_string.print_data_list_hex("> tmp_phy_bit_over_sampling is:", tmp_phy_bit_over_sampling)

    # 2、sample 是高斯滤波器 + IQ 调制（数据量是
    num_sample = (num_bit * SAMPLE_PER_SYMBOL) + (LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL)
    sample = [0,0] * num_sample  # 初始化 sample 列表
    cos_table_int8, sin_table_int8 = bsp_signal.sample_cosine_and_sine()
    gauss_coef_int8 = [0, 0, 0, 0, 2, 11, 32, 53, 60, 53, 32, 11, 2, 0, 0, 0]

    tmp = 0
    sample[0] = cos_table_int8[tmp]
    sample[1] = sin_table_int8[tmp]

    for i in range(num_sample - 1):
        acc = 0
        for j in range(3, LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - 4):
            acc += gauss_coef_int8[LEN_GAUSS_FILTER * SAMPLE_PER_SYMBOL - j - 1] * tmp_phy_bit_over_sampling[i + j]

        tmp = (tmp + acc) & 1023
        sample[(i + 1) * 2] = cos_table_int8[tmp]
        sample[(i + 1) * 2 + 1] = sin_table_int8[tmp]

    return sample

def create_ll_payload(mac, adv_data, channel):
    '''
    AA D6 BE 89 8E （preamble + access address)
    42 26 06 05 04 03 02 01  (PDU-Header + PDU-Payload-Adva)
    19 09 53 44 52 2F 42 6C 75 65 74 6F 6F 74 68 2F 4C 6F 77 2F 45 6E 65 72 67 79 (PDU-Payload-AdvData)
    E8 7D 36 (CRC)
    '''

    ll_payload = [0xAA,0xD6,0xBE,0x89,0x8E] #  preamble + access address
                                            #  PDU-Header        
    '''                                     
    0x42 0x26 --> 0x2642 -> 0010 0110 0100 0010
                         ->                0010 PDU-Type（ADV_NONCONN_IND）
                         ->           ..00 RFU 保留
                         ->           .1.. TxAdd
                         ->           0... RxAdd
                         -> ..10 0110 Length(这个是 PDU Payload 长度)
                         -> 00.. RFU
    '''
    # 组装广播 PDU
    pdu_adv = []
    pdu_adv.extend([0x42, (len(adv_data)+6) & 0xFF])    # PDU-Header
    pdu_adv.extend(reversed(mac))                       # PDU-Payload-Adva(实际 MAC 的的反转)
    pdu_adv.extend(adv_data)                            # PDU-Payload-AdvData

    # 生成 CRC(基于PDU)
    crc = bsp_algorithm.bt_crc(pdu_adv, len(pdu_adv))    # CRC 只对 PDU 进行
    
    # 加白(基于PDU+CRC)
    pdu_adv_crc = pdu_adv + crc
    pdu_adv_crc_wt = bsp_algorithm.bt_dewhitening(pdu_adv_crc,channel)

    # 最终组装
    ll_payload.extend(pdu_adv_crc_wt)

    # 打印
    bsp_string.print_data_list_hex("> pre_wt_adv_pdu:", pdu_adv)
    bsp_string.print_data_list_hex("\n> ll data final:", ll_payload)


    return ll_payload

# 示例输入
mac = [1,2,3,4,5,6]
#adv_name = "btfz's gnu-radio course"
adv_name = "hello btfz's gnu-radio"
adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
channel = 37
ll_datas = create_ll_payload(mac, adv_datas, channel)

# bit 是广播包 42 Bytes 的 bits 表示（小端）
ll_datas_bit = bsp_string.bytes_to_bits_lsb(ll_datas)
bsp_string.print_data_list_hex("\n> ll_datas_bit =",ll_datas_bit,line_item_num=40,seg_item_num=4)
# ll_datas = bsp_string.bits_to_bytes_lsb(ll_datas_bit)
# bsp_string.print_data_list_hex("\n> ll_datas =",ll_datas)

ll_datas_sample = gen_sample_from_phy_bit(ll_datas_bit)
# bsp_string.print_data_list("\n> ll_datas_sample(IQ datas)",ll_datas_sample,line_item_num=40)
bsp_string.print_data_list_hex("\n> ll_datas_sample(IQ datas)", ll_datas_sample, line_item_num=40, seg_item_num=4)

ll_datas_normalization_sample = np.divide(ll_datas_sample, 256)

with open("normalization_sample.bin", "wb") as f:
    for data in ll_datas_normalization_sample:
        f.write(struct.pack("f", data))  # 将浮点数打包成4字节的二进制数据
