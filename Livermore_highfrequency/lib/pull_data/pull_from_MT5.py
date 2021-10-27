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


class pull_from_MT5_M1:
    def __init__(self, XAUUSD_data_path, length):

        # number of columns to be displayed
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1500)      # max table width to display

        # 建立与MetaTrader 5程序端的连接
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # 从当前开始拉取M1数据
        rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M1, 0, length)

        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the 'datetime' format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # pandas数据可视化
        rates_frame.to_csv(XAUUSD_data_path)
        print("MT5数据拉取成功,保存至{0}".format(XAUUSD_data_path))


class pull_from_MT5_H1:
    def __init__(self, XAUUSD_data_path):
        # number of columns to be displayed
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1500)      # max table width to display

        # 建立与MetaTrader 5程序端的连接
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # set time zone to UTC
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
        utc_from = datetime(2020, 1, 1, tzinfo=timezone)
        utc_to = datetime.now() - timedelta(days=1)
        # get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
        rates = mt5.copy_rates_range(
            "XAUUSD", mt5.TIMEFRAME_H1, utc_from, utc_to)

        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the 'datetime' format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # pandas数据可视化
        rates_frame.to_csv(XAUUSD_data_path)
        print("MT5数据拉取成功,保存至{0}".format(XAUUSD_data_path))


if __name__ == "__main__":
    pull_from_MT5_M1(r"raw_data\XAUUSD_M1.csv", 90000)
    pull_from_MT5_H1(r"raw_data\XAUUSD_H1.csv")
