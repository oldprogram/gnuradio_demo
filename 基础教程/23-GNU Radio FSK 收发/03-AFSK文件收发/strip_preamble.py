#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Title: strip_preamble
# Author: Barry Duggan

"""
Strip preamble and trailer packets from input file.
Then convert Base64 to original input.
"""

import os.path
import sys
import base64

_debug = 0          # set to zero to turn off diagnostics
state = 0
Pkt_len = 52

if (len(sys.argv) < 3):
    print ('Usage: python3 strip_preamble.py <input file> <output file>')
    print ('Number of arguments=', len(sys.argv))
    print ('Argument List:', str(sys.argv))
    exit (1)
# test if input file exists
fn = sys.argv[1]
if not(os.path.exists(fn)):
    print(fn, 'does not exist')
    exit (1)
# open input file
f_in = open (fn, 'rb')

# open output file
f_out = open (sys.argv[2], 'wb')

while True:
    if (state == 0):
        buff = f_in.read (Pkt_len)
        b_len = len(buff)
        if ((buff[0] == 37) and (buff[51] == 93)):
            continue
        else:
            # decode Base64
            data = base64.b64decode(buff)
            f_out.write (data)
            if (_debug):
                print ("End of preamble")
            state = 1
            continue
    elif (state == 1):
        buff = f_in.read(4)
        b_len = len(buff)
        if b_len == 0:
            print ('End of file')
            break
        if (buff[0] == 37):     # '%'
            if (buff == b'%UUU'):
                print ("End of text")
                buff = f_in.read(4)     # skip next four 'U's
                rcv_fn = []
                i = 0
                while (i < 44):
                    ch = f_in.read(1)
                    if (ch == b'%'):
                        break
                    rcv_fn.append((ord)(ch))
                    i += 1
                rf_len = len (rcv_fn)
                x = 0
                while (x < rf_len):
                    rcv_fn[x] = str((chr)(rcv_fn[x]))
                    x += 1
                ofn = "".join(rcv_fn)
                print ("Transmitted file name:",ofn)
                state = 2
                break
        else:
            # decode Base64
            data = base64.b64decode(buff)
            f_out.write (data)
            continue

f_in.close()
f_out.close()

