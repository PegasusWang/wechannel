#!/usr/bin/env python
# -*- coding:utf-8 -*-

from handlers import (
    base, post, user
)
from rest import (
    articles_rest, news_rest
)
from tornado.web import url

# collect all url routes from rest module
url_patterns = []

for module in [post, user]:
    url_patterns.extend(getattr(module, 'URL_ROUTES'))

for module in [articles_rest, news_rest]:
    url_patterns.extend(getattr(module, 'URL_ROUTES'))

url_patterns.append(url(r'.*', base.PageNotFoundHandler))    # catch return 404
