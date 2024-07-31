#!/usr/bin/env python
# coding=utf-8

class bsp_algorithm:
    @staticmethod
    def bt_swap_bits(value):
        return (value * 0x0202020202 & 0x010884422010) % 1023

    # (De)Whiten data based on BLE channel
    @staticmethod
    def bt_dewhitening(data, channel):
        ret = []
        lfsr = bsp_algorithm.bt_swap_bits(channel) | 2

        for d in data:
            d = bsp_algorithm.bt_swap_bits(d)
            for i in 128, 64, 32, 16, 8, 4, 2, 1:
                if lfsr & 0x80:
                    lfsr ^= 0x11
                    d ^= i

                lfsr <<= 1
                i >>= 1
            ret.append(bsp_algorithm.bt_swap_bits(d))

        return ret

    # 24-bit CRC function
    @staticmethod
    def bt_crc(data, length, init=0x555555):
        ret = [(init >> 16) & 0xff, (init >> 8) & 0xff, init & 0xff]

        for d in data[:length]:
            for v in range(8):
                t = (ret[0] >> 7) & 1

                ret[0] <<= 1
                if ret[1] & 0x80:
                    ret[0] |= 1

                ret[1] <<= 1
                if ret[2] & 0x80:
                    ret[1] |= 1

                ret[2] <<= 1

                if d & 1 != t:
                    ret[2] ^= 0x5b
                    ret[1] ^= 0x06

                d >>= 1

        ret[0] = bsp_algorithm.bt_swap_bits((ret[0] & 0xFF))
        ret[1] = bsp_algorithm.bt_swap_bits((ret[1] & 0xFF))
        ret[2] = bsp_algorithm.bt_swap_bits((ret[2] & 0xFF))

        return ret

