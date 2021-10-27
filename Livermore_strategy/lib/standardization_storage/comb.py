# -*- encoding: utf-8 -*-
'''
@File    :   comb.py
@Time    :   2021/05/03 21:33:07
@Author  :   Wuhaotian
@Version :   1.1
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
    def __init__(self, database_path, constant):
        """
        传入参数
        database_path ：数据库路径
        constant : 组合价格常数
        """

        '''trading_category_db_path : 交易品类db路径
         trading_comb_db_path : 交易组合db路径
        '''
        trading_category_db_path = database_path + r"\trading_category.db"
        trading_comb_db_path = database_path + r"\trading_comb.db"

        conn_trading_category = sqlite3.connect(trading_category_db_path)
        cur_trading_category = conn_trading_category.cursor()

        conn_trading_comb = sqlite3.connect(trading_comb_db_path)
        cur_trading_comb = conn_trading_comb.cursor()

        cur_trading_comb.execute("select * from trading_comb_list")
        trading_comb_list = cur_trading_comb.fetchall()

        def fraction(i: str):
            numerator = float(i.split("/")[0])
            denominator = float(i.split("/")[1])
            result = numerator / denominator
            return result
        
        # 循环交易组合列表
        for trading_comb in trading_comb_list:
            trading_comb_ID = trading_comb[0]
            comb_category = trading_comb[2].split(",")
            trading_category_ID = trading_comb[3]

            # 读取交易组合的交易品类信息
            cur_trading_category.execute(
                "select category_name,exact_digit from trading_category_list where trading_category_ID = {0}".format(trading_category_ID))
            trading_category_info = cur_trading_category.fetchone()
            core = trading_category_info[0]
            exact_digit = trading_category_info[1]

            # 组合价格核心元素路径与辅助元素路径
            core_db_path = database_path + r'\{0}.db'.format(core)
            aux_db_path = database_path + r'\{0}_AUX.db'.format(core)

            # 与组合价格核心元素数据库建立连接
            conn_core = sqlite3.connect(core_db_path)
            cur_core = conn_core.cursor()

            # 核心元素所需信息列表
            cur_core.execute(
                "select TIMESTICKER,CLOSE,DATE,VOLUME from {0}_list".format(core))
            core_list = cur_core.fetchall()

            auxiliary_list = []
            coefficient_list = []

            # 读取核心元素信息
            core_element = comb_category[0].split("=")
            core_coef = fraction(core_element[1])

            # 读取辅助元素信息
            for i in range(1, len(comb_category)):
                aux_element = comb_category[i].split("=")
                auxiliary_list.append(aux_element[0])
                coefficient_list.append(fraction(aux_element[1]))

             # 组合价格辅助元素量quant
            quant = len(auxiliary_list)

            # 组合名称
            f_name = str(trading_comb_ID) + r"_" + core
            for i in range(quant):
                f_name += "_" + auxiliary_list[i]

            # 与原始数据数据库建立连接
            conn_aux = sqlite3.connect(aux_db_path)
            cur_aux = conn_aux.cursor()

            # 与组合价格存储数据库建立连接
            comb_db_path = database_path + r'\trading_comb_info\{0}.db'.format(f_name)
            conn_comb = sqlite3.connect(comb_db_path)
            cur_comb = conn_comb.cursor()

            # 创建表STOCK_LIST
            '''
                - ID：自增ID
                - 日期：交易日，格式为2021-02-24
                - 收盘价：该股票在对应交易日的收盘价，精确到小数点后3位，四舍五入
                - “是否记录”：unsigned int，1为需要记录，0为不需要记录；第一条记录为1，其余默认为0
                - “记录所在栏”：以表名来命名默认值，增加新股票时都新建全量6张不同初始状态的表
                - 不记录：0
                - 次级回升栏:1
                - 自然回升栏:2
                - 上升趋势栏:3
                - 下降趋势栏:4
                - 自然回撤栏:5
                - 次级回撤栏:6
                - “是否关键点”：unsigned int，1为是，0为否。默认值为0，需要通过更新逻辑来更新
                - “趋势信号”：unsigned int，1为上升趋势结束，2为上升趋势恢复，3为下降趋势结束，4为下降趋势恢复，5为危险信号，末位加0表示volume不足
            '''
            cur_comb.execute('''CREATE TABLE IF NOT EXISTS STOCK_LIST
                (ID             INTEGER PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                PRICE           UNSIGNED INT   NOT NULL,
                VOLUME          UNSIGNED INT   DEFAULT 0,
                RECORD          UNSIGNED INT   DEFAULT 0,
                COLUMN          UNSIGNED INT   DEFAULT 0,
                KEYSPOT         UNSIGNED INT   DEFAULT 0);''')

            # 从核心元素开始迭代
            for data in core_list:
                # 初始状态时间戳，价格，组合价格为价格乘以核心元素参数
                ts = data[0]
                ts_tuple = (ts,)
                price = data[1]
                date = data[2]
                volume = data[3]
                comb = price * core_coef + constant

                # 将核心数据插入组合价格表中
                cur_comb.execute("insert into STOCK_LIST( NAME, DATE, TIMESTICKER, PRICE, VOLUME) \
                        VALUES(?, ?, ?, ?, ?) ", (core, date, ts, price, volume))

                # 根据系数和价格求组合价格
                for i in range(quant):
                    # 辅助元素名称和系数
                    aux_name = auxiliary_list[i]
                    aux_coef = coefficient_list[i]
                    # 选中辅助元素所在列表的时间戳
                    cur_core.execute(
                        "select TIMESTICKER from {0}_list".format(aux_name))
                    ts_list = cur_core.fetchall()
                    # 查询核心元素日期是否在辅助元素时间戳列表中
                    # 若时间戳在列表中，则组合价格加上辅助元素价格
                    if ts_tuple in ts_list:
                        cur_core.execute(
                            "select CLOSE from {0}_list where TIMESTICKER = {1}".format(aux_name, ts))
                        aux_price = cur_core.fetchone()[0]
                        comb += aux_price * aux_coef

                    else:
                        # 入不在列表中建立与原始数据数据库连接，并记录辅助元素
                        cur_aux.execute(
                            "select CLOSE from {0}_list where TIMESTICKER <= {1}  ".format(aux_name, ts + 61200))
                        aux_price = cur_aux.fetchall()[-1][0]
                        comb += aux_price * aux_coef

                    # 记录辅助元素
                    cur_comb.execute("insert into STOCK_LIST( NAME, DATE, TIMESTICKER, PRICE) \
                        VALUES(?, ?, ?, ?) ", (aux_name, date, ts, aux_price))

                # 记录组合价格
                comb = round(comb, exact_digit)
                cur_comb.execute("insert into STOCK_LIST( NAME, DATE, TIMESTICKER, PRICE) \
                        VALUES(?, ?, ?, ?) ", ('comb', date, ts, comb))

            # 关闭数据库连接
            conn_comb.commit()
            conn_comb.close()
            print("交易组合{0}标准价格存储成功".format(trading_comb_ID))


if __name__ == "__main__":
    comb("database", 600)
