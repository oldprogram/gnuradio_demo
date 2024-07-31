#!/usr/bin/env python
# coding=utf-8
import struct

class bsp_string:
    # from ieee754 import IEEE754
    # 将浮点数以4个字节的方式表示，通常使用 IEEE 754 标准的二进制编码。这种编码将浮点数分为三部分：符号位、指数位和尾数位。
    # 可以使用 struct 进行转换
    @staticmethod
    def float_to_hex(f):
        return hex(struct.unpack('<I', struct.pack('<f', f))[0])

    @staticmethod
    def int8_to_uint8(x):
        if x < 0:
            return (x+(1 << 32)) & 0xFF
        return x

    # 打印 datas list 数据，每隔 line_item_num 换一行，每隔 seg_item_num 多一个空格
    # 打印大量数据时建议 line_item_num = 40, seg_item_num = 4
    @staticmethod
    def print_data_list_hex(title, datas, line_item_num=0xffffffff, seg_item_num=0xffffffff):
        print(title, f"[total_length: {len(datas)}]")

        idx = 1
        for x in datas:
            x = bsp_string.int8_to_uint8(x)
            
            if idx % line_item_num == 0:
                print("%02X" %(x))
            else:
                if idx % seg_item_num == 0:
                    print("%02X" %(x),end="  ")
                else:
                    print("%02X" %(x),end=" ")
            idx += 1
        print("")

    @staticmethod
    def print_data_list(title, datas, line_item_num=0xffffffff):
        print(title, f"[total_length: {len(datas)}]")
        # 自动计算最大的数字占多少位（负数会自动计算），然后后面对齐
        max_data = max(datas)
        min_data = min(datas)
        digits_num = max(len(str(max_data)),len(str(min_data)))

        idx = 1
        for x in datas:
            if idx%line_item_num==0:
                print(f"{x:>{digits_num}}")
            else:
                print(f"{x:>{digits_num}}",end=" ")
            idx += 1
        print("")

    # 小端 bit_list 转 byte_list 
    @staticmethod
    def bits_to_bytes_lsb(bit_list):
        byte_list = bytearray()   
        idx = 0
        tmp = 0
        for value in bit_list:
            tmp += (value<<idx)
            idx+=1
            if idx % 8 == 0:
                byte_list.append(tmp)
                idx = 0
                tmp = 0

        return bytes(byte_list)

    # 小端 byte_list 转 bit_list
    @staticmethod
    def bytes_to_bits_lsb(byte_list):
        bit_list = bytearray()
        for value in byte_list:
            for i in range(8):
                # 使用右移运算符将每一位的值提取出来
                bit_value = (value >> i) & 1
                # 将每一位的值添加到结果字节列表中
                bit_list.append(bit_value)
        return bytes(bit_list)


