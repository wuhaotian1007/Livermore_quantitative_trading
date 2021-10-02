# -*- encoding: utf-8 -*-
'''
@File    :   pull_from_MT5.py
@Time    :   2021/10/02 19:15:08
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''


# here put the import lib
import csv
import pytz
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import sqlite3
import time
import datetime


class pull_from_MT5_history:
    def __init__(self, XAUUSD_data_path):

        # number of columns to be displayed
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1500)      # max table width to display

        # 建立与MetaTrader 5程序端的连接
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # 从当前开始拉取M1数据
        rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M1, 0, 90000)
        mt5.shutdown()

        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the 'datetime' format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # pandas数据可视化
        rates_frame.to_csv(XAUUSD_data_path)
        print("MT5数据拉取成功,保存至{0}".format(XAUUSD_data_path))

class XAUUSD_std:
    def __init__(self, XAUUSD_data_path, XAUUSD_db_path) -> None:
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
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = date.strftime("%Y-%m-%d %H:%M:%S")
                ts = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M:%S"))
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
        print("XAUUSD_Daily标准化入库成功")
        
if __name__ == "__main__":
    pull_from_MT5_history(r"raw_data\XAUUSD_M1.csv")
    XAUUSD_std(r"raw_data\XAUUSD_M1.csv", r"database\XAUUSD.db")
