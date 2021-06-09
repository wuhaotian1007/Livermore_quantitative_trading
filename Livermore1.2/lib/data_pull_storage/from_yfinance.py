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
import yfinance as yf


# 数据范围开始日期
start_date = "2020-01-01"
# yfinance拉取数据
df_TNX = yf.download("^TNX", interval="1h", start=start_date)
df_DXY = yf.download("DX-Y.NYB", interval="1h", start=start_date)

# DXY原数据路径
DXY_data_path = 'C:/Users/sgnjim/Desktop/for_python/Livermore1.2/raw_data/DXY.csv'
# TNX原数据路径
TNX_data_path = 'C:/Users/sgnjim/Desktop/for_python/Livermore1.2/raw_data/TNX.csv'

# pandas数据可视化
df_TNX.to_csv(TNX_data_path)
df_DXY.to_csv(DXY_data_path)


# 连接数据库data.db和指针
conn = sqlite3.connect(
    'C:/Users/sgnjim/Desktop/for_python/Livermore1.2/database/raw_data.db')
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
        c.execute("insert into DXY_list(DATE, NAME, TIMESTICKER, CLOSE) \
                     VALUES(?, ?, ?, ?) ", (date, "DXY", ts, close))

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
        c.execute("insert into TNX_list( DATE, NAME, TIMESTICKER, CLOSE) \
                     VALUES(?, ?, ?, ?) ", (date, "TNX", ts, close))

# 关闭数据库连接
conn.commit()
conn.close()
