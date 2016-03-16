#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime


def datestr_from_stamp(time_stamp, format_str):
    """strftime('%Y-%m-%d %H:%M:%S')"""
    try:
        return (
            datetime.datetime.fromtimestamp(
                int(time_stamp)
            ).strftime(format_str)
        )
    except ValueError:
        return (
            datetime.datetime.fromtimestamp(
                int(time_stamp/1000.0)
            ).strftime(format_str)
        )


def datetime_from_stamp(time_stamp):
    try:
        return (
            datetime.datetime.fromtimestamp(
                int(time_stamp)
            )
        )
    except ValueError:
        return (
            datetime.datetime.fromtimestamp(
                int(time_stamp/1000.0)
            )
        )


def days_from_epoch(year, month, day):
    """从1970.01.01到给定日期的天数"""
    date_time = datetime.datetime(year, month, day)
    beg_date_time = datetime.datetime(1970, 1, 1)
    return (date_time-beg_date_time).days


def datetime_from_days(days):
    """从1970.01.01的天数到datetime对象"""
    beg_date_time = datetime.datetime(1970, 1, 1)
    return beg_date_time + datetime.timedelta(days=days)


def days_from_slash_date(date_str):
    '''1990/08/22'''
    if date_str.count('/') == 1:
        year, month = date_str.split('/')
        if len(year) < len(month):
            year, month = month, year
        return days_from_epoch(int(year), int(month), day=1)

    elif date_str.count('/') == 2:
        year, month, day = map(int, date_str.split('/'))
        return days_from_epoch(year, month, day)
    else:
        print(date_str)
        return date_str


def days_from_now(timestamp):
    """计算给定时间戳距离现在多少天"""
    now = datetime.datetime.now()
    old = datetime_from_stamp(timestamp)
    return (now-old).days


if __name__ == '__main__':
    print(datetime_from_stamp(757382400000))
    print(type(datetime_from_stamp(757382400000)))
    print(days_from_slash_date('2000/08/24'))
    print(days_from_slash_date('1990/03/29'))
    print(days_from_slash_date('12/1989'))
    print(days_from_slash_date('2000/08/24'))
    print(type(days_from_slash_date('2000/08/24')))
    print(datetime_from_days(days_from_epoch(2015,1,1)))
    print(days_from_now(1457478405))
