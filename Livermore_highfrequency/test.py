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
    def __init__(self, database_path, XAU_ceof, DXY_coef, TNX_coef, constant, match_mode):
        """
        传入参数
        database_path ：数据库路径
        constant : 组合价格常数
        """
        # 建立打印结果txt BEM = best effort match, SM = strict match
        doc_bem = open("out_BEM.txt", "w")
        doc_sm = open("out_SM.txt", "w")

        # 建立数据库连接
        conn_db = sqlite3.connect(database_path)
        cur_db = conn_db.cursor()

        # 选择数据库中共有的最大时间戳
        cur_db.execute("select min(TIMESTICKER) from XAUUSD_list")
        min_ts_XAUUSD = cur_db.fetchone()[0]

        cur_db.execute("select min(TIMESTICKER) from TNX_list")
        min_ts_TNX = cur_db.fetchone()[0]

        cur_db.execute("select min(TIMESTICKER) from DXY_list")
        min_ts_DXY = cur_db.fetchone()[0]

        max_ts = max(min_ts_XAUUSD, min_ts_DXY, min_ts_TNX)

        # 以XAUUSD为基准开始进行组合价格遍历
        aggr_volume = 0
        last_ts_str = 0

        cur_db.execute(
            "select DATE, CLOSE, TIMESTICKER, VOLUME from XAUUSD_list where TIMESTICKER >= {0}".format(max_ts))
        XAUUSD_data_list = cur_db.fetchall()

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

            # 将时间戳转换为当天日期 用于加总当日volume
            ts_str = time.strftime("%Y-%m-%d", time.localtime(ts))

            # 根据时间戳时区调整7小时候选取与之最接近的DXY与TNX价格用于组合
            cur_db.execute(
                "select CLOSE from DXY_list where TIMESTICKER <= {0}".format(ts + 25200))
            DXY_close = cur_db.fetchall()[-1][0]

            cur_db.execute(
                "select CLOSE from TNX_list where TIMESTICKER <= {0}".format(ts + 25200))
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
            if ts_exist:
                cur_db.execute("insert into comb_bem(DATE, NAME, PRICE, TIMESTICKER, CUR_VOLUME, AGGR_VOLUME) VALUES(?, ?, ?, ?, ?, ?) ",
                            (date, "comb", comb_price, ts, cur_volume, aggr_volume))

            # 打印结果
            print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                str(cur_volume) + "\t" + str(aggr_volume))
            print(str(date) + "\t" + "comb" + "\t" + str(comb_price) + "\t" +
                str(cur_volume) + "\t" + str(aggr_volume), file=doc_bem)
        
        # 提交数据
        conn_db.commit()
        conn_db.close()
        
        doc_sm.close()
        doc_bem.close()
        
        print("组合价格生成完毕")


if __name__ == "__main__":
    comb(r"database\XAUUSD_H.db", 3/7, -3 /
         0.3, -3/0.03, 600, "best_effort_match")