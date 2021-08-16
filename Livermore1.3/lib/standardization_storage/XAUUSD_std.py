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
import sqlite3


class XAUUSD_std:
    def __init__(self, XAUUSD_db_path, XAUUSD_data_path) -> None:
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_db_path)
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS XAUUSD_list
            (DATE            TEXT           PRIMARY KEY,
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
                date = datetime.strptime(date, "%Y-%m-%d")
                date = date.strftime("%Y-%m-%d")
                ts = time.mktime(time.strptime(date, "%Y-%m-%d"))
                high = row[3]
                low = row[4]
                close = row[5]
                volume = row[6]
                # 插入数据
                close = round(float(close), 2)
                c.execute("insert into XAUUSD_list( DATE, NAME, TIMESTICKER, CLOSE, VOLUME, HIGH, LOW) \
                            VALUES(?, ?, ?, ?, ?, ? , ?) ", (date, "XAUUSD", ts, close, volume, high, low))

        # 保存并关闭数据库连接
        conn.commit()
        conn.close()

class TNX_std:
    def __init__(self, XAUUSD_db_path, TNX_data_path):
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_db_path)
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS TNX_list
            (DATE            TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                CLOSE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                NOTES           TEXT           NULL);''')

        # 按路径读取数据

        with open(TNX_data_path, 'r', encoding="UTF-8") as f:
            TNX_csv = csv.reader(f)
            # 跳过第一行
            next(TNX_csv)
            for row in TNX_csv:
                date = row[0][0:10]
                t = row[0][11:16]
                close = row[5]
                ts = time.mktime(time.strptime(date, "%Y-%m-%d"))
                close = round(float(close), 2)
                if t == '08:00':
                    # 插入数据
                    c.execute("insert into TNX_list( DATE, NAME, TIMESTICKER, CLOSE) \
                            VALUES(?, ?, ?, ?) ", (date, "TNX", ts, close))

        # 关闭数据库连接
        conn.commit()
        conn.close()

class DXY_std:
    def __init__(self, XAUUSD_db_path, DXY_data_path):
        # 连接数据库data.db和指针
        conn = sqlite3.connect(
            'C:/Users/sgnjim/Desktop/for_python/Livermore1.3/database/XAUUSD.db')
        c = conn.cursor()

        # 创建表data_list收集
        c.execute('''CREATE TABLE IF NOT EXISTS DXY_list
            (DATE            TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                CLOSE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                NOTES           TEXT           NULL);''')

        # DXY原数据路径
        DXY_data_path = 'C:/Users/sgnjim/Desktop/for_python/Livermore1.3/raw_data/DXY.csv'

        # 按路径读取数据

        with open(DXY_data_path, 'r', encoding="UTF-8") as f:
            DXY_csv = csv.reader(f)
            next(DXY_csv)
            for row in DXY_csv:
                date = row[0][0:10]
                t = row[0][11:16]
                close = row[5]
                ts = time.mktime(time.strptime(date, "%Y-%m-%d"))
                close = round(float(close), 2)
                if t == '17:00':
                    # 插入数据
                    c.execute("insert into DXY_list( DATE, NAME, TIMESTICKER, CLOSE) \
                            VALUES(?, ?, ?, ?) ", (date, "DXY", ts, close))

        # 关闭数据库连接
        conn.commit()
        conn.close()
        print("标准化入库成功")
