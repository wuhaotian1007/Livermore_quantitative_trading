# -*- encoding: utf-8 -*-
'''
@File    :   pull_from_yfinance.py
@Time    :   2021/10/02 19:29:38
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sys
import time
import datetime
from collections import defaultdict
import pandas as pd
import numpy as np
import csv
import sqlite3
import yfinance as yf


class pull_from_yfinance:
    def __init__(self, DXY_data_path, TNX_data_path, raw_data_db_path):

        # yfinance拉取数据
        df_TNX = yf.download("^TNX", interval="2m", period="60d")
        df_DXY = yf.download("DX-Y.NYB", interval="2m", period="60d")

        # pandas数据可视化
        df_TNX.to_csv(TNX_data_path)
        df_DXY.to_csv(DXY_data_path)

        # 连接数据库data.db和指针
        conn = sqlite3.connect(raw_data_db_path)
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

        print("yfinance数据拉取成功")


if __name__ == "__main__":
    pull_from_yfinance(r"raw_data\DXY.csv",
                       r"raw_data\TNX.csv", r"database\XAUUSD.db")
