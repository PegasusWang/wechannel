#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import _env
import bcrypt
import concurrent.futures
import traceback
from wtforms import ValidationError
from tornado.escape import utf8
from tornado.gen import coroutine, Return
from config.config import CONFIG
from lib._db import get_collection
from model.forms import RegisterForm


executor = concurrent.futures.ThreadPoolExecutor(2)


class User(object):
    __collection__ = 'user'
    col = get_collection(CONFIG.MONGO.DATABASE, __collection__, 'motor')
    _fields = {
        'email',
        'password',
    }

    @classmethod
    @coroutine
    def insert(cls, email, password, password2):
        user = yield cls.col.find_one({'email': email})
        form = RegisterForm(email=email, password=password,
                            password2=password2)

        if (not user) and form.validate():
            password_hashed = yield executor.submit(
                bcrypt.hashpw, utf8(password), bcrypt.gensalt())
            yield cls.col.insert({'email': email, 'password': password_hashed})
        else:
            raise ValidationError("insert error")

    @classmethod
    @coroutine
    def check_password(cls, email, check_password):
        user = yield cls.col.find_one({'email': email})
        password = user.get('password')
        password_hashed = yield executor.submit(
            bcrypt.hashpw, utf8(check_password), utf8(password))
        raise Return(password == password_hashed)
