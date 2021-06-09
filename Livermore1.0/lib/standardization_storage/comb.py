# -*- encoding: utf-8 -*-
'''
@File    :   comb.py
@Time    :   2021/05/03 21:33:07
@Author  :   Wuhaotian
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
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


class comb:
    def __init__(self, core: str, core_coef: float, constant: float, **argu):
        """
        传入参数
        core : 组合价格核心名称
        core_coef : 核心元素参数
        constant : 组合价格常数
        **argu : dict [辅助元素名称：辅助元素系数]
        """
        # 组合价格辅助元素量quant
        quant = len(argu)

        # 与组合价格核心元素数据库建立连接
        conn1 = sqlite3.connect(
            'C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\database\\{0}.db'.format(core))
        c1 = conn1.cursor()

        # 核心元素所需信息列表
        c1.execute(
            "select TIMESTICKER,CLOSE,DATE,VOLUME from {0}_list".format(core))
        core_list = c1.fetchall()

        auxiliary_list = list(argu.keys())
        coefficient_list = list(argu.values())

        # 组合名称
        f_name = core
        for i in range(quant):
            f_name += "_" + auxiliary_list[i]

        # 与原始数据数据库建立连接
        conn2 = sqlite3.connect(
            "C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\database\\raw_data.db")
        c2 = conn2.cursor()

        # 与组合价格存储数据库建立连接
        conn = sqlite3.connect(
            'C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\database\\{0}.db'.format(f_name))
        c = conn.cursor()

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
        '''
        c.execute('''CREATE TABLE IF NOT EXISTS STOCK_LIST
            (ID             INTEGER PRIMARY KEY,
            NAME            TEXT           NOT NULL,
            DATE            TEXT           NOT NULL,
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
            c.execute("insert into STOCK_LIST( NAME, DATE, PRICE, VOLUME) \
                     VALUES(?, ?, ?, ?) ", (core, date, price, volume))

            # 根据系数和价格求组合价格
            for i in range(quant):
                # 辅助元素名称和系数
                aux_name = auxiliary_list[i]
                aux_coef = coefficient_list[i]
                # 选中辅助元素所在列表的时间戳
                c1.execute("select TIMESTICKER from {0}_list".format(aux_name))
                ts_list = c1.fetchall()
                # 查询核心元素日期是否在辅助元素时间戳列表中
                # 若时间戳在列表中，则组合价格加上辅助元素价格
                if ts_tuple in ts_list:
                    c1.execute(
                        "select CLOSE from {0}_list where TIMESTICKER = {1}".format(aux_name, ts))
                    aux_price = c1.fetchone()[0]
                    comb += aux_price * aux_coef

                else:
                    # 入不在列表中建立与原始数据数据库连接，并记录辅助元素
                    c2.execute(
                        "select CLOSE from {0}_list where TIMESTICKER <= {1}  ".format(aux_name, ts + 61200))
                    aux_price = c2.fetchall()[-1][0]
                    comb += aux_price * aux_coef

                # 记录辅助元素
                c.execute("insert into STOCK_LIST( NAME, DATE, PRICE) \
                     VALUES(?, ?, ?) ", (aux_name, date, aux_price))

            # 记录组合价格
            comb = round(comb, 2)
            c.execute("insert into STOCK_LIST( NAME, DATE, PRICE) \
                     VALUES(?, ?, ?) ", ('comb', date, comb))

        # 关闭数据库连接
        conn.commit()
        conn.close()


# 使用组合类
comb1 = comb("XAUUSD", 3/7, 600, DXY=- 3/0.3, TNX=- 3/0.03)
comb2 = comb("XAUUSD", 3/7, 600, DXY=- 3/0.3)
comb3 = comb("XAUUSD", 3/7, 600, TNX=- 3/0.03)
