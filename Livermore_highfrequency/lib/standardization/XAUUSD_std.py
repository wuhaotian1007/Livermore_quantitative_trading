# -*- encoding: utf-8 -*-
'''
@File    :   dataframe.py
@Time    :   2021/04/19 15:02:32
@Author  :   Wuhaotian
@Version :   1.0
@Contact :   460205923@qq.com
'''

# here put the import lib
import sys
import time
from datetime import date, datetime
from collections import defaultdict
import pandas as pd
import numpy as np
import csv
import os
import sqlite3


class XAUUSD_std:
    def __init__(self, XAUUSD_data_path, XAUUSD_db_path):
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_db_path)
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS XAUUSD_list
                (DATE           TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                CLOSE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                HIGH            UNSIGNED INT   NOT NULL,
                LOW             UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                NOTES           TEXT           NULL);''')

        # 按路径读取数据
        with open(XAUUSD_data_path, 'r', encoding="UTF-8") as f_XAUUSD:
            XAUUSD_csv = csv.reader(f_XAUUSD)
            # 跳过第一行
            next(f_XAUUSD)
            for row in XAUUSD_csv:
                date = row[1]
                # 改变日期格式从yyyy/m/d到yyyy-mm-dd
                date = date.replace('/', '-')
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = date.strftime("%Y-%m-%d %H:%M:%S")
                ts = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
                high = row[3]
                low = row[4]
                close = row[5]
                volume = row[6]
                # 插入数据
                close = round(float(close), 2)
                c.execute(
                    "select * from XAUUSD_list where TIMESTICKER == {}".format(ts))
                ts_exist = c.fetchone()
                if not ts_exist:
                    c.execute("insert into XAUUSD_list( DATE, NAME, TIMESTICKER, CLOSE, VOLUME, HIGH, LOW) \
                                VALUES(?, ?, ?, ?, ?, ? , ?) ", (date, "XAUUSD", ts, close, volume, high, low))
                    print("输入{0}".format(ts))
                else:
                    print("重复输入{0}".format(ts))

        print("XAUUSD标准化入库成功,保存至{}".format(XAUUSD_db_path))

        # 关闭数据库连接
        conn.commit()
        conn.close()


class DXY_std:
    def __init__(self, DXY_data_path, XAUUSD_db_path):
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_db_path)
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS DXY_list
            (DATE            TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                CLOSE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0);''')

        # 按路径读取数据

        with open(DXY_data_path, 'r', encoding="UTF-8") as f_DXY:
            DXY_csv = csv.reader(f_DXY)
            # 跳过第一行
            next(DXY_csv)
            for row in DXY_csv:
                date = row[0][0:19]
                close = row[5]
                close = round(float(close), 2)
                ts = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
                c.execute(
                    "select * from DXY_LIST where TIMESTICKER == {}".format(ts))
                ts_exist = c.fetchone()
                if not ts_exist:
                    c.execute("insert into DXY_list(DATE, NAME, TIMESTICKER, CLOSE) \
                                VALUES(?, ?, ?, ?) ", (date, "DXY", ts, close))
                    print("输入{0}".format(ts))
                else:
                    print("重复输入{0}".format(ts))

        print("DXY标准化入库成功,保存至{0}".format(XAUUSD_db_path))

        # 关闭数据库连接
        conn.commit()
        conn.close()


class TNX_std:
    def __init__(self, TNX_data_path, XAUUSD_db_path):
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_db_path)
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS TNX_list
                    (DATE            TEXT           PRIMARY KEY,
                    NAME            TEXT           NOT NULL,
                    CLOSE           UNSIGNED INT   NOT NULL,
                    TIMESTICKER     UNSIGNED INT   NOT NULL,
                    VOLUME          UNSIGNED INT   DEFAULT 0);''')

        # 按路径读取数据

        with open(TNX_data_path, 'r', encoding="UTF-8") as f_TNX:
            TNX_csv = csv.reader(f_TNX)
            # 跳过第一行
            next(TNX_csv)
            for row in TNX_csv:
                date = row[0][0:19]
                close = row[5]
                close = round(float(close), 2)
                ts = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
                c.execute(
                    "select * from TNX_list where TIMESTICKER == {}".format(ts))
                ts_exist = c.fetchone()
                if not ts_exist:
                    c.execute("insert into TNX_list( DATE, NAME, TIMESTICKER, CLOSE) \
                                    VALUES(?, ?, ?, ?) ", (date, "TNX", ts, close))
                    print("输入{0}".format(ts))
                else:
                    print("重复输入{0}".format(ts))

        print("TNX标准化入库成功,保存至{0}".format(XAUUSD_db_path))

        # 关闭数据库连接
        conn.commit()
        conn.close()


if __name__ == '__main__':
    # 小时线入库
    XAUUSD_std(r"raw_data\XAUUSD_H1.csv", r"database\XAUUSD_H.db")
    DXY_std(r"raw_data\DXY_H1.csv", r"database\XAUUSD_H.db")
    TNX_std(r"raw_data\TNX_H1.csv", r"database\XAUUSD_H.db")

    # 分钟线入库
    XAUUSD_std(r"raw_data\XAUUSD_M1.csv", r"database\XAUUSD_M.db")
    DXY_std(r"raw_data\DXY_M2.csv", r"database\XAUUSD_M.db")
    TNX_std(r"raw_data\TNX_M2.csv", r"database\XAUUSD_M.db")