#!/usr/bin/env python
# -*- coding:utf-8 -*-


from tornado.gen import coroutine
from tornado.web import url
from tornado.util import ObjectDict
from six.moves.urllib.parse import urljoin
import _env
from .base import BaseHandler
from config.config import CONFIG
from lib.date_util import datestr_from_stamp
from lib.json_tools import bson_to_json


class IndexHandler(BaseHandler):
    @property
    def _db(self):
        return self.application._motor.wechat_post

    def page_url(self, page_str):
        query_string = self.request.query
        request_url = self.request.full_url().rsplit('/page')[0]
        url = urljoin(request_url, '/page/' + page_str)
        if query_string:
            return url + '?' + query_string
        else:
            return url

    @coroutine
    def get(self, page=None):
        nick_name = self.get_query_argument('nick_name', None)
        try:
            page = max(1, int(page)) if page else 1
        except TypeError:
            page = 1
        posts_per_page = CONFIG.SITE.POSTS_PER_PAGE
        if nick_name is not None:
            cursor = self._db.find({'nick_name': nick_name})
        else:
            cursor = self._db.find()
        cnt = yield cursor.count()
        pages = max(1, int(cnt / posts_per_page))
        page = min(page, pages) if page >= 1 else 1
        posts = []
        pre_url = 'http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl='

        cursor.sort([('ori_create_time', -1)]).limit(posts_per_page).skip(
            (page-1)*posts_per_page)
        for doc in (yield cursor.to_list(length=posts_per_page)):
            post = bson_to_json(doc)
            post['image'] = pre_url + post['cdn_url']
            post['date'] = datestr_from_stamp(post['ori_create_time'],
                                              '%Y-%m-%d')
            posts.append(ObjectDict(post))

        prev_url = None if page == 1 else self.page_url(str(page-1))
        next_url = None if page >= pages else self.page_url(str(page+1))
        self.render('index.html', posts=posts, page=page, pages=pages,
                    prev_url=prev_url, next_url=next_url)


URL_ROUTES = [
    url(r'/', IndexHandler),
    url(r'/page/(\d*)/?', IndexHandler),
]
