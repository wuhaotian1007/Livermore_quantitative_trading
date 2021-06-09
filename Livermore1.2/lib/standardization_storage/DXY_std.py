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
from datetime import date, datetime
from collections import defaultdict
import pandas as pd
import numpy as np
import csv
import sqlite3
import time

# 连接数据库data.db和指针
conn = sqlite3.connect(
    'C:/Users/sgnjim/Desktop/for_python/Livermore1.2/database/XAUUSD.db')
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
DXY_data_path = 'C:/Users/sgnjim/Desktop/for_python/Livermore1.2/raw_data/DXY.csv'


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
