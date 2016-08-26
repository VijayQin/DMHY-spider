#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 19:25:58 2016

if you have any questions,
please feel free to contact me.

@author: Vijay Qin

"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import sqlite3
import os
import requests
from lxml import html
import datetime
import urllib2
import time
import re


# MS_PATH_LIMIT = 260
MS_PATH_LIMIT = 247

class DMHY_Write_file_exception:

    def __init__ (self, path, mode, url):
        self.path = path
        self.url = url
        self.write_file = open(path, mode)

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        if type != None :
            print "type:", type
            print "value:", value
            print "trace:", trace
            try :
                print "path:", self.path
            except :
                print "path:", self.path.encode("gbk", "ignore")
            print "url:", self.url
        self.write_file.close()

    def write(self, content):
        return self.write_file.write(content)


class DMHY_DataBase:

    def __init__(self, mode, attr, url, domain, sqlite_db, time_delay, warehouse):

        self.mode = mode
        self.attr = attr
        self.url = url
        self.domain = domain
        self.sqlite_db = sqlite_db
        self.time_delay = time_delay
        self.warehouse = warehouse
        self.new_data = []

        with sqlite3.connect(sqlite_db) as con :
            cu = con.cursor()
            create_sql = r'''
                create table if not exists DMHY_DataBase (
                    id INTEGER PRIMARY KEY,
                    date VARCHAR(20),
                    type VARCHAR(10),
                    title VARCHAR(255),
                    magnet VARCHAR(255),
                    size VARCHAR(10),
                    uploader VARCHAR(30),
                    HTML TEXT,
                    attach VARCHAR(255),
                    finish BOOLEAN
                )'''
            cu.execute(create_sql)
            cu.close()
            con.commit()

        if not os.path.exists(warehouse) :
            os.makedirs(warehouse)

        # 1、更新昨天
        if 1 == mode :
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            self.date_min = datetime.datetime.combine(yesterday, datetime.time.min)
            self.date_max = datetime.datetime.combine(yesterday, datetime.time.max)
        # 2、更新指定日期(格式:2016-08-23)
        elif 2 == mode :
            target_date = datetime.datetime.strptime(attr, r'%Y-%m-%d')
            self.date_min = datetime.datetime.combine(target_date, datetime.time.min)
            self.date_max = datetime.datetime.combine(target_date, datetime.time.max)
        # 3、更新时间段(格式:['2016-08-22','2016-08-23'])
        elif 3 == mode :
            target_date = attr.split(',')
            target_date_min = datetime.datetime.strptime(target_date[0][1:], r'%Y-%m-%d')
            target_date_max = datetime.datetime.strptime(target_date[1][:-1], r'%Y-%m-%d')
            self.date_min = datetime.datetime.combine(target_date_min, datetime.time.min)
            self.date_max = datetime.datetime.combine(target_date_max, datetime.time.max)
        # 4、自动更新模式
        elif 4 == mode :
            with sqlite3.connect(sqlite_db) as con :
                cu = con.cursor()
                select_sql = r'''
                    select
                        date
                    from
                        DMHY_DataBase
                    ORDER BY
                        date DESC
                    LIMIT 1
                    '''
                cu.execute(select_sql)
                date = cu.fetchall()
                if [] != date :
                    date = date[0][0]
                    self.date_min = datetime.datetime.strptime(date, r'%Y/%m/%d %H:%M')
                    self.date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                else :
                    self.date_min = datetime.datetime.fromtimestamp(0.0)
                    self.date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
                cu.close()
                con.commit()


    def fetch_update_list(self) :
        """
        return update list.
        """
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        page = 1
        update_list = []
        while True :
            # time.sleep(self.time_delay)
            response = requests.get(self.url + str(page), headers)
            tree = html.fromstring(response.content)
            response.close()
            data_list = tree.xpath('//table[@id="topic_list"]/tbody/tr')
            i = 0
            for data in data_list :
                date = data.xpath('td[1]/span/text()')[0]
                trial = self.date_justify(date, page)
                if 1 == trial :
                    pass
                elif 0 == trial :
                    update_list.append(data)
                else :
                    return update_list
            page = page + 1


    def start_requests(self) :
        """
        Start update tasks.

        return 0表示下载完成
        """
        print u"正在获取更新列表..."
        update_list = self.fetch_update_list()
        update_num = len(update_list)
        print u"本次共有%d个更新" % update_num
        with sqlite3.connect(self.sqlite_db) as con :
            # Download updates
            for i in range(update_num) :
                print ""
                print u"已完成：%d/%d" % (i, update_num)
                sys.stdout.write("\033[2F") # Cursor up one line
                self.parse_item(update_list[i], con)
            # Clean up out-of-date items
            print u"正在清除过期的内容..."
            insert_sql = '''
                insert into DMHY_DataBase
                    values(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
            cu = con.cursor()
            for d in self.new_data :
                cu.execute(insert_sql, d)
            cu.close
            con.commit()
            print u"内容更新完毕"
            return 0


    def date_justify(self, date, page) :
        # return 1表示日期还没到, return 0表示要下载, return -1表示日期已过
        item_date = datetime.datetime.strptime(date, r'%Y/%m/%d %H:%M');
        # 1、更新昨天 2、更新指定日期(格式:2016-08-08) 3、更新时间段(格式:[2016-08-05,2016-08-08])
        # 4、自动更新模式 5、更新固定页数
        if self.mode in [1,2,3,4]:
            if 0 < (item_date - self.date_max).total_seconds() :
                return 1
            elif 0 <= (item_date - self.date_min).total_seconds() :
                return 0
            else :
                return -1
        elif 5 == self.mode :
            if page <= self.attr :
                return 0
            else :
                return -1


    def parse_item(self, data, con) :
        item_date = data.xpath('td[1]/span/text()')[0]
        item_type = data.xpath('td[2]/a//font/text()')[0]
        item_title = data.xpath('td[@class="title"]/a/text()')[0]
        item_title = self.formulate_title(item_title)
        item_magnet = data.xpath('td[4]/a[@class="download-arrow arrow-magnet"]/@href')[0]
        item_size = data.xpath('td[5]/text()')[0]
        item_uploader = data.xpath('td[9]/a/@href')[0]
        item_uploader = self.domain + item_uploader
        item_finish = False

        try:
            print u"[正在下载] " + item_title
        except Exception, e:
            print (u"[正在下载] " + item_title).encode("GBK", 'ignore')
            # print (u"[正在下载] " + item_title).encode("GB18030")

        # 为了不造成服务器太大负担, 所以每次请求间隔10s
        # 所以可能会出现,请求第二页的时候,已经有字幕组新上传了动画,此时第一页的最后几条会在第二页出现
        # 因此在实际使用的时候需要重新查询一遍数据库是否有该条记录
        cu = con.cursor()
        select_sql = '''
            select
                count(*)
            from
                DMHY_DataBase
            where
                date = ? AND
                type = ? AND
                title = ? AND
                size = ? OR
                magnet = ?
            '''
        cu.execute(select_sql, (item_date, item_type, item_title, item_size, item_magnet))
        if 0 == cu.fetchall()[0][0]:
            path = self.formulate_folder_path(item_date, item_type, item_title)
            if not os.path.exists(path) :
                os.makedirs(path)
            item_attach = path

            # get item
            url = self.domain + data.xpath('td[@class="title"]/a/@href')[0]
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = {'User-Agent': user_agent}
            time.sleep(self.time_delay)
            response = requests.get(url, headers)
            item_html = response.text
            response.close()

            # save html
            html_title = self.formulate_title(url.split('/')[-1])
            file_path = self.prune_title(path, html_title)
            # with open(file_path, 'w') as f_html :
            #     f_html.write(item_html)
            with DMHY_Write_file_exception(file_path, 'w', url) as f_html :
                f_html.write(item_html)

            # save torrent
            tree = html.fromstring(item_html)
            torrent_urls = tree.xpath('//div[@id="resource-tabs"]/div/p[1]/a/@href')
            if 1<= len(torrent_urls) :
                torrent_url = torrent_urls[0]
                torrent_url = 'https:' + torrent_url
                time.sleep(self.time_delay)
                try :
                    u = urllib2.urlopen(torrent_url)
                except urllib2.HTTPError, e:
                    if 404 == e.code :
                        print "HTTPError error({0}): {1}".format(e.code, e.reason)
                    else :
                        print e.code
                        print e.reason
                        raise
                except Exception as e:
                    print e.code
                    print e.reason
                    raise
                torrent = u.read()
                u.close()
                fileName = self.formulate_title(torrent_url.split('/')[-1])
                file_path = self.prune_title(path, fileName)
                # with open(file_path, 'wb') as f :
                #     f.write(torrent)
                with DMHY_Write_file_exception(file_path, 'wb', url) as f :
                    f.write(torrent)

            # add self.new_data
            item = (item_date, item_type, item_title, item_magnet, item_size)
            item = item + (item_uploader, item_html, item_attach, item_finish)
            self.new_data.insert(0, item)
        cu.close()

        sys.stdout.write("\033[F") # Cursor up one line
        sys.stdout.write("\033[K") # Clear to the end of line
        try:
            print u"[完成] " + item_title
        except Exception, e:
            print (u"[完成] " + item_title).encode("GBK", 'ignore')
        sys.stdout.write("\033[K") # Clear to the end of line


    def prune_title (self, path, fileName) :
        joinpath = os.path.join(path, fileName)
        if MS_PATH_LIMIT <= len(joinpath) :
            joinpath = os.path.join(path, fileName[len(path)-(MS_PATH_LIMIT-1):])
        return joinpath


    def formulate_title (self, title) :
        title = "_".join(title.split(' '))
        title = "".join(title.split())
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        title = re.sub(rstr, "_", title)
        return title


    def formulate_folder_path(self, item_date, item_type, item_title) :

        item_datetime = datetime.datetime.strptime(item_date, r'%Y/%m/%d %H:%M')
        joinpath = os.path.join(self.warehouse,
                                str(item_datetime.year),
                                '%02d' % item_datetime.month,
                                '%02d' % item_datetime.day,
                                str(item_type),
                                '%02d%02d_%s' % (item_datetime.hour,
                                                item_datetime.minute,
                                                item_title))[:MS_PATH_LIMIT-10]
        return joinpath


if __name__ == '__main__':

    print u"请输入模式:1、更新昨天 2、更新指定日期(格式:2016-08-08)"
    print u"           3、更新时间段(格式:[2016-08-05,2016-08-08])"
    print u'           4、自动更新模式(不要在第一次运行时使用) 5、更新固定页数'
    mode = int(raw_input())

    if 1 == mode :
        print u'即将更新昨天的内容'
        attr = ''
    elif 2 == mode :
        print u'请输入要更新的日期(格式:2016-08-08)'
        attr = str(raw_input())
    elif 3 == mode :
        print u"请输入要更新的时间段(格式:[2016-08-05,2016-08-08])"
        attr = str(raw_input())
    elif 4 == mode :
        print u'即将进入自动更新模式(不要在第一次运行时使用)'
        attr = ''
    elif 5 == mode :
        print u'请输入要更新的页数'
        attr = int(raw_input())

    url = r"https://share.dmhy.org/topics/list/page/"
    domain = r"https://share.dmhy.org"

    path = os.getcwd()

    # sqlite_db = r"D:\Data\Desktop\Workspace\test\DMHY\DMHY.db"
    sqlite_db = os.path.join(path, 'DMHY.db')
    time_delay = 0

    # warehouse = r'D:\Data\Desktop\Workspace\test\DMHY\Warehouse'
    warehouse = os.path.join(path, 'Warehouse')
    if (MS_PATH_LIMIT-40) <= len(warehouse) :
        print u'本地仓库路径过长, 不能超出',str(MS_PATH_LIMIT-41),u'个字符, 请更改存放路径'

    print u'正在更新内容, 请稍后'
    DataBase = DMHY_DataBase(mode, attr, url, domain, sqlite_db, time_delay, warehouse)
    DataBase.start_requests()
