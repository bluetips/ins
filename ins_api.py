# -*- coding: utf-8 -*-
"""
@Time : 2020/6/16 13:18
@Author : keith wx:bluetips
@File : ins_api.py
@Software: PyCharm 
@desc: 
"""
import random
import re
import time
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import pymongo
import pymysql
import requests
from DBUtils.PooledDB import PooledDB


class CookiExceptin(Exception):
    def __init__(self):
        pass

    def __str__(self):
        print("太频繁")


class Ins:
    def __init__(self, name):
        self.db_tool = MysqlTool()
        self.pic_hash = 'eddbde960fed6bde675388aac39a3657'
        self.star_hash = 'd5d763b1e2acf209d62d22d184488e57'
        self.tag_hash = 'ff260833edf142911047af6024eb634a'
        self.cookies = self.db_tool.get_ins_cookie()
        self.headers = {
            'cookie': self.cookies[0],
            'user-agent': 'Mozilla/5.0 (iPehone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        self.username = name
        self.user_id = self.get_uid(name=name)
        # self.myclient = pymongo.MongoClient("mongodb://139.196.91.125:27017/")
        # self.mydb = self.myclient["ins"]
        self.pic_thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="pic_info_")
        self.comment_thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="pic_comment_")
        self.comment_thread_list = []
        self.started_thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="pic_started_")

    def save_star(self, list, short):
        ret_list = []
        for i in list:
            item = {}
            item['owner_id'] = i['node']['id']
            item['owner_name'] = i['node']['username']
            item['full_name'] = i['node']['full_name']
            item['profile_url'] = i['node']['profile_pic_url']
            item['short'] = short
            ret_list.append(item)
        try:
            self.db_tool.save_started(ret_list)
        except Exception:
            pass

    def get_stars(self, short):
        url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22shortcode%22%3A%22{}%22%2C%22include_reel%22%3Atrue%2C%22first%22%3A50%7D'.format(
            self.star_hash, short)
        # resp = requests.get(url, headers=self.headers).json()
        resp = self.change_cookie(url)
        resp_list = resp['data']['shortcode_media']['edge_liked_by']['edges']
        self.save_star(resp_list, short)
        last_code = resp['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']
        while resp['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']:
            url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22shortcode%22%3A%22{}%22%2C%22include_reel%22%3Atrue%2C%22first%22%3A12%2C%22after%22%3A%22{}%22%7D'.format(
                self.star_hash, short, last_code)
            # resp = requests.get(url, headers=self.headers).json()
            resp = self.change_cookie(url)
            resp_list = resp['data']['shortcode_media']['edge_liked_by']['edges']
            self.save_star(resp_list, short)
            last_code = resp['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']

    def save_comment(self, data, short):
        ret_list = []
        for i in data['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']:
            item = {}
            item['short'] = short
            item['comment'] = i['node']['text']
            item['_id'] = i['node']['id']
            item['owner'] = i['node']['owner']['id']
            item['owner_name'] = i['node']['owner']['username']
            item['time'] = i['node']['created_at']
            item['liked'] = i['node']['edge_liked_by']['count']
            ret_list.append(item)
        try:
            self.db_tool.save_comments(ret_list)
        except Exception:
            pass

    def get_comment(self, short):
        url = 'https://www.instagram.com/p/{}/comments/?__a=1'.format(short)
        resp = self.change_cookie(url)
        # resp = requests.get(url, headers=self.headers).json()
        print('get_comment')
        self.save_comment(resp, short)

    def save_pic(self, data_list):
        ret_list = []
        for data in data_list:
            item = {}
            item['_id'] = data['node']['id']
            content = ''
            try:
                for i in data['node']['edge_sidecar_to_children']['edges']:
                    content = content + i['node']['display_url'] + '\n'
            except Exception:
                content = data['node']['display_url']
            item['content'] = content
            item['short'] = data['node']['shortcode']
            item['time'] = data['node']['taken_at_timestamp']
            item['like_num'] = data['node']['edge_media_preview_like']['count']
            item['comment_num'] = data['node']['edge_media_to_comment']['count']
            item['user_id'] = self.user_id
            item['username'] = self.username
            try:
                item['text'] = data['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception:
                item['text'] = ''
                pass
            ret_list.append(item)
        self.db_tool.save_pics(ret_list)

    def change_cookie(self, url):
        while 1:
            resp = requests.get(url, headers=self.headers).json()
            if resp.get('status') == 'fail':
                print('切换cookie')
                self.headers = {
                    'cookie': random.choice(self.cookies),
                    'user-agent': 'Mozilla/5.0 (iPehone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
                }
            else:
                break
        return resp

    def get_pics(self):
        uid = self.user_id
        url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A50%7D'.format(
            self.pic_hash, uid)
        resp = self.change_cookie(url)

        resp_list = resp['data']['user']['edge_owner_to_timeline_media'][
            'edges']
        ret_list = []
        for i in resp_list:
            short = i['node']['shortcode']
            ret_list.append(i)
        self.save_pic(ret_list)
        last_code = resp['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

        while resp['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']:
            url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A50%2C%22after%22%3A%22{}%22%7D'.format(
                self.pic_hash, uid, last_code)
            time.sleep(10)
            resp = self.change_cookie(url)
            resp_list = resp['data']['user']['edge_owner_to_timeline_media'][
                'edges']
            ret_list = []
            for i in resp_list:
                short = i['node']['shortcode']
                ret_list.append(i)
            self.save_pic(ret_list)
            last_code = resp['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

    def get_uid(self, name):
        url = 'https://www.instagram.com/{}/tagged/'.format(name)
        resp = requests.get(url, headers=self.headers)
        return re.findall('"owner":\{"id":"(\d+)"', resp.content.decode())[0]

    def save_tags(self, data):
        ret_list = []
        for i in data:
            item = {}
            item['username'] = self.username
            item['user_id'] = self.user_id
            item['_typename'] = i['node']['__typename']
            try:
                item['text'] = i['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception:
                item['text'] = ''
            item['short'] = i['node']['shortcode']
            item['comment_num'] = i['node']['edge_media_to_comment']['count']
            item['time'] = i['node']['taken_at_timestamp']
            item['owner_id'] = i['node']['owner']['id']
            item['owner_name'] = i['node']['owner']['username']
            item['content'] = i['node']['display_url']
            ret_list.append(item)
        try:
            self.db_tool.save_tagged(ret_list)
        except Exception:
            pass

    def get_tagged(self):
        uid = self.user_id
        base_url = 'https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A50%2C%22"%3A"{}"%7D'
        url = base_url.format(self.tag_hash, uid, "")
        # resp = requests.get(url, headers=self.headers).json()
        resp = self.change_cookie(url)
        tag_list = resp['data']['user']['edge_user_to_photos_of_you']['edges']
        self.save_tags(tag_list)
        while resp['data']['user']['edge_user_to_photos_of_you']['page_info']['has_next_page']:
            next_code = resp['data']['user']['edge_user_to_photos_of_you']['page_info']['end_cursor']
            url = base_url.format(self.tag_hash, uid, next_code)
            time.sleep(5)
            # resp = requests.get(url, headers=self.headers).json()
            resp = self.change_cookie(url)
            tag_list = resp['data']['user']['edge_user_to_photos_of_you']['edges']
            self.save_tags(tag_list)


class MysqlTool:
    def __init__(self):
        # self.connect = pymysql.connect(host="139.196.91.125", user="weibo", password="keith123",
        #                                database="weibo", port=3306)
        # self.pool = PooledDB(pymysql, 5, host="139.196.91.125", user='weibo',
        #                      passwd='keith123', db='weibo', port=3306)
        #
        self.connect = pymysql.connect(host="127.0.0.1", user="root", password="woaixuexi",
                                       database="chiccess", port=3306)
        self.pool = PooledDB(pymysql, 5, host="127.0.0.1", user='root',
                             passwd='woaixuexi', db='chiccess', port=3306)

    def get_ins_cookie(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        cursor.execute("select cookie from ins_cookies")
        ret = cursor.fetchall()
        cursor.close()
        conn.close()
        ret = [i[0] for i in ret]
        return ret

    def save_pics(self, ret_list):
        print('save_pics')
        ret_list = [(
            i['short'], i['time'], pymysql.escape_string(i['text']), i['content'], i['user_id'],
            i['username'], i['like_num'], i['comment_num']
        ) for i in ret_list]
        try:
            cursor = self.connect.cursor()
            sql_template = "insert into ins_pics(short,time,text,content,user_id,username,like_num,comment_num)values (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.executemany(sql_template, ret_list)
            self.connect.commit()
        except Exception:
            self.connect.rollback()
            for ret in ret_list:
                try:
                    cursor.execute(sql_template % (ret))
                except Exception:
                    print('inert error')
            self.connect.commit()
        pass

    def save_tagged(self, ret_list):
        ret_list = [(
            i['short'], i['time'], pymysql.escape_string(i['text']), i['content'], i['_typename'], i['user_id'],
            i['username'],
            i['owner_id'], i['owner_name'], i['comment_num']) for i in ret_list]
        try:
            cursor = self.connect.cursor()
            sql_template = "insert into ins_tagged(short,time,text,content,typename,user_id,username,owner_id,owner_name,comment_num)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.executemany(sql_template, ret_list)
            self.connect.commit()
        except Exception:
            self.connect.rollback()
            for ret in ret_list:
                try:
                    cursor.execute(sql_template % (ret))
                except Exception:
                    print('inert error')
            self.connect.commit()

    def get_short(self, type):
        conn = self.pool.connection()
        cursor = conn.cursor()
        cursor.execute(" select short from ins_pics where short not in(select short from ins_{}); ".format(type))
        ret = cursor.fetchall()
        cursor.close()
        conn.close()
        return ret

    def save_started(self, ret_list):
        '''item['owner_id'] = i['node']['id']
            item['owner_name'] = i['node']['username']
            item['full_name'] = i['node']['full_name']
            item['profile_url'] = i['node']['profile_pic_url']
            item['short']'''
        print('save_star')
        conn = self.pool.connection()
        cursor = conn.cursor()
        ret_list = [(
            i['short'], i['owner_id'],
            i['owner_name'], i['full_name'], i['profile_url']) for i in ret_list]
        try:

            sql_template = "insert into ins_liked(short,user_id,username,fullname,profile_url)values (%s,%s,%s,%s,%s)"
            cursor.executemany(sql_template, ret_list)
            conn.commit()
        except Exception:
            pass
        finally:
            cursor.close()
            conn.close()
        pass

    def save_comments(self, ret_list):
        print('save_comment')
        conn = self.pool.connection()
        cursor = conn.cursor()
        ret_list = [(
            i['_id'], i['short'], i['time'], pymysql.escape_string(i['comment']), i['owner'],
            i['owner_name'], i['liked']) for i in ret_list]
        try:

            sql_template = "insert into ins_comment(id,short,time,comment,user_id,username,like_num)values (%s,%s,%s,%s,%s,%s,%s)"
            cursor.executemany(sql_template, ret_list)
            conn.commit()
        except Exception:
            self.connect.rollback()
            for ret in ret_list:
                try:
                    sql_tem = "insert into ins_comment(id,short,time,comment,user_id,username,like_num)values ('%s','%s','%s','%s','%s','%s','%s')"
                    cursor.execute(sql_tem % (ret))
                except Exception:
                    print('inert error')
            conn.commit()
        finally:
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app = Ins('devonwindsor')
    ret = app.db_tool.get_short('comment')
    for i in ret:
        i = i[0]
        print('爬取{}的评'.format(i))
        app.get_comment(short=i)
        # app.get_stars(short=i)
    # app.get_tagged()
    # app.get_pics()

    # for future in as_completed(app.comment_thread_list):
    #     print('插入评论成功')
    #     pass
    #     uid = app.get_uid('elkin')
    #     app.get_tagged(uid)
    #     # app.get_pics(uid)
    #     # ret = app.mydb['pic'].find()
    #     # for i in ret:
    #     #     app.get_stars(short=i['short'])
    #     #     app.get_comment(short=i['short'])
    #     #     time.sleep(10)
    #     #     pass
