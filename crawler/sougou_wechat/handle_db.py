#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
from config.config import CONFIG
from lib._db import get_mongodb
db = get_mongodb(CONFIG.MONGO.DATABASE, client='mongo')


def remove_duplicate_article():
    col_name = 'wechat_post'
    col = getattr(db, col_name)
    title_set = set()
    for doc in col.find(fileds=['title']):
        title = doc['title']
        print(title)
        if title not in title_set:
            title_set.add(title)
        else:
            print('remove title: %s', title)
            col.remove(doc['_id'])


if __name__ == '__main__':
    remove_duplicate_article()
