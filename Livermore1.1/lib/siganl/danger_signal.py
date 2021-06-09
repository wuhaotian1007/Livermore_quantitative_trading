# -*- encoding: utf-8 -*-
'''
@File    :   danger_siganl.py
@Time    :   2021/05/21 18:39:02
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3


class danger_signal:
    def __init__(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("select ID from STOCK_LIST where TRENDSIGNAL > 0 ")
        fir_ID = c.fetchall()[0][0]
        c.execute(
            "select ID,price,record,column,date from STOCK_LIST where NAME = '{0}' and ID > {1}".format('comb', fir_ID))
        info_list = c.fetchall()
        for info in info_list:
            # 最新价格信息
            ID = info[0]
            price = info[1]
            record = info[2]
            column = info[3]
            date = info[4]
            # 获取同一天XAUUSD的volume
            c.execute(
                "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(date, "XAUUSD"))
            volume = c.fetchall()[0][0]
            # 上一被记录点的信息
            c.execute(
                "select date,column from STOCK_LIST where record = {0} and ID < {1} and NAME = '{2}'".format(1, ID, "comb"))
            last_info = c.fetchall()[-1]
            last_date = last_info[0]
            last_column = last_info[1]
            # 获取同一天XAUUSD的volume
            c.execute(
                "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(last_date, "XAUUSD"))
            last_volume = c.fetchall()[0][0]

            # 最新趋势状态栏信息
            c.execute(
                "select TRENDSIGNAL,COLUMN from STOCK_LIST where ID <= {0} and TRENDSIGNAL > {1}".format(ID, 0))
            last_info = c.fetchall()
            last_trend_signal = last_info[-1][0]
            last_column = last_info[-1][1]

            # 当最新一个趋势状态栏为下降趋势结束时
            if last_trend_signal in (3, 30, 5, 50):
                # 下降趋势最新关键点价格若存在
                c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                    4, 1, "comb", ID))
                last_down_price_list = c.fetchall()
                if last_down_price_list:
                    last_down_price = last_down_price_list[-1][0]
                    # 当此状态栏记录在下降趋势栏时
                    if last_column == 4:
                        if price <= last_down_price - 9 or column * record == 4:
                            # 根据volume条件记录危险信号
                            if volume > last_volume * 0.99:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))
                    # 当此时状态记录在自然回撤栏时
                    elif last_column == 5:
                        if price <= last_down_price - 9 or column * record == 5:
                            # 根据volume条件记录危险信号
                            if volume > last_volume * 0.99:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))

            # 当最新一个趋势状态栏为下降趋势恢复时
            elif last_trend_signal in (6, 7, 60, 70):
                # 下降趋势最新关键点价格若存在,最新价格上升到下降趋势栏最新关键点以上3点则记录危险信号
                c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                    4, 1, "comb", ID))
                last_down_price_list = c.fetchall()
                if last_down_price_list:
                    last_down_price = last_down_price_list[-1][0]
                    if price >= last_down_price + 9:
                        # 根据volume条件记录危险信号
                        if volume > last_volume * 0.99:
                            c.execute(
                                "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                        else:
                            c.execute(
                                "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))

            # 当最新一个趋势状态栏为上升趋势结束时
            if last_trend_signal in (1, 10, 7, 70):
                # 上升趋势最新关键点价格若存在
                c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                    3, 1, "comb", ID))
                last_up_price_list = c.fetchall()
                if last_up_price_list:
                    last_up_price = last_up_price_list[-1][0]
                    # 当此状态栏记录在上升趋势栏时
                    if last_column == 3:
                        if price >= last_up_price + 9 or column * record == 3:
                            # 根据volume条件记录危险信号
                            if volume > last_volume * 0.99:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))
                    # 当此时状态记录在自然回升栏时
                    elif last_column == 2:
                        if price >= last_down_price + 9 or column * record == 2:
                            # 根据volume条件记录危险信号
                            if volume > last_volume * 0.99:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))

            # 当最新一个趋势状态栏为上升趋势恢复时
            elif last_trend_signal in (2, 20, 5, 50):
                # 上升趋势最新关键点价格若存在,最新价格下跌到上升趋势栏最新关键点以上3点则记录危险信号
                c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                    3, 1, "comb", ID))
                last_up_price_list = c.fetchall()
                if last_up_price_list:
                    last_up_price = last_up_price_list[-1][0]
                    if price <= last_up_price - 9:
                        # 根据volume条件记录危险信号
                        if volume > last_volume * 0.99:
                            c.execute(
                                "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(1, ID))
                        else:
                            c.execute(
                                "update STOCK_LIST set DANGERSIGNAL = {0} where ID = {1}".format(10, ID))
        # 关闭数据库连接
        conn.commit()
        conn.close()


danger_signal("../../database/XAUUSD_DXY_TNX.db")

