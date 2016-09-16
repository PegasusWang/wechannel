#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""防盗链测试"""

from requests import get


url = 'http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=http://mmbiz.qpic.cn/mmbiz/zYJiboYpSP4dxQ9bUDia7tXvc5xwAtibkff3wSPicGwdWAM1z9j8G5ajohicO5b46ePmv3ibxqRpnp7KfQtvKAR6zQlg/0?wx_fmt=jpeg'


def test_my():
    #  H = {'Referer': 'http://wechannel.io/'}
    H = {'Referer': 'http://104.238.149.32/'}
    r = get(url, headers=H)
    with open('my.jpeg', 'wb') as f:
        f.write(r.content)



def test_men():
    H = {'Referer': 'http://chuansong.me:8888/'}
    r = get(url, headers=H)
    with open('men.jpeg', 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    test_my()
    test_men()
