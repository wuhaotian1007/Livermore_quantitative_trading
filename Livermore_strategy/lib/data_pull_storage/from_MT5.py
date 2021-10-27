# -*- encoding: utf-8 -*-
'''
@File    :   from_MT5.py
@Time    :   2021/05/03 14:18:08
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


class pull_from_MT5:
    def __init__(self, XAUUSD_data_path, name, database_path, interval):
        # number of columns to be displayed
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1500)      # max table width to display

        # 建立与MetaTrader 5程序端的连接
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # 建立数据库连接
        strategy_db_path = database_path + r"\strategy.db"
        conn_strategy = sqlite3.connect(strategy_db_path)
        cur_strategy = conn_strategy.cursor()

        # 获取今天开始的时间戳
        today = datetime.date.today()
        today_ts = int(time.mktime(time.strptime(str(today), '%Y-%m-%d')))

        # 获取开始日期
        cur_strategy.execute("select time_interval from strategy_list")
        time_interval = cur_strategy.fetchone()[0]
        start_date = time_interval.split(",")[0]
        start_ts = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
        end_date = time_interval.split(",")[1]
        end_ts = time.mktime(time.strptime(end_date, "%Y-%m-%d"))
        if start_ts <= today_ts + 729 * 86400:
            start_ts = today_ts - 729 * 86400
            start_date = time.strftime("%Y-%m-%d", time.localtime(start_ts))
            print("超出MT5时间范围730天，已自动获取{0}到{1}的数据".format(start_date, end_date))
        
        start_ts_backups = start_ts - 365 * 86400
        # set time zone to UTC
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset

        # get bars
        if interval == "D1_max":
            rates = mt5.copy_rates_range(
                name, mt5.TIMEFRAME_D1, start_ts_backups, end_ts)
        if interval == "D1":
            rates = mt5.copy_rates_range(
                name, mt5.TIMEFRAME_D1, start_ts, end_ts)
        if interval == "M10":
            rates = mt5.copy_rates_range(
                name, mt5.TIMEFRAME_M10, start_ts, end_ts)
        if interval == "M12":
            rates = mt5.copy_rates_range(
                name, mt5.TIMEFRAME_M12, start_ts, end_ts)
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the 'datetime' format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # pandas数据可视化
        rates_frame.to_csv(XAUUSD_data_path)
        print("MT5数据{0}拉取成功,保存至{1}".format(interval, XAUUSD_data_path))


if __name__ == "__main__":
    pull_from_MT5(r"raw_data\XAUUSD_D1_max.csv", "XAUUSD", "database", "D1_max")
    pull_from_MT5(r"raw_data\XAUUSD_D1.csv", "XAUUSD", "database", "D1")
    pull_from_MT5(r"raw_data\XAUUSD.csv", "XAUUSD", "database", "D1")
    pull_from_MT5(r"raw_data\XAUUSD_M12.csv", "XAUUSD", "database", "M12")
