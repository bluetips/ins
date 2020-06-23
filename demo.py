# -*- coding: utf-8 -*-
"""
@Time : 2020/6/16 12:54
@Author : keith wx:bluetips
@File : demo.py
@Software: PyCharm 
@desc: 
"""

from ins_api import Ins


def get_comment(name):
    app = Ins(name)
    ret = app.db_tool.get_short('comment')
    for i in ret:
        i = i[0]
        print('爬取{}的评'.format(i))
        app.get_comment(short=i)


def get_started(name):
    app = Ins(name)
    ret = app.db_tool.get_short('liked')
    for i in ret:
        i = i[0]
        print('爬取{}的咱'.format(i))
        app.get_stars(short=i)


def get_pics(name):
    app = Ins(name)
    app.get_pics()
    app.update_user_crawl_status(1)


def get_tagged(name):
    app = Ins(name)
    app.get_tagged()


if __name__ == '__main__':
    name = 'devonwindsor'
    get_pics(name)

    # get_comment(name)
    # get_started(name)
