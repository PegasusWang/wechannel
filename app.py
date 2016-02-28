#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lib import _db
from lib._db import get_db
from config.config import CONFIG
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.options import options, define
from urls import url_patterns
from motorengine.connection import connect
from settings import settings

#define("port", default=8888, help="run on the given port", type=int)



class ArticlesApp(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)
        self._redis = _db.redis_client
        self._motor = get_db(CONFIG.MONGO.DATABASE, client='motor')
        connect(CONFIG.MONGO.DATABASE, host=CONFIG.MONGO.HOST,
                port=CONFIG.MONGO.PORT,
                io_loop=tornado.ioloop.IOLoop.current())    # motorengine


def main():
    tornado.options.parse_command_line()
    app = ArticlesApp()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
