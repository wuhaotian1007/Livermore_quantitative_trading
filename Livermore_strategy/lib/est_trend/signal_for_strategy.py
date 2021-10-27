# -*- encoding: utf-8 -*-
'''
@File    :   signal_for_strategy.py
@Time    :   2021/09/04 15:32:52
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3
import os
from sqlite3.dbapi2 import connect


class signal_for_strategy:
    def __init__(self, database_path):
        '''
        新建一个list 专门用于策略模拟时的买入信号输入
        '''
        trading_comb_info_path = database_path + r"/trading_comb_info"
        trading_comb_signal_path = database_path + r"/trading_comb_signal"

        for file in os.listdir(trading_comb_info_path):
            trading_comb_ID = file[0]

            # 建立交易组合信号数据库的连接
            trading_comb_signal_db_path = trading_comb_signal_path + \
                r"/" + trading_comb_ID + r".db"
            conn_trading_comb_signal = sqlite3.connect(
                trading_comb_signal_db_path)
            cur_trading_comb_signal = conn_trading_comb_signal.cursor()

            # 建立交易组合信息数据库的连接
            trading_comb_info_db_path = trading_comb_info_path + r"/" + file
            conn_trading_comb_info = sqlite3.connect(trading_comb_info_db_path)
            cur_trading_comb_info = conn_trading_comb_info.cursor()

            cur_trading_comb_signal.execute('''CREATE TABLE IF NOT EXISTS TREND_FOR_STRATEGY
                        (ID                INTEGER        PRIMARY KEY,
                        TRADING_CATEGORY   TEXT           NOT NULL,
                        DATE               TEXT           NOT NULL,
                        TIMESTICKER        UNSIGNED INT   NOT NULL,
                        TRENDSIGNAL        TEXT           DEFAULT 0,
                        AUG                INT            NULL,
                        CUR                FLOAT          NOT NULL,
                        CLOSE              FLOAT          NOT NULL,
                        SMA_5d             FLOAT          NOT NULL,
                        SMA_10d            FLOAT          NOT NULL,
                        SMA_30d            FLOAT          NOT NULL,
                        SMA_200d           FLOAT          NOT NULL);''')

            # 获取交易品类 为file文件名数字后的第一个名称
            trading_category = file.split("_")[1]

            # 建立交易品类的价格信心数据库连接
            conn_trading_category_info = sqlite3.connect(
                database_path + "/" + trading_category + "_D1_max.db")
            cur_trading_category_info = conn_trading_category_info.cursor()

            # 读取trading_comb_info下文件COMB_TREND_table的所有趋势信号
            cur_trading_comb_info.execute("select * from COMB_TREND")
            trading_comb_info_list = cur_trading_comb_info.fetchall()

            for info in trading_comb_info_list:
                ID = info[0]
                DATE = info[2]
                TIMESTICKER = info[3]
                TRENDSIGNAL = info[4]
                AUG = info[5]
                danger_signal_date = info[6]

                # 如果趋势信号是XX的危险信号，找到对应日期的趋势信号种类
                if TRENDSIGNAL in [5, 50]:
                    cur_trading_comb_info.execute(
                        "select TRENDSIGNAL from COMB_TREND where DATE = '{0}'".format(danger_signal_date))
                    dangerous_siganl = cur_trading_comb_info.fetchone()[0]
                    TRENDSIGNAL = str(dangerous_siganl) + str(TRENDSIGNAL)

                # 如果趋势信号是当前危险信号，找到当前所在的记录栏
                if TRENDSIGNAL in [6, 60]:
                    cur_trading_comb_info.execute(
                        "select COLUMN from STOCK_LIST where DATE = '{0}' AND NAME = 'comb'".format(DATE))
                    dangerous_column = cur_trading_comb_info.fetchone()[0]
                    if dangerous_column == 3:
                        TRENDSIGNAL = str(TRENDSIGNAL) + "u"
                    elif dangerous_column == 4:
                        TRENDSIGNAL = str(TRENDSIGNAL) + "d"

                # 获取趋势信号天的收盘价
                cur_trading_category_info.execute(
                    "select close from {0}_list where TIMESTICKER = {1}".format(trading_category, TIMESTICKER))
                CLOSE = cur_trading_category_info.fetchone()[0]

                # 获取趋势信号天后一天的实时价格（开盘价）
                cur_trading_category_info.execute(
                    "select ID from {0}_list where TIMESTICKER = {1}".format(trading_category, TIMESTICKER))
                last_ID = cur_trading_category_info.fetchone()[0]

                cur_trading_category_info.execute(
                    "select max(ID) from {0}_list".format(trading_category))
                max_ID = cur_trading_category_info.fetchone()[0]

                # 当不是最后一天时，实时价格为趋势信号后一天收盘价
                if last_ID != max_ID:
                    cur_trading_category_info.execute(
                        "select OPEN from {0}_list where ID = {1}".format(trading_category, last_ID + 1))
                    CUR = cur_trading_category_info.fetchone()[0]
                elif last_ID == max_ID:
                    CUR = CLOSE

                # 获取趋势信号天的各个SMA
                SMA_5d = 0
                SMA_10d = 0
                SMA_30d = 0
                SMA_200d = 0

                cur_trading_category_info.execute(
                    "select close from {0}_list where ID < {1} and ID > {2} ".format(trading_category, last_ID + 1, last_ID - 5))
                SMA_5d_list = cur_trading_category_info.fetchall()
                for price in SMA_5d_list:
                    SMA_5d += price[0]/5

                cur_trading_category_info.execute(
                    "select close from {0}_list where ID < {1} and ID > {2} ".format(trading_category, last_ID + 1, last_ID - 10))
                SMA_10d_list = cur_trading_category_info.fetchall()
                for price in SMA_10d_list:
                    SMA_10d += price[0]/10

                cur_trading_category_info.execute(
                    "select close from {0}_list where ID < {1} and ID > {2} ".format(trading_category, last_ID + 1, last_ID - 30))
                SMA_30d_list = cur_trading_category_info.fetchall()
                for price in SMA_30d_list:
                    SMA_30d += price[0]/30

                cur_trading_category_info.execute(
                    "select close from {0}_list where ID < {1} and ID > {2} ".format(trading_category, last_ID + 1, last_ID - 200))
                SMA_200d_list = cur_trading_category_info.fetchall()
                for price in SMA_200d_list:
                    SMA_200d += price[0]/200

                cur_trading_comb_signal.execute("insert into TREND_FOR_STRATEGY(ID, TRADING_CATEGORY, DATE, TIMESTICKER, TRENDSIGNAL, AUG, CUR, CLOSE, SMA_5d, SMA_10d, SMA_30d, SMA_200d) \
                            VALUES(?, ?, ?, ?, ?, ?, ?, ? ,? ,?, ?, ?) ", (ID, trading_category, DATE, TIMESTICKER, TRENDSIGNAL, AUG, CUR, CLOSE, round(SMA_5d, 2), round(SMA_10d, 2), round(SMA_30d, 2), round(SMA_200d, 2)))

            conn_trading_comb_signal.commit()
            conn_trading_comb_signal.close()
            print("交易组合{}的趋势信号已准备进入交易模拟".format(trading_comb_ID))


if __name__ == "__main__":
    signal_for_strategy("database")
