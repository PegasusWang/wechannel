#!/usr/bin/env python
# -*- coding:utf-8 -*-


import _env
from .base import BaseHandler
from lib.date_util import datestr_from_stamp
from lib.json_tools import bson_to_json
from tornado.gen import coroutine
from tornado.web import url
from tornado.util import ObjectDict


class IndexHandler(BaseHandler):
    @property
    def _db(self):
        return self.application._motor.wechat_post

    @coroutine
    def get(self, page=1):
        posts = []
        pre_url = 'http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl='
        cursor = self._db.find().sort('ori_create_time', -1)
        for doc in (yield cursor.to_list(length=18)):
            post = bson_to_json(doc)
            post['image'] = pre_url+post['cdn_url']
            post['date'] = datestr_from_stamp(post['ori_create_time'],
                                              '%Y-%m-%d')
            posts.append(ObjectDict(post))
        self.render('index.html', posts=posts)


URL_ROUTES = [
    url(r'/', IndexHandler),
]
