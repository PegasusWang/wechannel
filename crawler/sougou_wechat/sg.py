#!/usr/bin/env python
# -*- coding:utf-8 -*-

import _env
import ast
import json
import logging
import pprint
import random
import re
import sys
import time
import traceback
import requests

import six.moves.urllib.parse as urlparse   # for py2 and py3 use six
from six.moves.urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from single_process import single_process
from tornado.escape import xhtml_unescape

from config.config import CONFIG
from extract import extract
from iwgc import name_list, tagid_by_name
from lib._db import get_mongodb
from lib._db import redis_client as _redis
from lib.date_util import datestr_from_stamp, days_from_now
from lib.redis_tools import gid
from ua import random_ua
from web_util import get, parse_curl_str, change_ip

"""搜狗微信爬虫，先根据公众号名字拿到列表页，如果第一个匹配就转到第一个搜索结果
的页面, 再遍历每个公众号的文章列表页面。需要定期更新cookies。
"""


class DocumentExistsException(Exception):
    pass


class DocumentExpireException(Exception):
    """用来控制超过一定天数后就跳过"""
    pass


def logged(class_):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format='Line:%(lineno)s- %(message)s')
    class_.logger = logging.getLogger(class_.__name__)
    return class_


@logged
class SougouWechat:
    db = get_mongodb(CONFIG.MONGO.DATABASE, client='mongo')
    headers = None
    curl_str = """
    curl 'http://weixin.sogou.com/gzhjs?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&ext=&cb=sogou.weixin_gzhcb&page=13&gzhArtKeyWord=&tsn=0&t=1455693188126&_=1455692977408' -H 'Cookie: SUV=00A27B2BB73D015554D9EC5137A6D159; ssuid=6215908745; SUID=2E0D8FDB66CA0D0A0000000055323CAB; usid=g6pDWznVhdOwAWDb; CXID=9621B02E3A96A6AB3F34DB9257660015; SMYUV=1448346711521049; _ga=GA1.2.1632917054.1453002662; ABTEST=8|1455514045|v1; weixinIndexVisited=1; ad=G7iNtZllll2QZQvQlllllVbxBJtlllllNsFMpkllllUlllllRTDll5@@@@@@@@@@; SNUID=C1B8F6463A3F10F2A42630AD3BA7E3E1; ppinf=5|1455520623|1456730223|Y2xpZW50aWQ6NDoyMDE3fGNydDoxMDoxNDU1NTIwNjIzfHJlZm5pY2s6NzpQZWdhc3VzfHRydXN0OjE6MXx1c2VyaWQ6NDQ6NENDQTE0NDVEMTg4OTRCMTY1MUEwMENDQUNEMEQxNThAcXEuc29odS5jb218dW5pcW5hbWU6NzpQZWdhc3VzfA; pprdig=Xmd5TMLPOARs3V2jIAZo-5UJDINIE0oFY97uU510_JOZm2-uu5TnST5KKW3oDgJY6-xd66wDhsb4Nm8wbOh1FCPohYO12b1kCrFoe-WUPrvg9JSqC72rjagjOlDg-JX72LcIjFOhsj7l_YGuaJpDrjFPoqy39C0AReCpmVcI5SM; PHPSESSID=e8vhf5d36raupjdb73k1rp7le5; SUIR=C1B8F6463A3F10F2A42630AD3BA7E3E1; sct=21; ppmdig=145569047300000087b07d5762b93c817f4868607c9ba98c; LSTMV=769%2C99; LCLKINT=47772; IPLOC=CN2200' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36' -H 'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01' -H 'Referer: http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=lA5I5al3X8DLRO7Ypz8g44dD75TkiekfFoGEDMmpUgIjEtQirDGcaSXT-vwsAyxo' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --compressed
    """

    def __init__(self, wechat_name, tag_id, limit=CONFIG.CRAWLER.LIMIT,
                 col_name='wechat_post',
                 media_col_name="wechat_media"):
        self.col = getattr(self.db, col_name)
        self.media_col = getattr(self.db, media_col_name)
        self.name = wechat_name    # 微信公众号名称
        self.tag_id = tag_id
        self.limit = limit
        self.key = '_'.join([self.__class__.__name__, self.name]).upper()
        if self.headers is None:
            self.update_headers()

    @property
    def page(self):
        _page = _redis.get(self.key)
        return int(_page) if _page else 1

    @page.setter
    def page(self, page):
        _redis.set(self.key, page)

    @staticmethod
    def getSUV():
        """模拟js代码生成suv"""
        return "SUV=" + quote(
            str(int(time.time()*1000)*1000 + round(random.random()*1000))
        )

    @classmethod
    def get_headers(cls):
        url, headers, data = parse_curl_str(cls.curl_str)
        del headers['Cookie']
        return headers

    @classmethod
    def get_cookie_str(cls):
        """生成一个搜狗微信的cookie并返回
        """
        while True:
            time.sleep(5)
            url = 'http://weixin.sogou.com/weixin?query=%s' % \
                random.choice('abcdefghijklmnopqrstuvwxyz')

            # 获取SNUID
            cookie = get(url, headers=cls.get_headers())
            headers = cookie.headers
            try:
                cookie_str = headers.get('Set-Cookie') + '; ' + \
                    SougouWechat.getSUV()
            except Exception:
                cookie_str = None

            cls.logger.info('cookie_str: %s' % cookie_str)
            # 跳过没有设置SNUID的
            if cookie_str and 'SUID' in cookie_str and 'SNUID' in cookie_str:
                return cookie_str

    @classmethod
    def update_headers(cls):
        cls.logger.info('*********updating cookies*********')
        _, headers, _ = parse_curl_str(cls.curl_str)
        headers['Cookie'] = cls.get_cookie_str()
        if headers['Cookie'] is None:
            change_ip()
            cls.update_headers()
        else:
            cls.headers = headers

    def search(self, retries=3):
        """搜索搜狗微信公众号并返回公众号文章列表页面,返回列表格式如下
        http://weixin.sogou.com/gzh?openid=oIWsFt2uCBiQ3mWa2BSUtmdKD3gs&amp;ext=p8lVKENENbkGdvuPNCqHoUqzuLEPtZheP6oyzp3YVsY_-OJEvXMz4yk2nJytyUxY
        """
        query_url = 'http://weixin.sogou.com/weixin?type=1&' + urlencode({'query': self.name})
        self.logger.info('query_url: %s', query_url)

        while retries > 0:
            self.logger.info('retry search %s %d' % (self.name, retries))
            html = get(query_url, headers=self.headers).text
            soup = BeautifulSoup(html)
            a_tag_list = soup.find_all(attrs={'uigs': re.compile('account_name')})
            href = None
            try:
                for a_tag in a_tag_list:
                    if a_tag and a_tag.text.lower() == self.name.lower():
                        href = a_tag.get('href')
                        break
            except Exception:
                self.logger.info('found %s failed' % self.name)
                continue

            if href is not None:
                break
            else:
                self.update_headers()
                time.sleep(5)
            retries -= 1

        res = href or None
        return res

    def _get_articel_info(self, article_info, nick_name, ori_create_time):
        for k, v in article_info.items():
            if isinstance(v, str):
                article_info[k] = xhtml_unescape(v)
        article_dict = {
            'cdn_url': article_info['cover'].replace('\\', ''),
            'title': article_info['title'],
            'nick_name': nick_name,
            'link': ('http://mp.weixin.qq.com' +
                     article_info['content_url'].replace('\\', '')),
            'ori_create_time': ori_create_time,
            'desc': article_info['digest'],
        }
        return article_dict

    def fetch_channel_json(self, channel_json_url):
        time.sleep(random.randint(60, 120))
        self.logger.info(channel_json_url)
        res = get(channel_json_url, headers=self.headers)
        # http://stackoverflow.com/questions/24027589/how-to-convert-raw-javascript-object-to-python-dictionary
        html = res.text.strip()
        o = ast.literal_eval(html)
        if not o:
            self.logger.debug(pprint.pformat(html))
            self.logger.info(
                'fetch channel_json_url: %s failed', channel_json_url
            )
            change_ip()
            return
        nick_name = o['nick_name']
        general_msg_list = o['general_msg_list']
        article_list = ast.literal_eval(general_msg_list)['list']
        article_dict_list = []
        for article in article_list:
            app_msg_ext_info = article['app_msg_ext_info']
            comm_msg_info = article['comm_msg_info']
            ori_create_time = comm_msg_info['datetime']

            article_dict_list.append(
                self._get_articel_info(
                    app_msg_ext_info, nick_name, ori_create_time
                )
            )
            if app_msg_ext_info['is_multi']:
                for article_info in app_msg_ext_info['multi_app_msg_item_list']:
                    article_dict_list.append(
                        self._get_articel_info(
                            article_info, nick_name, ori_create_time
                        )
                    )

        article_dict_list = self.get_remove_too_old_days_article(article_dict_list)
        article_dict_list = self.get_remove_mongodb_already_has_article(nick_name, article_dict_list)

        self.logger.info(pprint.pformat(article_dict_list))
        self.save_article_dict_list(nick_name, article_dict_list)

    def get_remove_too_old_days_article(self, article_dict_list, expire_days=15):
        res = []
        for article_dict in article_dict_list:
            if days_from_now(article_dict['ori_create_time']) > expire_days:
                self.logger.info(
                    '%s跳过%d天前文章 title : %s\n', self.name,
                    expire_days, article_dict['title']
                )
            else:
                res.append(article_dict)
        return res

    def get_remove_mongodb_already_has_article(self, nick_name, article_dict_list):
        res = []
        for article_dict in article_dict_list:
            if self.col.find_one(
                dict(title=article_dict['title'])
            ):
                self.logger.info(
                    '%s 已存在title : %s\n', self.name, article_dict['title']
                )
            else:
                res.append(article_dict)
        return res

    def save_article_dict_list(self, nick_name, article_dict_list):
        # 先删除超过限制数量的文章
        if self.col.find(dict(nick_name=self.name)).count() > self.limit:
            oldest_doc = list(self.col.find(dict(nick_name=self.name)).
                              sort([('ori_create_time', 1)]).limit(1))[0]
            oldest_doc_id = oldest_doc.get('_id')
            self.col.remove({'_id': oldest_doc_id})
            self.logger.info(
                "%s:删除:%s : %s\n" %
                (
                    self.name,
                    oldest_doc.get('title'),
                    datestr_from_stamp(
                        oldest_doc.get('ori_create_time'), '%Y-%m-%d'
                    )
                )
            )
        for o in article_dict_list:
            if o['title']:
                o_date = datestr_from_stamp(
                    o.get('ori_create_time'), '%Y-%m-%d'
                )
                self.logger.info(
                    '%s-保存文章 title : %s %s\n', self.name, o['title'], o_date
                )

                o['tag_id'] = self.tag_id
                self.col.update({'_id': gid()}, {'$set': o}, True)

    def fetch(self, update=False):
        url = self.search()
        if url:
            json_url = url + '&f=json'
            self.fetch_channel_json(json_url)
        else:
            self.logger.info('抓取结束或找不到微信号 %s\n' % self.name)
        self.logger.info('抓取结束 %s\n' % self.name)

    def update(self):
        self.fetch(update=True)


def fetch(name):
    if name:
        tagid = tagid_by_name(name.strip())
        if tagid:
            print("tag_id: %d" % tagid)
            s = SougouWechat(name, tag_id=tagid, limit=CONFIG.CRAWLER.LIMIT)
            s.fetch()


def fetch_all(_id=1, li_name="name_list", update=False):
    name_li = name_list(_id, li_name)
    name_li.sort()
    for index, name in enumerate(name_li):
        s = SougouWechat(name, tag_id=_id, limit=CONFIG.CRAWLER.LIMIT)
        if update:
            s.update()
        else:
            s.fetch()
        print('剩余%d个微信号待抓取' % (len(name_li)-index-1))


@single_process
def main():
    try:
        name = sys.argv[1]
    except IndexError:
        # to_fetch_id = list(range(16, 22))
        to_fetch_id = [22]
        random.shuffle(to_fetch_id)
        for _id in to_fetch_id:
            fetch_all(_id, 'need_name_list')
        return

    fetch(name.strip())

if __name__ == '__main__':
    main()
