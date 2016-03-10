# wechannel
一个tornado练手小项目。初步做成微信公众号文章聚合阅读，聚合一些财经，技术，段子等公众号，提供简单的导航。[微阅读](http://weiyuedu.me)
step:

1. pip install -r requirements.txt
2. install mongodb and redis.
3. cp config/config.py.example config.py; modify your own config.
4. run spider: python iwgc.py; python crawler/sougou_wechat/sougou.py 微信公众号名称
5. ./run.sh
