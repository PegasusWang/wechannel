#!/usr/bin/env python
# -*- coding:utf-8 -*-


from .base import BaseHandler
from tornado.web import url


class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')
        #self.render('default.html')


URL_ROUTES = [
    url(r'/', IndexHandler),
]
