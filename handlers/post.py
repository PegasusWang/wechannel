#!/usr/bin/env python
# -*- coding:utf-8 -*-


from tornado.gen import coroutine
from tornado.web import url
from cerberus import Validator
from six.moves.urllib.parse import urljoin
import _env
from .base import BaseHandler
from config.config import CONFIG
from model.post import WechatPost


class Pagination(object):
    def __init__(self, request, page, cnt, limit=CONFIG.SITE.POSTS_PER_PAGE):
        if not self._validate_page(page):
            page = 1
        self.request = request    # RequestHanler().request
        self.cnt = cnt    # all nums
        self.pages = max(1, int(cnt/limit))
        self.page = min(page, self.pages) if page >= 1 else 1

    def _validate_page(self, page):
        schema = {'page': {'type': 'integer', 'min': 1}}
        v = Validator(schema)
        return v.validate({'page': page})

    def page_url(self, page):
        query_string = self.request.query    # query string
        request_url = self.request.full_url().rsplit('/page')[0]
        if not request_url.endswith('/'):
            request_url += '/'
        url = urljoin(request_url, 'page/' + str(page))
        if query_string:
            return url + '?' + query_string
        else:
            return url

    @property
    def prev_url(self):
        return None if self.page == 1 else self.page_url(self.page-1)

    @property
    def next_url(self):
        return None if self.page >= self.pages else self.page_url(self.page+1)


class IndexHandler(BaseHandler):

    @coroutine
    def get(self, page=1):
        nick_name = self.get_query_argument('nick_name', None)
        limit = CONFIG.SITE.POSTS_PER_PAGE
        if nick_name is not None:
            condition = {'nick_name': nick_name}
        else:
            condition = {}
        cnt = yield WechatPost.count(condition)
        order_by = [('ori_create_time', -1)]
        skip = (int(page)-1) * limit
        posts = yield WechatPost.query(condition, order_by, limit, skip)
        p = Pagination(self.request, page, cnt, CONFIG.SITE.POSTS_PER_PAGE)

        self.render('index.html',
                    nick_name=nick_name,
                    posts=posts, page=p.page, pages=p.pages,
                    prev_url=p.prev_url, next_url=p.next_url,
                    site=CONFIG.SITE)


class TagHandler(BaseHandler):
    @coroutine
    def get(self, tag_id=16, page=1):
        limit = CONFIG.SITE.POSTS_PER_PAGE
        condition = {'tag_id': int(tag_id)}
        cnt = yield WechatPost.count(condition)
        order_by = [('ori_create_time', -1)]
        skip = (int(page)-1) * limit
        posts = yield WechatPost.query(condition, order_by, limit, skip)
        p = Pagination(self.request, page, cnt, CONFIG.SITE.POSTS_PER_PAGE)

        self.render('index.html',
                    posts=posts, page=p.page, pages=p.pages,
                    prev_url=p.prev_url, next_url=p.next_url,
                    site=CONFIG.SITE)


URL_ROUTES = [
    url(r'/', IndexHandler),
    url(r'/page/(\d*)/?', IndexHandler),
    url(r'/tag/(\d+)/?', TagHandler),
    url(r'/tag/(\d+)/page/(\d*)/?', TagHandler),
]
