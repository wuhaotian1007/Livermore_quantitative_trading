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
    def __init__(self, DXY_data_path, TNX_data_path, frequency, length):

        # yfinance拉取数据
        df_TNX = yf.download("^TNX", interval=frequency, period=length)
        df_DXY = yf.download("DX-Y.NYB", interval=frequency, period=length)

        # pandas数据可视化
        df_TNX.to_csv(TNX_data_path)
        df_DXY.to_csv(DXY_data_path)

        print("yfinance:{0}数据{1}拉取成功".format(frequency, length))


class pull_from_yfinance_H1:
    def __init__(self, DXY_data_path, TNX_data_path):
        # 数据范围开始日期
        start_date = "2020-01-01"
        # yfinance拉取数据
        df_TNX = yf.download("^TNX", interval="1h", start=start_date)
        df_DXY = yf.download("DX-Y.NYB", interval="1h", start=start_date)

        # pandas数据可视化
        df_TNX.to_csv(TNX_data_path)
        df_DXY.to_csv(DXY_data_path)

        print("yfinanceH1数据拉取成功")


if __name__ == "__main__":
    pull_from_yfinance(r"raw_data\DXY_M2.csv",
                       r"raw_data\TNX_M2.csv", "2m", "60d")
    pull_from_yfinance_H1(r"raw_data\DXY_H1.csv", r"raw_data\TNX_H1.csv")
