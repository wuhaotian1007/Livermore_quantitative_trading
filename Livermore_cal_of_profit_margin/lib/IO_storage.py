# -*- encoding: utf-8 -*-
'''
@File    :   IO_storage.py
@Time    :   2021/06/23 17:44:42
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import csv
import pandas as pd
import os
import openpyxl
import sqlite3
import time
import datetime


class IO_storage:
    def __init__(self, category_db_path, trading_record_db_path, trading_history_input_path, XAUUSD_db_path):
        # 读取交易品类信息
        conn_category = sqlite3.connect(category_db_path)
        cur_category = conn_category.cursor()

        # 创建db收集策略交易信息
        conn_storage = sqlite3.connect(trading_record_db_path)
        cur_storage = conn_storage.cursor()
        cur_storage.execute('''CREATE TABLE IF NOT EXISTS history_list
                (ID                INTEGER        PRIMARY KEY,
                trading_time       TEXT           NOT NULL,
                trading_currency   TEXT           NOT NULL,
                trading_type       TEXT           NOT NULL,
                trading_volume     FLOAT          NOT NULL,
                trading_price      FLOAT          NOT NULL,
                close_time         TEXT           NOT NULL,
                close_price        FLOAT          NOT NULL,
                service_charge     FLOAT          NOT NULL,
                inventory_charge   FLOAT          NOT NULL,
                advance_charge     FLOAT          NOT NULL,
                net_profit         FLOAT          NOT NULL,
                high               FLOAT          NOT NULL,
                low                FLOAT          NOT NULL,
                max_profit         FLOAT          NOT NULL,
                max_loss           FLOAT          NOT NULL,
                nominal_profit_margin     TEXT          NOT NULL,
                total_profit_margin       TEXT          NOT NULL,
                surplus            FLOAT          NOT NULL,
                note               TEXT           NULL);''')

        trading_history_data = pd.read_excel(trading_history_input_path,
                             sheet_name=0, header=1)

        # 读取初始净值
        wb = openpyxl.load_workbook(trading_history_input_path)
        ws = wb["Sheet1"]
        initial_nv = ws.cell(row=1, column=2).value

        # 逐行在df中读取数据并计算后入库
        for indexs in trading_history_data.index:

            # excel直接输入参数
            trading_time = trading_history_data.loc[indexs].values[0]
            trading_currency = trading_history_data.loc[indexs].values[1]
            trading_type = trading_history_data.loc[indexs].values[2]
            trading_volume = trading_history_data.loc[indexs].values[3]
            trading_price = trading_history_data.loc[indexs].values[4]
            close_time = trading_history_data.loc[indexs].values[5]
            close_price = trading_history_data.loc[indexs].values[6]
            service_charge = trading_history_data.loc[indexs].values[7]
            inventory_charge = trading_history_data.loc[indexs].values[8]
            note = trading_history_data.loc[indexs].values[9]

            # 查询交易品类信息数据库
            cur_category.execute(
                "select * from currency_list where name = '{}'".format(trading_currency))
            currency_info = cur_category.fetchone()
            closing_line = currency_info[2]
            leverage_ratio = currency_info[3]
            volume_per_hand = currency_info[4]
            soft_limit = currency_info[5]
            points = currency_info[6]

            # 输出参数
            # 预付款
            if trading_currency == "XAUUSD":
                advance_charge = volume_per_hand * trading_price * trading_volume / leverage_ratio
            else:
                advance_charge = volume_per_hand * trading_volume / leverage_ratio

            # 净利润
            if trading_type == "buy":
                net_profit = (close_price - trading_price) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                net_profit = round(net_profit, 2)
            elif trading_type == "sell":
                net_profit = (trading_price - close_price) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                net_profit = round(net_profit, 2)

            # 净值结余和上一笔净值结余
            if indexs == 0:
                surplus = initial_nv + net_profit
                last_surplus = surplus
            else:
                last_surplus = surplus
                surplus += net_profit

            # 连接对应货币的交易数据
            conn_XAUUSD = sqlite3.connect(XAUUSD_db_path)
            cur_XAUUSD = conn_XAUUSD.cursor()

            # 将时间转换为时间戳格式
            trading_time_array = time.strptime(
                trading_time, "%Y.%m.%d %H:%M:%S")
            trading_time_stamp = int(time.mktime(trading_time_array))
            close_time_array = time.strptime(close_time, "%Y.%m.%d %H:%M:%S")
            close_time_stamp = int(time.mktime(close_time_array))

            # 期间最高价
            cur_XAUUSD.execute("select max(high) from XAUUSD_list where TIMESTICKER < {0} and TIMESTICKER > {1}".format(
                close_time_stamp, trading_time_stamp))
            high = cur_XAUUSD.fetchone()[0]

            # 期间最低价
            cur_XAUUSD.execute("select min(low) from XAUUSD_list where TIMESTICKER < {0} and TIMESTICKER > {1}".format(
                close_time_stamp, trading_time_stamp))
            low = cur_XAUUSD.fetchone()[0]

            # 极限利润
            if trading_type == "buy":
                max_profit = (high - trading_price) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                max_profit = round(max_profit, 2)
            elif trading_type == "sell":
                max_profit = (trading_price - low) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                max_profit = round(max_profit, 2)

            # 极限亏损
            if trading_type == "buy":
                max_loss = (low - trading_price) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                max_loss = round(max_loss, 2)
            elif trading_type == "sell":
                max_loss = (trading_price - high) * volume_per_hand * \
                    trading_volume + service_charge + inventory_charge
                max_loss = round(max_loss, 2)

            # 名义利润率
            nominal_profit_margin = net_profit/(advance_charge + abs(max_loss))
            nominal_profit_margin = "%.2f%%" % (nominal_profit_margin * 100)

            # 总利润率
            total_profit_margin = net_profit/last_surplus
            total_profit_margin = "%.2f%%" % (total_profit_margin * 100)

            cur_storage.execute("insert into history_list(trading_time, trading_currency, trading_type, trading_volume, trading_price, close_time, close_price, service_charge, inventory_charge, advance_charge, net_profit, surplus, high, low, max_profit, max_loss, nominal_profit_margin, total_profit_margin, note) \
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?) ", (trading_time, trading_currency, trading_type, trading_volume, trading_price, close_time, close_price, service_charge, inventory_charge, advance_charge, net_profit, surplus, high, low, max_profit, max_loss, nominal_profit_margin, total_profit_margin, note))

        # 保存并关闭数据库连接
        conn_category.commit()
        conn_category.close()

        conn_XAUUSD.commit()
        conn_XAUUSD.close()

        conn_storage.commit()
        conn_storage.close()

        print("交易历史计算完成，并成功入库")
