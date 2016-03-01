#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import _env
from config.config import CONFIG
from pymongo import MongoClient
from motor import MotorClient
from redis import StrictRedis


def make_mongo_url(mongo_config):
    # http://stackoverflow.com/questions/29006887/mongodb-cr-authentication-failed
    if getattr(mongo_config, 'USERNAME', None):
        MONGO_LOGIN = "%s:%s@" % (mongo_config.USERNAME, mongo_config.PASSWORD)
    else:
        MONGO_LOGIN = ""

    return "mongodb://%s%s:%s/" % (MONGO_LOGIN, mongo_config.HOST,
                                   mongo_config.PORT)


MONGO_URL = make_mongo_url(CONFIG.MONGO)

mongo_client = MongoClient(MONGO_URL)
motor_client = MotorClient(MONGO_URL)
redis_client = StrictRedis(CONFIG.REDIS.HOST, CONFIG.REDIS.PORT,
                           CONFIG.REDIS.PASSWORD)


client_db_map = {
    'mongo': mongo_client,
    'motor': motor_client
}


def get_collection(db_name, collection_name, client='mongo'):
    client = client_db_map.get(client)
    db = getattr(client, db_name, None)
    return getattr(db, collection_name, None)


def get_db(db_name, client='mongo'):
    client = client_db_map.get(client)
    return getattr(client, db_name, None)
