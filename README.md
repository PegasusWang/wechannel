# wechannel
一个tornado练手小项目。初步做成微信公众号文章聚合阅读，聚合一些财经，技术，段子等公众号，提供简单的导航。
# [微阅读](http://weiyuedu.me)

# 使用步骤
前端:

```
cd themes
npm install
gulp # 监控前端项目
```

后端:

1. pip install -r requirements.txt
2. install mongodb and redis.
3. cp config/config.py.example config.py; modify your own config.
4. run spider: python iwgc.py; python crawler/sougou_wechat/sg.py
5. ./run.sh


访问:

http://127.0.0.1:3000/,需要的话在gulpfile修改
