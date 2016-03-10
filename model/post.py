#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import traceback
from tornado.gen import coroutine, Return
from tornado.util import ObjectDict
from config.config import CONFIG
from lib._db import get_collection
from lib.json_tools import bson_to_json
from lib.date_util import datestr_from_stamp


class WechatPost(object):
    col_name = 'wechat_post'
    col = get_collection(CONFIG.MONGO.DATABASE, col_name, 'motor')

    @classmethod
    @coroutine
    def query(cls, condition={}, order_by=None, limit=None, skip=None):
        try:
            cursor = cls.col.find(condition)
            if order_by:
                cursor.sort(order_by)
            if limit:
                cursor.limit(limit)
            if skip:
                cursor.skip(skip)

            pre_url = 'http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl='
            posts = []
            for doc in (yield cursor.to_list(length=limit)):
                post = bson_to_json(doc)
                post['image'] = pre_url + post['cdn_url']
                post['date'] = datestr_from_stamp(post['ori_create_time'],
                                                  '%Y-%m-%d')
                posts.append(ObjectDict(post))
            raise Return(posts)
        except ValueError:
            traceback.print_exc()
            raise Return([])


    @classmethod
    @coroutine
    def count(cls, condition={}):
        cnt = yield cls.col.find(condition).count()
        raise Return(cnt)
