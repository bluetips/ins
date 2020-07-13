# -*- coding: utf-8 -*-
"""
@Time : 2020/6/16 12:54
@Author : keith wx:bluetips
@File : demo.py
@Software: PyCharm 
@desc: 
"""
import csv
from concurrent.futures.thread import ThreadPoolExecutor

from ins_api import Ins, MysqlTool


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
    if app.user_id == 0:
        return
    else:
        app.get_pics()
        app.update_user_crawl_status(1)


def get_pics_1(name):
    app = Ins(name)


def get_tagged(name):
    app = Ins(name)
    if app.user_id == 0:
        return
    else:
        app.get_tagged()


def thread_pool_run_pics():
    pics_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="pic_")
    db_tool = MysqlTool()
    cursor = db_tool.connect.cursor()
    cursor.execute('select distinct username as name from ins_pics;')
    ret = cursor.fetchall()
    ret = [i[0] for i in ret]
    ins_ids = csv.reader(open('./ins.csv'))
    pn = 0
    for ins_id in ins_ids:
        if pn < 2:
            pn += 1
            continue
        elif ins_id[1] in ret:
            continue
        else:
            name = ins_id[1]
            pics_pool.submit(get_pics, name)


def thread_pool_run_pics_2():
    pics_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="pic_")
    ins_ids = csv.reader(open('./ins.csv'))
    pn = 0
    for ins_id in ins_ids:
        if pn < 2:
            pn += 1
            continue
        else:
            name = ins_id[1]
            pics_pool.submit(get_pics_1, name)


def thread_pool_run_tagged():
    pics_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="tagged_")
    db_tool = MysqlTool()
    cursor = db_tool.connect.cursor()
    cursor.execute('select distinct username as name from ins_pics;')
    ret = cursor.fetchall()
    ret = [i[0] for i in ret]
    cursor.execute('select distinct username as name from ins_tagged;')
    ret_2 = cursor.fetchall()
    ret_2 = [i[0] for i in ret]
    for i in ret:
        if i in ret_2:
            continue
        get_tagged(i)
        # pics_pool.submit(get_tagged, i)


if __name__ == '__main__':
    # get_pics('virat.kohli')
    # edge_sidecar_to_children
    # thread_pool_run_pics_2()
    thread_pool_run_pic()
s