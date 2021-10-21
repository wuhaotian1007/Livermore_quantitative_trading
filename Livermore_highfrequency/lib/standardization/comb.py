# -*- encoding: utf-8 -*-
'''
@File    :   comb.py
@Time    :   2021/10/02 20:53:54
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
from sqlite3.dbapi2 import sqlite_version
import sys
import time
from datetime import date, datetime
from collections import defaultdict
import pandas as pd
import numpy as np
import csv
import sqlite3


class comb:
    def __init__(self, database_path, XAU_ceof, DXY_coef, TNX_coef, constant, match_mode, process_length):
        """
        传入参数
        database_path ：数据库路径
        constant : 组合价格常数
        """
        # 获取操作频率
        frequency = database_path[-4]

        # 建立打印结果txt BEM = best effort match, SM = strict match
        doc_bem = open("out_BEM.txt", "w")
        doc_sm = open("out_SM.txt", "w")

        if frequency == "H":
            half_path = database_path[:-4]
            if DXY_coef != 0:
                half_path += "DXY_"
            if TNX_coef != 0:
                half_path += "TNX_"

            # 建立日线bem交易所数据库连接
            conn_D1_bem_exchange_db = sqlite3.connect(
                half_path + "D1_bem_exchange.db")
            cur_D1_bem_exchange_db = conn_D1_bem_exchange_db.cursor()

            # 创建日线汇总table
            cur_D1_bem_exchange_db.execute('''CREATE TABLE IF NOT EXISTS STOCK_LIST
                (ID             INTEGER PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                PRICE           UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                RECORD          UNSIGNED INT   DEFAULT 0,
                COLUMN          UNSIGNED INT   DEFAULT 0,
                KEYSPOT         UNSIGNED INT   DEFAULT 0);''')

            # 建立日线美东sm数据库连接
            conn_D1_sm_est_db = sqlite3.connect(half_path + "D1_sm_est.db")
            cur_D1_sm_est_db = conn_D1_sm_est_db.cursor()

            # 创建日线汇总table
            cur_D1_sm_est_db.execute('''CREATE TABLE IF NOT EXISTS STOCK_LIST
                (ID             INTEGER PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                PRICE           UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                RECORD          UNSIGNED INT   DEFAULT 0,
                COLUMN          UNSIGNED INT   DEFAULT 0,
                KEYSPOT         UNSIGNED INT   DEFAULT 0);''')

        # 建立数据库连接
        conn_db = sqlite3.connect(database_path)
        cur_db = conn_db.cursor()

        # 选择数据库中共有的最大时间戳
        cur_db.execute("select min(TIMESTICKER) from XAUUSD_list")
        min_ts_XAUUSD = cur_db.fetchone()[0]

        cur_db.execute("select min(TIMESTICKER) from TNX_list")
        min_ts_TNX = cur_db.fetchone()[0] + 25200

        cur_db.execute("select min(TIMESTICKER) from DXY_list")
        min_ts_DXY = cur_db.fetchone()[0] + 25200

        max_ts = max(min_ts_XAUUSD, min_ts_DXY, min_ts_TNX)

        # 以XAUUSD为基准开始进行组合价格遍历
        aggr_volume = 0
        last_ts_str = 0

        cur_db.execute(
            "select DATE, CLOSE, TIMESTICKER, VOLUME from XAUUSD_list where TIMESTICKER >= {0}".format(max_ts))
        XAUUSD_data_list = cur_db.fetchall()
        if process_length == "all":
            print("开始首次组合价格全处理")
        else:
            XAUUSD_data_list = XAUUSD_data_list[-process_length:]

        if match_mode == "best_effort_match":
            # 新建组合价格table_list
            cur_db.execute('''CREATE TABLE IF NOT EXISTS comb_bem
                (DATE           TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                PRICE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                CUR_VOLUME      UNSIGNED INT   DEFAULT 0,
                AGGR_VOLUME     UNSIGNED INT   DEFAULT 0);''')

            # 对XAUUSD列表开始遍历
            for XAUUSD_data in XAUUSD_data_list:
                # XAU收盘价，时间戳，当前时间的volume
                date = XAUUSD_data[0]
                XAUUSD_close = XAUUSD_data[1]
                ts = XAUUSD_data[2]
                cur_volume = XAUUSD_data[3]

                # 小时时间
                hour = date[11:13]

                # 将时间戳转换为当天日期 用于加总当日volume
                ts_str = time.strftime("%Y-%m-%d", time.localtime(ts))

                # 根据时间戳时区调整7小时候选取与之最接近的DXY与TNX价格用于组合
                cur_db.execute(
                    "select CLOSE from DXY_list where TIMESTICKER <= {0}".format(ts - 25200))
                DXY_close = cur_db.fetchall()[-1][0]

                cur_db.execute(
                    "select CLOSE from TNX_list where TIMESTICKER <= {0}".format(ts - 25200))
                TNX_close = cur_db.fetchall()[-1][0]

                # 生成组合价格
                comb_price = XAUUSD_close * XAU_ceof + DXY_close * \
                    DXY_coef + TNX_close * TNX_coef + constant
                comb_price = round(comb_price, 2)

                # 当日volume加总
                if ts_str == last_ts_str:
                    aggr_volume += cur_volume
                else:
                    aggr_volume = cur_volume

                last_ts_str = ts_str

                # 组合价格入库
                cur_db.execute(
                    "select TIMESTICKER from comb_bem where TIMESTICKER == {}".format(ts))
                ts_exist = cur_db.fetchone()
                if not ts_exist:
                    cur_db.execute("insert into comb_bem(DATE, NAME, PRICE, TIMESTICKER, CUR_VOLUME, AGGR_VOLUME) VALUES(?, ?, ?, ?, ?, ?) ",
                                   (date, "comb", comb_price, ts, cur_volume, aggr_volume))

                    # 如果为bem_exchange的23:00时记录日线
                    if hour == "23" and frequency == "H":
                        cur_D1_bem_exchange_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE, VOLUME) VALUES(?, ?, ?, ?, ?) ",
                                                       ("XAUUSD", ts_str, ts, XAUUSD_close, aggr_volume))
                        cur_D1_bem_exchange_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE) VALUES(?, ?, ?, ?) ",
                                                       ("DXY", ts_str, ts, DXY_close))
                        cur_D1_bem_exchange_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE) VALUES(?, ?, ?, ?) ",
                                                       ("TNX", ts_str, ts, TNX_close))
                        cur_D1_bem_exchange_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE, VOLUME) VALUES(?, ?, ?, ?, ?) ",
                                                       ("comb", ts_str, ts, comb_price, aggr_volume))
                        print("bem_exchange"+ts_str)

                    # 打印结果
                    print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                          str(cur_volume) + "\t" + str(aggr_volume))
                    print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                          str(cur_volume) + "\t" + str(aggr_volume), file=doc_bem)
                else:
                    print("重复输入"+date)

        elif match_mode == "strict_match":
            # 新建组合价格table_list
            cur_db.execute('''CREATE TABLE IF NOT EXISTS comb_sm
                (DATE           TEXT           PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                PRICE           UNSIGNED INT   NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                CUR_VOLUME      UNSIGNED INT   DEFAULT 0,
                AGGR_VOLUME     UNSIGNED INT   DEFAULT 0);''')

            # 对XAUUSD列表开始遍历
            for XAUUSD_data in XAUUSD_data_list:
                # XAU收盘价，时间戳，当前时间的volume
                date = XAUUSD_data[0]
                XAUUSD_close = XAUUSD_data[1]
                ts = XAUUSD_data[2]
                cur_volume = XAUUSD_data[3]

                # 小时时间
                hour = date[11:13]

                # 将时间戳转换为当天日期 用于加总当日volume
                ts_str = time.strftime("%Y-%m-%d", time.localtime(ts))

                # 根据时间戳时区调整7小时候选取与之最接近的DXY与TNX价格用于组合
                cur_db.execute(
                    "select CLOSE from DXY_list where TIMESTICKER == {0}".format(ts - 25200))
                DXY_close = cur_db.fetchone()

                cur_db.execute(
                    "select CLOSE from TNX_list where TIMESTICKER == {0}".format(ts - 25200))
                TNX_close = cur_db.fetchone()

                # 当三者价格同时存在时取组合价格
                if DXY_close and TNX_close:
                    DXY_close = DXY_close[0]
                    TNX_close = TNX_close[0]

                    # 生成组合价格
                    comb_price = XAUUSD_close * XAU_ceof + DXY_close * \
                        DXY_coef + TNX_close * TNX_coef + constant
                    comb_price = round(comb_price, 2)

                    # 当日volume加总
                    if ts_str == last_ts_str:
                        aggr_volume += cur_volume
                    else:
                        aggr_volume = cur_volume

                    last_ts_str = ts_str

                    # 组合价格入库
                    cur_db.execute(
                        "select TIMESTICKER from comb_sm where TIMESTICKER == {}".format(ts))
                    ts_exist = cur_db.fetchone()

                    if not ts_exist:
                        cur_db.execute("insert into comb_sm(DATE, NAME, PRICE, TIMESTICKER, CUR_VOLUME, AGGR_VOLUME) VALUES(?, ?, ?, ?, ?, ?) ",
                                       (date, "comb", comb_price, ts, cur_volume, aggr_volume))

                        # 如果为sm_est的21:00时(此时TNX为14:00）的收盘价记录日线
                        if hour == "21" and frequency == "H":
                            cur_D1_sm_est_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE, VOLUME) VALUES(?, ?, ?, ?, ?) ",
                                                     ("XAUUSD", ts_str, ts-50400, XAUUSD_close, aggr_volume))
                            cur_D1_sm_est_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE) VALUES(?, ?, ?, ?) ",
                                                     ("DXY", ts_str, ts-50400, DXY_close))
                            cur_D1_sm_est_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE) VALUES(?, ?, ?, ?) ",
                                                     ("TNX", ts_str, ts-50400, TNX_close))
                            cur_D1_sm_est_db.execute("insert into STOCK_LIST(NAME, DATE, TIMESTICKER, PRICE, VOLUME) VALUES(?, ?, ?, ?, ?) ",
                                                     ("comb", ts_str, ts-50400, comb_price, aggr_volume))
                            print("sm_est"+ts_str)
                        # 打印结果
                        print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                              str(cur_volume) + "\t" + str(aggr_volume))
                        print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                              str(cur_volume) + "\t" + str(aggr_volume), file=doc_sm)
                    else:
                        print("重复输入"+date)

        # 关闭数据库连接
        conn_db.commit()
        conn_db.close()

        if frequency == "H":
            conn_D1_bem_exchange_db.commit()
            conn_D1_bem_exchange_db.close()
            conn_D1_sm_est_db.commit()
            conn_D1_sm_est_db.close()

        doc_sm.close()
        doc_bem.close()

        print("组合价格生成完毕")


if __name__ == "__main__":
    comb(r"database\XAUUSD_H.db", 3/7, -3 /
         0.3, -3/0.03, 600, "best_effort_match", "all")
    comb(r"database\XAUUSD_H.db", 3/7, -3 /
         0.3, -3/0.03, 600, "strict_match", "all")
    comb(r"database\XAUUSD_M.db", 3/7, -3 /
         0.3, -3/0.03, 600, "best_effort_match", "all")
    comb(r"database\XAUUSD_M.db", 3/7, -3 /
         0.3, -3/0.03, 600, "strict_match", "all")
