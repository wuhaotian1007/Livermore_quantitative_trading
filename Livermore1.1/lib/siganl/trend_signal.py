# -*- encoding: utf-8 -*-
'''
@File    :   danger_signal.py
@Time    :   2021/05/20 14:36:43
@Author  :   Wuhaotian
@Version :   1.1
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3


class signal:
    def __init__(self, db_path):
        # 建立与组合价格db连接
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # 获取当每个趋势关键点全都出现时的最小ID
        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
            'comb', 1, 2))
        min_ID_nup = c.fetchall()[0][0]
        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
            'comb', 1, 3))
        min_ID_up = c.fetchall()[0][0]
        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
            'comb', 1, 4))
        min_ID_down = c.fetchall()[0][0]
        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
            'comb', 1, 5))
        min_ID_ndown = c.fetchall()[0][0]

        min_ID = max(min_ID_ndown, min_ID_nup, min_ID_up, min_ID_down)

        c.execute(
            "select ID,price,date,column from STOCK_LIST where NAME = '{0}' and ID > {1}".format('comb', min_ID))
        info_list = c.fetchall()
        for info in info_list:
            # 最新价格信息
            ID = info[0]
            price = info[1]
            date = info[2]
            column = info[3]
            # 获取同一天XAUUSD的volume
            c.execute(
                "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(date, "XAUUSD"))
            volume = c.fetchall()[0][0]
            trend_signal = 0
            # 上一被记录点的信息
            c.execute(
                "select price,date,column from STOCK_LIST where record = {0} and ID < {1} and NAME = '{2}'".format(1, ID, "comb"))
            last_info = c.fetchall()[-1]
            last_price = last_info[0]
            last_date = last_info[1]
            last_column = last_info[2]
            # 获取同一天XAUUSD的volume
            c.execute(
                "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(last_date, "XAUUSD"))
            last_volume = c.fetchall()[0][0]

            # 如果前一栏在上升趋势栏或自然回升栏记录，判断最新价格与前一被记录价格大小决定趋势延续或是结束
            if last_column in (2, 3):
                # 如果价格继续上升判断是否上升趋势恢复
                if price >= last_price:
                    # 最新上升趋势关键点价格
                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                        'comb', ID, 1, 3))
                    last_up_price_list = c.fetchall()
                    # 如果存在上一个keyprice,比较当前价格是否突破3点
                    if last_up_price_list:
                        last_up_price = last_up_price_list[-1][0]
                        if price >= last_up_price + 9:
                            # 比较volume后更新最新点的趋势信号
                            if volume > last_volume * 0.99:
                                trend_signal += 2
                            else:
                                trend_signal += 20
                            c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1} ".format(
                                trend_signal, ID))
                # 如果价格下降先判断上升趋势是否结束再根据当前趋势判断是否有下降趋势恢复
                if price < last_price:
                    # 如果前一记录栏为上升趋势栏
                    if last_column == 3:
                        # 最新上升趋势关键点价格
                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                            'comb', ID, 1, 3))
                        last_up_price_list = c.fetchall()
                        if last_up_price_list:
                            last_up_price = last_up_price_list[-1][0]
                            if price <= last_up_price - 9:
                                # 根据volume判断上升趋势结束记录形式
                                if volume > last_volume * 0.99:
                                    trend_signal += 1
                                else:
                                    trend_signal += 10
                                # 判断是否存在下降趋势恢复
                                if column == 4:
                                    # 最新下降趋势关键点价格
                                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                        'comb', ID, 1, 4))
                                    last_down_price_list = c.fetchall()
                                    # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                    if last_down_price_list:
                                        last_down_price = last_down_price_list[-1][0]
                                        if price <= last_down_price - 9:
                                            if volume > last_volume * 0.99:
                                                trend_signal += 6
                                            else:
                                                trend_signal += 60
                                # 更新最新一点趋势信号
                                c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1}".format(
                                    trend_signal, ID))

                    # 如果前一记录栏为自然回升栏
                    if last_column == 2:
                        # 最新自然回升栏已记录价格
                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                            'comb', ID, 1, 2))
                        last_up_price_list = c.fetchall()
                        if last_up_price_list:
                            last_up_price = last_up_price_list[-1][0]
                            if price <= last_up_price - 9:
                                # 根据volume判断上升趋势结束记录形式
                                if volume > last_volume * 0.99:
                                    trend_signal += 1
                                else:
                                    trend_signal += 10
                                # 判断是否存在下降趋势恢复
                                if column == 4:
                                    # 最新下降趋势关键点价格
                                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                        'comb', ID, 1, 4))
                                    last_down_price_list = c.fetchall()
                                    # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                    if last_down_price_list:
                                        last_down_price = last_down_price_list[-1][0]
                                        if price <= last_down_price - 9:
                                            if volume > last_volume * 0.99:
                                                trend_signal += 6
                                            else:
                                                trend_signal += 60
                                # 更新最新一点趋势信号
                                c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1}".format(
                                    trend_signal, ID))

        # 如果前一栏在下降趋势栏或自然回撤栏记录，判断最新价格与前一被记录价格大小决定趋势延续或是结束
            if last_column in (4, 5):
                # 如果价格继续下降判断是否下降趋势恢复
                if price <= last_price:
                    # 最新下降趋势关键点价格
                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                        'comb', ID, 1, 4))
                    last_down_price_list = c.fetchall()
                    # 如果存在上一个keyprice,比较当前价格是否向下突破3点
                    if last_down_price_list:
                        last_down_price = last_down_price_list[-1][0]
                        if price <= last_down_price - 9:
                            # 比较volume后更新最新点的趋势信号
                            if volume > last_volume * 0.99:
                                trend_signal += 6
                            else:
                                trend_signal += 60
                            c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1} ".format(
                                trend_signal, ID))
                # 如果价格上升先判断下降趋势是否结束再根据当前趋势判断是否有上升趋势恢复
                if price > last_price:
                    # 如果前一记录栏为下降趋势栏
                    if last_column == 4:
                        # 最新下降趋势关键点价格
                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                            'comb', ID, 1, 4))
                        last_down_price_list = c.fetchall()
                        if last_down_price_list:
                            last_down_price = last_down_price_list[-1][0]
                            if price >= last_down_price + 9:
                                # 根据volume判断上升趋势结束记录形式
                                if volume > last_volume * 0.99:
                                    trend_signal += 3
                                else:
                                    trend_signal += 30
                                # 判断是否存在上升趋势恢复
                                if column == 3:
                                    # 最新上升趋势关键点价格
                                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                        'comb', ID, 1, 3))
                                    last_up_price_list = c.fetchall()
                                    # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                    if last_up_price_list:
                                        last_up_price = last_up_price_list[-1][0]
                                        if price >= last_up_price + 9:
                                            if volume > last_volume * 0.99:
                                                trend_signal += 2
                                            else:
                                                trend_signal += 20
                                # 更新最新一点趋势信号
                                c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1}".format(
                                    trend_signal, ID))

                    # 如果前一记录栏为自然回撤栏
                    if last_column == 5:
                        # 最新自然回撤栏已记录价格
                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                            'comb', ID, 1, 5))
                        last_down_price_list = c.fetchall()
                        if last_down_price_list:
                            last_down_price = last_down_price_list[-1][0]
                            if price >= last_down_price + 9:
                                # 根据volume判断上升趋势结束记录形式
                                if volume > last_volume * 0.99:
                                    trend_signal += 3
                                else:
                                    trend_signal += 30
                                # 判断是否存在上升趋势恢复
                                if column == 3:
                                    # 最新上升趋势关键点价格
                                    c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                        'comb', ID, 1, 3))
                                    last_up_price_list = c.fetchall()
                                    # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                    if last_up_price_list:
                                        last_up_price = last_up_price_list[-1][0]
                                        if price >= last_up_price + 9:
                                            if volume > last_volume * 0.99:
                                                trend_signal += 2
                                            else:
                                                trend_signal += 20
                                # 更新最新一点趋势信号
                                c.execute("update STOCK_LIST set TRENDSIGNAL = {0} where ID = {1}".format(
                                    trend_signal, ID))
        # 关闭数据库连接
        conn.commit()
        conn.close()


signal("../../database/XAUUSD_DXY_TNX.db")
signal("../../database/XAUUSD_TNX.db")
signal("../../database/XAUUSD_DXY.db")
