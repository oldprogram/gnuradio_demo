#!/bin/bash

meld <(hexdump -C $1) <(hexdump -C $2)


