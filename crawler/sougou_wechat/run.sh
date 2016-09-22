#!/usr/bin/env bash

PREFIX=$(cd "$(dirname "$0")"; pwd)
cd $PREFIX
source ~/.bashrc

python -u sg.py    # -u 参数强制刷新输出
date
