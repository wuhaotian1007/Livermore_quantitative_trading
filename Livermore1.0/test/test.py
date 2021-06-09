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
start_date = "2021-05-05"
for i in range(20):

    # yfinance拉取数据
    df_TNX = yf.download("^TNX", interval="1h", start=start_date)

    print(df_TNX)
