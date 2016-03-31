# -*- coding:utf-8 -*-

"""
use py.test for test:
py.test -q test_model_user.py
"""

import pytest
from tornado.ioloop import IOLoop
from tornado.testing import gen_test, AsyncTestCase
from model.user import User
from wtforms import ValidationError


class TestModelUser(AsyncTestCase):

    def setUp(self):
        self.io_loop = IOLoop.current()

    @gen_test
    def test_insert(self):
        d = dict(email="t@qq.com", password="1234", password2="1234")
        yield User.insert(**d)
        user = yield User.col.find_one({'email': d['email']})
        assert user.get('email') == d['email']
        yield User.col.remove({'email': d['email']})

        d2 = dict(email="t@qq.com", password="1234", password2="1")
        with pytest.raises(ValidationError) as e:
            yield User.insert(**d2)
        assert 'insert error' == e.value.message

    @gen_test
    def test_check_password(self):
        d = dict(email="t@qq.com", password="1234", password2="1234")
        yield User.insert(**d)
        assert (yield User.check_password(d['email'], d['password'])) == True
        assert (yield User.check_password(d['email'], '')) == False
        yield User.col.remove({'email': d['email']})
