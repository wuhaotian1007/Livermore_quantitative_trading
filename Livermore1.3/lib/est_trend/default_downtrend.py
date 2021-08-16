# -*- encoding: utf-8 -*-
'''
@File    :   sqlite.py
@Time    :   2021/04/21 18:22:39
@Author  :   Wuhaotian
@Version :   1.0
@Contact :   460205923@qq.com
'''

# here put the import lib
import sqlite3
import csv
import datetime


class def_down_XAUUSD_DXY_TNX:
    def __init__(self, database_path):
        XAUUSD_DXY_TNX_db_path = database_path + r"\XAUUSD_DXY_TNX.db"
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_DXY_TNX_db_path)
        c = conn.cursor()

        # 获取时间长度
        c.execute("SELECT max(ID) from STOCK_LIST")
        length = int(c.fetchone()[0]/4)

        # 设定第一个值 RECORD为1
        c.execute("update STOCK_LIST SET RECORD = 1 where ID < 5")

        # 设定第一个值 COLUMN为4
        c.execute("update STOCK_LIST SET COLUMN = 4 where ID < 5")

        # 创建趋势信号table
        c.execute('''CREATE TABLE IF NOT EXISTS COMB_TREND
            (ID              INTEGER        PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                TRENDSIGNAL     UNSIGNED INT   DEFAULT 0,
                AUG             TEXT           NULL,
                NOTE            TEXT           NULL);''')

        # 根据livermore操盘法则确定RECORD,COLUMN,KEYSPOT
        # i指针遍历XAUUSD

        class rule:
            def __init__(self, name, fir_ID, coefficient):
                for i in range(1, length):
                    # 获取判断所需数据
                    # ID
                    ID = fir_ID + 4 * i
                    # 价格
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ? ", (ID,))
                    price = c.fetchone()[0]
                    # 时间戳
                    c.execute(
                        "select timesticker from STOCK_LIST where ID = ? ", (ID,))
                    ts = c.fetchone()[0]

                    # 上一个被记录的ID，被记录的价格，被记录的行
                    c.execute(
                        "select max(ID) from STOCK_LIST where NAME = ? and RECORD = ?", (name, 1))
                    pre_ID = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个价格
                    pre_PRICE = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select COLUMN from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个所在栏
                    pre_COLUMN = c.fetchone()[0]

                    # 上一个趋势最后一点的ID，price
                    class pull_pre:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and COLUMN = ? and NAME = ? ", (1, pos, name))
                            ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if ID_list:
                                self.ID = ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    pre_2 = pull_pre(2)
                    pre_3 = pull_pre(3)
                    pre_4 = pull_pre(4)
                    pre_5 = pull_pre(5)

                    # 上一个趋势最后一keyspot点的ID，price
                    class pull_prekey:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and KEYSPOT = ? AND COLUMN = ? and NAME = ?", (1, 1, pos, name))
                            KEY_ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if KEY_ID_list:
                                self.ID = KEY_ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    prekey_2 = pull_prekey(2)
                    prekey_3 = pull_prekey(3)
                    prekey_4 = pull_prekey(4)
                    prekey_5 = pull_prekey(5)

                    # 定义比较函数
                    def bigger(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price >= prekey.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price >= pre.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    def smaller(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price <= prekey.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price <= pre.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    # 定义开始进入自然回撤栏的状态类

                    class begin_5:
                        def __init__(self, price):
                            # 同时在上升趋势的最后一个被记录数据下标两条红线，自然回升栏最后一个数字下标2条黑线
                            if pre_3.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_3.ID))
                            if pre_2.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_2.ID))

                            # 如果新出现的价格低于下降趋势栏最后记录的数字或低于自然回撤栏红线标记的最后一个价格3点或更多那么计入下降趋势栏，否则记录在自然回撤栏
                            if smaller(price, 4, 0, 0) or smaller(price, 5, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 4, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 5, ID))

                    # 定义开始进入自然回升栏的状态类
                    class begin_2:
                        def __init__(self, price):
                            # 同时在下降趋势的最后一个被记录数据下标2条黑线，自然回撤栏最后一个数字下标2条红线
                            if pre_4.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_4.ID))
                            if pre_5.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_5.ID))

                            # 如果新出现的价格高于上升趋势栏最后记录的数字或高于自然回升栏黑线标记的最后一个价格3点或更多那么计入上升趋势栏，否则记录在自然回升栏
                            if bigger(price, 3, 0, 0) or bigger(price, 2, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 3, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 2, ID))

                    if name == "comb":
                        # 当每个趋势关键点全都出现时
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 2))
                        min_ID_nup = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 3))
                        min_ID_up = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 4))
                        min_ID_down = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 5))
                        min_ID_ndown = c.fetchall()

                        if min_ID_down and min_ID_up and min_ID_ndown and min_ID_nup:
                            c.execute(
                                "select price, date, timesticker, column from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                date = info[1]
                                ts = info[2]
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
                                            if price >= last_up_price + 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 2
                                                else:
                                                    trend_signal = 20
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回升栏
                                        if last_column == 2:
                                            # 最新自然回升栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 2))
                                            last_up_price_list = c.fetchall()
                                            if last_up_price_list:
                                                last_up_price = last_up_price_list[-1][0]
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                    # 更新最新一点趋势信号
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

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
                                            if price <= last_down_price - 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 4
                                                else:
                                                    trend_signal = 40
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回撤栏
                                        if last_column == 5:
                                            # 最新自然回撤栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 5))
                                            last_down_price_list = c.fetchall()
                                            if last_down_price_list:
                                                last_down_price = last_down_price_list[-1][0]
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                    # 如果上一栏在上升趋势栏
                    if pre_COLUMN == 3:
                        # 如果价格大于上一价格，记录在上升趋势栏
                        if price > pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ? where ID =?", (1, 3, ID))
                        # 如果价格小于上一价格6点(或12点）更多，尝试记录在自然回撤栏）
                        elif price <= pre_PRICE - 6 * coefficient:
                            use = begin_5(price)

                    # 如果上一栏在下降趋势栏
                    elif pre_COLUMN == 4:
                        # 如果价格小于上一价格，记录在下降趋势栏
                        if price < pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 4, 0, ID))
                        # 如果价格大于上一价格6点(或12点）更多，尝试记录在自然回升栏
                        elif price >= pre_PRICE + 6 * coefficient:
                            use = begin_2(price)
                        # 其他情况不记录

                    # 如果上一栏在自然回升栏
                    elif pre_COLUMN == 2:
                        # 如果价格大于前一价格则尝试记录在自然回升栏
                        if price > pre_PRICE:
                            use = begin_2(price)
                        # 如果价格小于前一价格6点（或12点）更多则记录
                        elif price <= pre_PRICE - 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为红线且为自然回撤趋势
                            if pre_key_COLUMN == 5:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试在自然回撤栏记录
                                else:
                                    use = begin_5(price)
                            # 其余情况尝试记录在自然回撤栏
                            else:
                                use = begin_5(price)

                    # 如果上一栏在次级回升栏
                    elif pre_COLUMN == 1:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回升
                        if pre_key_COLUMN == 2:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格比前一价格低6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                        # 如果上一次keyspot为自然回撤
                        elif pre_key_COLUMN == 5:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次上升趋势最高点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (3, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格低于前一价格6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)

                    # 如果上一栏在自然回撤栏
                    elif pre_COLUMN == 5:
                        # 如果价格小于前一价格则尝试在自然回撤栏记录
                        if price < pre_PRICE:
                            use = begin_5(price)
                        # 如果价格大于前一价格6点（或12点）更多则记录
                        elif price >= pre_PRICE + 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为黑线且为自然回升趋势
                            if pre_key_COLUMN == 2:
                                # 上一次自然回升趋势最高点黑线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where KEYSPOT = ? and COLUMN = ? and NAME = ?", (1, 2, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于最高点黑线price记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试在自然回升栏记录
                                else:
                                    use = begin_2(price)
                            # 其余情况尝试在自然回升记录
                            else:
                                use = begin_2(price)

                    # 如果上一栏在次级回撤栏
                    elif pre_COLUMN == 6:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回撤
                        if pre_key_COLUMN == 5:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤最低点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (5, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回撤最低点价格高继续记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况记录尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                            # 如果价格比前一价格高6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                        # 如果上一次keyspot为自然回升
                        elif pre_key_COLUMN == 2:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    begin_5(price)
                            # 如果价格大于前一价格6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然级回升栏
                                else:
                                    use = begin_2(price)

                    # 将未记录的数据的COLUMN修改为上一个被记录的COLUMN
                    c.execute(
                        "select RECORD  from STOCK_LIST where ID = {}".format(ID))
                    whe_rec = c.fetchall()[0][0]
                    if whe_rec == 0:
                        c.execute("select max(ID) from STOCK_LIST where ID < ? and NAME = ? and RECORD = ?",
                                  (ID, name, 1))
                        last_rec_ID = c.fetchall()[0][0]
                        c.execute(
                            "select COLUMN from STOCK_LIST where ID = ?", (last_rec_ID,))
                        last_rec_col = c.fetchall()[0][0]
                        c.execute("update STOCK_list set COLUMN = ? where ID = ?",
                                  (last_rec_col, ID))

                    if name == "comb":
                        c.execute(
                            "select * from COMB_TREND where TRENDSIGNAL > {0} and TIMESTICKER < {1} ".format(0, ts))
                        # 如果存在趋势信号
                        if c.fetchall():
                            c.execute(
                                "select price,record,column,date,timesticker from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                record = info[1]
                                column = info[2]
                                date = info[3]
                                ts = info[4]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(date, "XAUUSD"))
                                volume = c.fetchall()[0][0]
                                # 上一被记录点的信息
                                c.execute(
                                    "select date,ID,price from STOCK_LIST where record = {0} and ID < {1} and NAME = '{2}'".format(1, ID, "comb"))
                                last_info = c.fetchall()[-1]
                                last_date = last_info[0]
                                last_ID = last_info[1]
                                last_price = last_info[2]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(last_date, "XAUUSD"))
                                last_volume = c.fetchall()[0][0]

                                # 最新趋势状态栏信息
                                c.execute(
                                    "select TIMESTICKER from COMB_TREND where TIMESTICKER < {0} and TRENDSIGNAL > {1}".format(ts, 0))
                                last_ts = c.fetchall()[-1][0]
                                c.execute(
                                    "select column from STOCK_LIST where timesticker = {0}  and NAME = '{1}'".format(last_ts, "comb"))
                                last_column = c.fetchall()[-1][0]
                                c.execute(
                                    "select TRENDSIGNAL,DATE from COMB_TREND where TIMESTICKER = {0} and TRENDSIGNAL > {1}".format(last_ts, 0))
                                last_info_list = c.fetchall()

                                for last_info in last_info_list:
                                    last_trend_signal = last_info[0]
                                    last_trend_date = last_info[1]
                                    # 当最新一个趋势状态栏为下降趋势结束时
                                    if last_trend_signal in (3, 30):
                                        # 下降趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            4, 1, "comb", last_ID))
                                        last_down_price_list = c.fetchall()
                                        if last_down_price_list:
                                            last_down_price = last_down_price_list[-1][0]
                                            # 当此状态栏记录在下降趋势栏时
                                            if last_column == 4:
                                                if price <= last_down_price - 3 * coefficient or column * record == 4:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回撤栏时
                                            elif last_column == 5:
                                                if price <= last_down_price - 3 * coefficient or column * record == 5:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                    # 当最新一个趋势状态栏为上升趋势结束时
                                    elif last_trend_signal in (1, 10):
                                        # 上升趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            3, 1, "comb", last_ID))
                                        last_up_price_list = c.fetchall()
                                        if last_up_price_list:
                                            last_up_price = last_up_price_list[-1][0]
                                            # 当此状态栏记录在上升趋势栏时
                                            if last_column == 3:
                                                if price >= last_up_price + 3 * coefficient or column * record == 3:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回升栏时
                                            elif last_column == 2:
                                                if price >= last_down_price + 3 * coefficient or column * record == 2:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                # 当最新价格上涨并且最新价格栏在下降趋势栏
                                if price > last_price and column == 4:
                                    # 下降趋势最新关键点价格若存在,最新价格上升到下降趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        4, 1, "comb", last_ID))
                                    last_down_price_list = c.fetchall()
                                    if last_down_price_list:
                                        last_down_price = last_down_price_list[-1][0]
                                        if price >= last_down_price + 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

                                # 当最新价格下跌且最新价格在上升趋势栏
                                if price < last_price and column == 3:
                                    # 上升趋势最新关键点价格若存在,最新价格下跌到上升趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        3, 1, "comb", last_ID))
                                    last_up_price_list = c.fetchall()
                                    if last_up_price_list:
                                        last_up_price = last_up_price_list[-1][0]
                                        if price <= last_up_price - 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

                c.execute("select ID,DATE from COMB_TREND")
                trend_list = c.fetchall()
                Aug_danger = 0
                for i in trend_list:
                    ID = i[0]
                    DATE = i[1]
                    year = int(DATE[0:4])
                    month = int((DATE[5:7]))
                    day = int(DATE[8:])

                    # 如果是七月的最后一个星期一，标注8月平仓预警直到8月最后一天
                    if month == 7:
                        anyday = datetime.datetime(
                            year, month, day).strftime("%w")
                        if anyday == "1" and day + 7 > 31:
                            Aug_danger = 1

                    if month == 9:
                        Aug_danger = 0

                    if Aug_danger == 1:
                        c.execute(
                            "update COMB_TREND set AUG = {0} where ID = {1}".format(Aug_danger, ID))

        rule("XAUUSD", 1, 7/3)
        rule("DXY", 2, 0.3/3)
        rule("TNX", 3, 0.03/3)
        rule("comb", 4, 9/3)


        # 关闭数据库连接
        conn.commit()
        conn.close()

class def_down_XAU_DXY:
    def __init__(self, database_path) -> None:
        
        XAUUSD_DXY_db_path = database_path + r"\XAUUSD_DXY.db"

        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_DXY_db_path)
        c = conn.cursor()

        # 获取时间长度
        c.execute("SELECT max(ID) from STOCK_LIST")
        length = int(c.fetchone()[0]/3)

        # 设定第一个值 RECORD为1
        c.execute("update STOCK_LIST SET RECORD = 1 where ID < 4")

        # 设定第一个值 COLUMN为4
        c.execute("update STOCK_LIST SET COLUMN = 4 where ID < 4")

        # 创建趋势信号table
        c.execute('''CREATE TABLE IF NOT EXISTS COMB_TREND
            (ID              INTEGER        PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                TRENDSIGNAL     UNSIGNED INT   DEFAULT 0,
                NOTE            TEXT           NULL);''')

        # 根据livermore操盘法则确定RECORD,COLUMN,KEYSPOT
        # i指针遍历XAUUSD

        class rule:
            def __init__(self, name, fir_ID, coefficient):
                for i in range(1, length):
                    # 获取判断所需数据
                    # ID
                    ID = fir_ID + 3 * i
                    # 价格
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ? ", (ID,))
                    price = c.fetchone()[0]
                    # 时间戳
                    c.execute(
                        "select timesticker from STOCK_LIST where ID = ? ", (ID,))
                    ts = c.fetchone()[0]

                    # 上一个被记录的ID，被记录的价格，被记录的行
                    c.execute(
                        "select max(ID) from STOCK_LIST where NAME = ? and RECORD = ?", (name, 1))
                    pre_ID = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个价格
                    pre_PRICE = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select COLUMN from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个所在栏
                    pre_COLUMN = c.fetchone()[0]

                    # 上一个趋势最后一点的ID，price
                    class pull_pre:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and COLUMN = ? and NAME = ? ", (1, pos, name))
                            ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if ID_list:
                                self.ID = ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    pre_2 = pull_pre(2)
                    pre_3 = pull_pre(3)
                    pre_4 = pull_pre(4)
                    pre_5 = pull_pre(5)

                    # 上一个趋势最后一keyspot点的ID，price
                    class pull_prekey:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and KEYSPOT = ? AND COLUMN = ? and NAME = ?", (1, 1, pos, name))
                            KEY_ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if KEY_ID_list:
                                self.ID = KEY_ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    prekey_2 = pull_prekey(2)
                    prekey_3 = pull_prekey(3)
                    prekey_4 = pull_prekey(4)
                    prekey_5 = pull_prekey(5)

                    # 定义比较函数
                    def bigger(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price >= prekey.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price >= pre.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    def smaller(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price <= prekey.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price <= pre.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    # 定义开始进入自然回撤栏的状态类

                    class begin_5:
                        def __init__(self, price):
                            # 同时在上升趋势的最后一个被记录数据下标两条红线，自然回升栏最后一个数字下标2条黑线
                            if pre_3.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_3.ID))
                            if pre_2.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_2.ID))

                            # 如果新出现的价格低于下降趋势栏最后记录的数字或低于自然回撤栏红线标记的最后一个价格3点或更多那么计入下降趋势栏，否则记录在自然回撤栏
                            if smaller(price, 4, 0, 0) or smaller(price, 5, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 4, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 5, ID))

                    # 定义开始进入自然回升栏的状态类
                    class begin_2:
                        def __init__(self, price):
                            # 同时在下降趋势的最后一个被记录数据下标2条黑线，自然回撤栏最后一个数字下标2条红线
                            if pre_4.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_4.ID))
                            if pre_5.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_5.ID))

                            # 如果新出现的价格高于上升趋势栏最后记录的数字或高于自然回升栏黑线标记的最后一个价格3点或更多那么计入上升趋势栏，否则记录在自然回升栏
                            if bigger(price, 3, 0, 0) or bigger(price, 2, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 3, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 2, ID))

                    if name == "comb":
                        # 当每个趋势关键点全都出现时
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 2))
                        min_ID_nup = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 3))
                        min_ID_up = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 4))
                        min_ID_down = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 5))
                        min_ID_ndown = c.fetchall()

                        if min_ID_down and min_ID_up and min_ID_ndown and min_ID_nup:
                            c.execute(
                                "select price, date, timesticker, column from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                date = info[1]
                                ts = info[2]
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
                                            if price >= last_up_price + 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 2
                                                else:
                                                    trend_signal = 20
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回升栏
                                        if last_column == 2:
                                            # 最新自然回升栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 2))
                                            last_up_price_list = c.fetchall()
                                            if last_up_price_list:
                                                last_up_price = last_up_price_list[-1][0]
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                    # 更新最新一点趋势信号
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

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
                                            if price <= last_down_price - 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 4
                                                else:
                                                    trend_signal = 40
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回撤栏
                                        if last_column == 5:
                                            # 最新自然回撤栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 5))
                                            last_down_price_list = c.fetchall()
                                            if last_down_price_list:
                                                last_down_price = last_down_price_list[-1][0]
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                    # 如果上一栏在上升趋势栏
                    if pre_COLUMN == 3:
                        # 如果价格大于上一价格，记录在上升趋势栏
                        if price > pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ? where ID =?", (1, 3, ID))
                        # 如果价格小于上一价格6点(或12点）更多，尝试记录在自然回撤栏）
                        elif price <= pre_PRICE - 6 * coefficient:
                            use = begin_5(price)

                    # 如果上一栏在下降趋势栏
                    elif pre_COLUMN == 4:
                        # 如果价格小于上一价格，记录在下降趋势栏
                        if price < pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 4, 0, ID))
                        # 如果价格大于上一价格6点(或12点）更多，尝试记录在自然回升栏
                        elif price >= pre_PRICE + 6 * coefficient:
                            use = begin_2(price)
                        # 其他情况不记录

                    # 如果上一栏在自然回升栏
                    elif pre_COLUMN == 2:
                        # 如果价格大于前一价格则尝试记录在自然回升栏
                        if price > pre_PRICE:
                            use = begin_2(price)
                        # 如果价格小于前一价格6点（或12点）更多则记录
                        elif price <= pre_PRICE - 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为红线且为自然回撤趋势
                            if pre_key_COLUMN == 5:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试在自然回撤栏记录
                                else:
                                    use = begin_5(price)
                            # 其余情况尝试记录在自然回撤栏
                            else:
                                use = begin_5(price)

                    # 如果上一栏在次级回升栏
                    elif pre_COLUMN == 1:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回升
                        if pre_key_COLUMN == 2:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格比前一价格低6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                        # 如果上一次keyspot为自然回撤
                        elif pre_key_COLUMN == 5:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次上升趋势最高点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (3, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格低于前一价格6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)

                    # 如果上一栏在自然回撤栏
                    elif pre_COLUMN == 5:
                        # 如果价格小于前一价格则尝试在自然回撤栏记录
                        if price < pre_PRICE:
                            use = begin_5(price)
                        # 如果价格大于前一价格6点（或12点）更多则记录
                        elif price >= pre_PRICE + 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为黑线且为自然回升趋势
                            if pre_key_COLUMN == 2:
                                # 上一次自然回升趋势最高点黑线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where KEYSPOT = ? and COLUMN = ? and NAME = ?", (1, 2, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于最高点黑线price记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试在自然回升栏记录
                                else:
                                    use = begin_2(price)
                            # 其余情况尝试在自然回升记录
                            else:
                                use = begin_2(price)

                    # 如果上一栏在次级回撤栏
                    elif pre_COLUMN == 6:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回撤
                        if pre_key_COLUMN == 5:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤最低点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (5, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回撤最低点价格高继续记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况记录尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                            # 如果价格比前一价格高6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                        # 如果上一次keyspot为自然回升
                        elif pre_key_COLUMN == 2:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    begin_5(price)
                            # 如果价格大于前一价格6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然级回升栏
                                else:
                                    use = begin_2(price)

                    # 将未记录的数据的COLUMN修改为上一个被记录的COLUMN
                    c.execute(
                        "select RECORD  from STOCK_LIST where ID = {}".format(ID))
                    whe_rec = c.fetchall()[0][0]
                    if whe_rec == 0:
                        c.execute("select max(ID) from STOCK_LIST where ID < ? and NAME = ? and RECORD = ?",
                                  (ID, name, 1))
                        last_rec_ID = c.fetchall()[0][0]
                        c.execute(
                            "select COLUMN from STOCK_LIST where ID = ?", (last_rec_ID,))
                        last_rec_col = c.fetchall()[0][0]
                        c.execute("update STOCK_list set COLUMN = ? where ID = ?",
                                  (last_rec_col, ID))

                    if name == "comb":
                        c.execute(
                            "select * from COMB_TREND where TRENDSIGNAL > {0} and TIMESTICKER < {1} ".format(0, ts))
                        # 如果存在趋势信号
                        if c.fetchall():
                            c.execute(
                                "select price,record,column,date,timesticker from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                record = info[1]
                                column = info[2]
                                date = info[3]
                                ts = info[4]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(date, "XAUUSD"))
                                volume = c.fetchall()[0][0]
                                # 上一被记录点的信息
                                c.execute(
                                    "select date,ID,price from STOCK_LIST where record = {0} and ID < {1} and NAME = '{2}'".format(1, ID, "comb"))
                                last_info = c.fetchall()[-1]
                                last_date = last_info[0]
                                last_ID = last_info[1]
                                last_price = last_info[2]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(last_date, "XAUUSD"))
                                last_volume = c.fetchall()[0][0]

                                # 最新趋势状态栏信息
                                c.execute(
                                    "select TIMESTICKER from COMB_TREND where TIMESTICKER < {0} and TRENDSIGNAL > {1}".format(ts, 0))
                                last_ts = c.fetchall()[-1][0]
                                c.execute(
                                    "select column from STOCK_LIST where timesticker = {0}  and NAME = '{1}'".format(last_ts, "comb"))
                                last_column = c.fetchall()[-1][0]
                                c.execute(
                                    "select TRENDSIGNAL,DATE from COMB_TREND where TIMESTICKER = {0} and TRENDSIGNAL > {1}".format(last_ts, 0))
                                last_info_list = c.fetchall()

                                for last_info in last_info_list:
                                    last_trend_signal = last_info[0]
                                    last_trend_date = last_info[1]
                                    # 当最新一个趋势状态栏为下降趋势结束时
                                    if last_trend_signal in (3, 30):
                                        # 下降趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            4, 1, "comb", last_ID))
                                        last_down_price_list = c.fetchall()
                                        if last_down_price_list:
                                            last_down_price = last_down_price_list[-1][0]
                                            # 当此状态栏记录在下降趋势栏时
                                            if last_column == 4:
                                                if price <= last_down_price - 3 * coefficient or column * record == 4:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回撤栏时
                                            elif last_column == 5:
                                                if price <= last_down_price - 3 * coefficient or column * record == 5:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                    # 当最新一个趋势状态栏为上升趋势结束时
                                    elif last_trend_signal in (1, 10):
                                        # 上升趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            3, 1, "comb", last_ID))
                                        last_up_price_list = c.fetchall()
                                        if last_up_price_list:
                                            last_up_price = last_up_price_list[-1][0]
                                            # 当此状态栏记录在上升趋势栏时
                                            if last_column == 3:
                                                if price >= last_up_price + 3 * coefficient or column * record == 3:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回升栏时
                                            elif last_column == 2:
                                                if price >= last_down_price + 3 * coefficient or column * record == 2:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                # 当最新价格上涨并且最新价格栏在下降趋势栏
                                if price > last_price and column == 4:
                                    # 下降趋势最新关键点价格若存在,最新价格上升到下降趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        4, 1, "comb", last_ID))
                                    last_down_price_list = c.fetchall()
                                    if last_down_price_list:
                                        last_down_price = last_down_price_list[-1][0]
                                        if price >= last_down_price + 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

                                # 当最新价格下跌且最新价格在上升趋势栏
                                if price < last_price and column == 3:
                                    # 上升趋势最新关键点价格若存在,最新价格下跌到上升趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        3, 1, "comb", last_ID))
                                    last_up_price_list = c.fetchall()
                                    if last_up_price_list:
                                        last_up_price = last_up_price_list[-1][0]
                                        if price <= last_up_price - 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

        rule("XAUUSD", 1, 7/3)
        rule("DXY", 2, 0.3/3)
        rule("comb", 3, 6/3)

        # 关闭数据库连接
        conn.commit()
        conn.close()

class def_down_XAU_TNX:
    def __init__(self, database_path):
        XAUUSD_TNX_db_path = database_path + r"\XAUUSD_TNX.db"
        # 连接数据库data.db和指针
        conn = sqlite3.connect(XAUUSD_TNX_db_path)
        c = conn.cursor()

        # 获取时间长度
        c.execute("SELECT max(ID) from STOCK_LIST")
        length = int(c.fetchone()[0]/3)

        # 设定第一个值 RECORD为1
        c.execute("update STOCK_LIST SET RECORD = 1 where ID < 5")

        # 设定第一个值 COLUMN为4
        c.execute("update STOCK_LIST SET COLUMN = 4 where ID < 5")

        # 创建趋势信号table
        c.execute('''CREATE TABLE IF NOT EXISTS COMB_TREND
            (ID              INTEGER        PRIMARY KEY,
                NAME            TEXT           NOT NULL,
                DATE            TEXT           NOT NULL,
                TIMESTICKER     UNSIGNED INT   NOT NULL,
                TRENDSIGNAL     UNSIGNED INT   DEFAULT 0,
                NOTE            TEXT           NULL);''')

        # 根据livermore操盘法则确定RECORD,COLUMN,KEYSPOT
        # i指针遍历XAUUSD

        class rule:
            def __init__(self, name, fir_ID, coefficient):
                for i in range(1, length):
                    # 获取判断所需数据
                    # ID
                    ID = fir_ID + 3 * i
                    # 价格
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ? ", (ID,))
                    price = c.fetchone()[0]
                    # 时间戳
                    c.execute(
                        "select timesticker from STOCK_LIST where ID = ? ", (ID,))
                    ts = c.fetchone()[0]

                    # 上一个被记录的ID，被记录的价格，被记录的行
                    c.execute(
                        "select max(ID) from STOCK_LIST where NAME = ? and RECORD = ?", (name, 1))
                    pre_ID = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select PRICE from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个价格
                    pre_PRICE = c.fetchone()[0]
                    # 指针选中上一个被记录的行
                    c.execute(
                        "select COLUMN from STOCK_LIST where ID = ?", (pre_ID,))
                    # 上一个所在栏
                    pre_COLUMN = c.fetchone()[0]

                    # 上一个趋势最后一点的ID，price
                    class pull_pre:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and COLUMN = ? and NAME = ? ", (1, pos, name))
                            ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if ID_list:
                                self.ID = ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    pre_2 = pull_pre(2)
                    pre_3 = pull_pre(3)
                    pre_4 = pull_pre(4)
                    pre_5 = pull_pre(5)

                    # 上一个趋势最后一keyspot点的ID，price
                    class pull_prekey:
                        def __init__(self, pos):
                            # 取出选中栏所有key的ID为列表
                            c.execute(
                                "select ID from STOCK_LIST where RECORD = ? and KEYSPOT = ? AND COLUMN = ? and NAME = ?", (1, 1, pos, name))
                            KEY_ID_list = c.fetchall()
                            # 如果列表非空取最后一个元组并将ID元组转化为数字
                            if KEY_ID_list:
                                self.ID = KEY_ID_list[-1][0]
                                # 取出self.ID对应的价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where ID = ?", (self.ID,))
                                self.PRICE = c.fetchone()[0]
                            else:
                                self.ID = False
                                self.PRICE = False

                    # 用类获取相应值
                    prekey_2 = pull_prekey(2)
                    prekey_3 = pull_prekey(3)
                    prekey_4 = pull_prekey(4)
                    prekey_5 = pull_prekey(5)

                    # 定义比较函数
                    def bigger(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price >= prekey.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price >= pre.PRICE + interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    def smaller(price: float, column: int, key: int, interval: int):
                        if key == 1:
                            prekey = pull_prekey(column)
                            if prekey.PRICE:
                                if price <= prekey.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        elif key == 0:
                            pre = pull_pre(column)
                            if pre.PRICE:
                                if price <= pre.PRICE - interval * coefficient:
                                    return True
                                else:
                                    return False
                            else:
                                return False

                    # 定义开始进入自然回撤栏的状态类

                    class begin_5:
                        def __init__(self, price):
                            # 同时在上升趋势的最后一个被记录数据下标两条红线，自然回升栏最后一个数字下标2条黑线
                            if pre_3.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_3.ID))
                            if pre_2.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_2.ID))

                            # 如果新出现的价格低于下降趋势栏最后记录的数字或低于自然回撤栏红线标记的最后一个价格3点或更多那么计入下降趋势栏，否则记录在自然回撤栏
                            if smaller(price, 4, 0, 0) or smaller(price, 5, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 4, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 5, ID))

                    # 定义开始进入自然回升栏的状态类
                    class begin_2:
                        def __init__(self, price):
                            # 同时在下降趋势的最后一个被记录数据下标2条黑线，自然回撤栏最后一个数字下标2条红线
                            if pre_4.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_4.ID))
                            if pre_5.ID:
                                c.execute(
                                    "update STOCK_LIST set KEYSPOT = ? where RECORD = ? and ID = ?", (1, 1, pre_5.ID))

                            # 如果新出现的价格高于上升趋势栏最后记录的数字或高于自然回升栏黑线标记的最后一个价格3点或更多那么计入上升趋势栏，否则记录在自然回升栏
                            if bigger(price, 3, 0, 0) or bigger(price, 2, 1, 3):
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 3, ID))
                            else:
                                c.execute(
                                    "update STOCK_LIST set RECORD = ?,COLUMN = ? where ID = ?", (1, 2, ID))

                    if name == "comb":
                        # 当每个趋势关键点全都出现时
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 2))
                        min_ID_nup = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 3))
                        min_ID_up = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 4))
                        min_ID_down = c.fetchall()
                        c.execute("select ID from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and COLUMN = {2}".format(
                            'comb', 1, 5))
                        min_ID_ndown = c.fetchall()

                        if min_ID_down and min_ID_up and min_ID_ndown and min_ID_nup:
                            c.execute(
                                "select price, date, timesticker, column from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                date = info[1]
                                ts = info[2]
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
                                            if price >= last_up_price + 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 2
                                                else:
                                                    trend_signal = 20
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回升栏
                                        if last_column == 2:
                                            # 最新自然回升栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 2))
                                            last_up_price_list = c.fetchall()
                                            if last_up_price_list:
                                                last_up_price = last_up_price_list[-1][0]
                                                if price <= last_up_price - 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 1
                                                    else:
                                                        trend_signal = 10
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在下降趋势恢复
                                                    if column == 4:
                                                        # 最新下降趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 4))
                                                        last_down_price_list = c.fetchall()
                                                        # 如果最新价格向下突破下降趋势最新关键点价格3点则下降趋势恢复
                                                        if last_down_price_list:
                                                            last_down_price = last_down_price_list[-1][0]
                                                            if price <= last_down_price - 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 4
                                                                else:
                                                                    trend_signal = 40
                                                    # 更新最新一点趋势信号
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

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
                                            if price <= last_down_price - 3 * coefficient:
                                                # 比较volume后更新最新点的趋势信号
                                                if volume > last_volume * 0.99:
                                                    trend_signal = 4
                                                else:
                                                    trend_signal = 40
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
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
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                                        # 如果前一记录栏为自然回撤栏
                                        if last_column == 5:
                                            # 最新自然回撤栏已记录价格
                                            c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and RECORD ={2} and column = {3}".format(
                                                'comb', ID, 1, 5))
                                            last_down_price_list = c.fetchall()
                                            if last_down_price_list:
                                                last_down_price = last_down_price_list[-1][0]
                                                if price >= last_down_price + 3 * coefficient:
                                                    # 根据volume判断上升趋势结束记录形式
                                                    if volume > last_volume * 0.99:
                                                        trend_signal = 3
                                                    else:
                                                        trend_signal = 30
                                                    c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))
                                                    # 判断是否存在上升趋势恢复
                                                    if column == 3:
                                                        # 最新上升趋势关键点价格
                                                        c.execute("select price from STOCK_LIST where NAME = '{0}' and ID < {1} and KEYSPOT ={2} and column = {3}".format(
                                                            'comb', ID, 1, 3))
                                                        last_up_price_list = c.fetchall()
                                                        # 如果最新价格向上突破上升趋势最新关键点价格3点则上升趋势恢复
                                                        if last_up_price_list:
                                                            last_up_price = last_up_price_list[-1][0]
                                                            if price >= last_up_price + 3 * coefficient:
                                                                if volume > last_volume * 0.99:
                                                                    trend_signal = 2
                                                                else:
                                                                    trend_signal = 20
                                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                                        VALUES(?, ?, ?, ?) ", ("comb", date, ts, trend_signal))

                    # 如果上一栏在上升趋势栏
                    if pre_COLUMN == 3:
                        # 如果价格大于上一价格，记录在上升趋势栏
                        if price > pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ? where ID =?", (1, 3, ID))
                        # 如果价格小于上一价格6点(或12点）更多，尝试记录在自然回撤栏）
                        elif price <= pre_PRICE - 6 * coefficient:
                            use = begin_5(price)

                    # 如果上一栏在下降趋势栏
                    elif pre_COLUMN == 4:
                        # 如果价格小于上一价格，记录在下降趋势栏
                        if price < pre_PRICE:
                            c.execute(
                                "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 4, 0, ID))
                        # 如果价格大于上一价格6点(或12点）更多，尝试记录在自然回升栏
                        elif price >= pre_PRICE + 6 * coefficient:
                            use = begin_2(price)
                        # 其他情况不记录

                    # 如果上一栏在自然回升栏
                    elif pre_COLUMN == 2:
                        # 如果价格大于前一价格则尝试记录在自然回升栏
                        if price > pre_PRICE:
                            use = begin_2(price)
                        # 如果价格小于前一价格6点（或12点）更多则记录
                        elif price <= pre_PRICE - 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为红线且为自然回撤趋势
                            if pre_key_COLUMN == 5:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试在自然回撤栏记录
                                else:
                                    use = begin_5(price)
                            # 其余情况尝试记录在自然回撤栏
                            else:
                                use = begin_5(price)

                    # 如果上一栏在次级回升栏
                    elif pre_COLUMN == 1:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回升
                        if pre_key_COLUMN == 2:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格比前一价格低6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                        # 如果上一次keyspot为自然回撤
                        elif pre_key_COLUMN == 5:
                            # 如果价格高于前一价格
                            if price > pre_PRICE:
                                # 读取上一次上升趋势最高点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (3, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                            # 如果价格低于前一价格6点或更多
                            elif price <= pre_PRICE - 6 * coefficient:
                                # 上一次自然回撤趋势最低点红线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where keyspot = ? and COLUMN = ? and NAME = ?", (1, 5, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格高于最低点红线price记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)

                    # 如果上一栏在自然回撤栏
                    elif pre_COLUMN == 5:
                        # 如果价格小于前一价格则尝试在自然回撤栏记录
                        if price < pre_PRICE:
                            use = begin_5(price)
                        # 如果价格大于前一价格6点（或12点）更多则记录
                        elif price >= pre_PRICE + 6 * coefficient:
                            # 选中上一次出现的keyspot的ID
                            c.execute(
                                "select max(ID) from STOCK_LIST where KEYSPOT = ? and name = ?", (1, name))
                            pre_key_ID = c.fetchone()[0]
                            # 读取上一次keyspot所在栏
                            c.execute(
                                "select COLUMN from STOCK_LIST where ID = ?", (pre_key_ID,))
                            pre_key_COLUMN = c.fetchone()[0]
                            # 如果上一次keyspot下为黑线且为自然回升趋势
                            if pre_key_COLUMN == 2:
                                # 上一次自然回升趋势最高点黑线price
                                c.execute(
                                    "select PRICE from STOCK_LIST where KEYSPOT = ? and COLUMN = ? and NAME = ?", (1, 2, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于最高点黑线price记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试在自然回升栏记录
                                else:
                                    use = begin_2(price)
                            # 其余情况尝试在自然回升记录
                            else:
                                use = begin_2(price)

                    # 如果上一栏在次级回撤栏
                    elif pre_COLUMN == 6:
                        # 取前一keyspot出的COLUMN
                        c.execute(
                            "select COLUMN from STOCK_list where KEYSPOT = ? and NAME = ? ", (1, name))
                        pre_key_COLUMN = c.fetchall()[-1][0]
                        # 如果上一次keyspot为自然回撤
                        if pre_key_COLUMN == 5:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤最低点红线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (5, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回撤最低点价格高继续记录在次级回撤栏
                                if price >= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况记录尝试记录在自然回撤栏
                                else:
                                    use = begin_5(price)
                            # 如果价格比前一价格高6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升趋势最后一点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (2, 1, name))
                                pre_nr_PRICE = c.fetchall()[-1][0]
                                # 如果价格低于上一次自然回升趋势最后一点价格继续记录在次级回升栏
                                if price <= pre_nr_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然回升栏
                                else:
                                    use = begin_2(price)
                        # 如果上一次keyspot为自然回升
                        elif pre_key_COLUMN == 2:
                            # 如果价格低于前一价格
                            if price < pre_PRICE:
                                # 读取上一次自然回撤趋势最低点价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and RECORD = ? and NAME = ?", (5, 1, name))
                                pre_drop_PRICE = c.fetchall()[-1][0]
                                # 如果价格大于上一次自然回撤趋势最低点价格则记录在次级回撤栏
                                if price >= pre_drop_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 6, 0, ID))
                                # 其余情况尝试记录在自然回撤栏
                                else:
                                    begin_5(price)
                            # 如果价格大于前一价格6点或更多
                            elif price >= pre_PRICE + 6 * coefficient:
                                # 读取上一次自然回升最高点黑线价格
                                c.execute(
                                    "select PRICE from STOCK_LIST where COLUMN = ? and KEYSPOT = ? and NAME = ?", (2, 1, name))
                                pre_key_PRICE = c.fetchall()[-1][0]
                                # 如果价格比上一次自然回升最高点价格低继续记录在次级回升栏
                                if price <= pre_key_PRICE:
                                    c.execute(
                                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 1, 0, ID))
                                # 其余情况尝试记录在自然级回升栏
                                else:
                                    use = begin_2(price)

                    # 将未记录的数据的COLUMN修改为上一个被记录的COLUMN
                    c.execute(
                        "select RECORD  from STOCK_LIST where ID = {}".format(ID))
                    whe_rec = c.fetchall()[0][0]
                    if whe_rec == 0:
                        c.execute("select max(ID) from STOCK_LIST where ID < ? and NAME = ? and RECORD = ?",
                                  (ID, name, 1))
                        last_rec_ID = c.fetchall()[0][0]
                        c.execute(
                            "select COLUMN from STOCK_LIST where ID = ?", (last_rec_ID,))
                        last_rec_col = c.fetchall()[0][0]
                        c.execute("update STOCK_list set COLUMN = ? where ID = ?",
                                  (last_rec_col, ID))

                    if name == "comb":
                        c.execute(
                            "select * from COMB_TREND where TRENDSIGNAL > {0} and TIMESTICKER < {1} ".format(0, ts))
                        # 如果存在趋势信号
                        if c.fetchall():
                            c.execute(
                                "select price,record,column,date,timesticker from STOCK_LIST where NAME = '{0}' and ID = {1}".format('comb', ID))
                            info_list = c.fetchall()
                            for info in info_list:
                                # 最新价格信息
                                price = info[0]
                                record = info[1]
                                column = info[2]
                                date = info[3]
                                ts = info[4]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(date, "XAUUSD"))
                                volume = c.fetchall()[0][0]
                                # 上一被记录点的信息
                                c.execute(
                                    "select date,ID,price from STOCK_LIST where record = {0} and ID < {1} and NAME = '{2}'".format(1, ID, "comb"))
                                last_info = c.fetchall()[-1]
                                last_date = last_info[0]
                                last_ID = last_info[1]
                                last_price = last_info[2]
                                # 获取同一天XAUUSD的volume
                                c.execute(
                                    "select volume from STOCK_LIST where date = '{0}' and name = '{1}'".format(last_date, "XAUUSD"))
                                last_volume = c.fetchall()[0][0]

                                # 最新趋势状态栏信息
                                c.execute(
                                    "select TIMESTICKER from COMB_TREND where TIMESTICKER < {0} and TRENDSIGNAL > {1}".format(ts, 0))
                                last_ts = c.fetchall()[-1][0]
                                c.execute(
                                    "select column from STOCK_LIST where timesticker = {0}  and NAME = '{1}'".format(last_ts, "comb"))
                                last_column = c.fetchall()[-1][0]
                                c.execute(
                                    "select TRENDSIGNAL,DATE from COMB_TREND where TIMESTICKER = {0} and TRENDSIGNAL > {1}".format(last_ts, 0))
                                last_info_list = c.fetchall()

                                for last_info in last_info_list:
                                    last_trend_signal = last_info[0]
                                    last_trend_date = last_info[1]
                                    # 当最新一个趋势状态栏为下降趋势结束时
                                    if last_trend_signal in (3, 30):
                                        # 下降趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            4, 1, "comb", last_ID))
                                        last_down_price_list = c.fetchall()
                                        if last_down_price_list:
                                            last_down_price = last_down_price_list[-1][0]
                                            # 当此状态栏记录在下降趋势栏时
                                            if last_column == 4:
                                                if price <= last_down_price - 3 * coefficient or column * record == 4:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回撤栏时
                                            elif last_column == 5:
                                                if price <= last_down_price - 3 * coefficient or column * record == 5:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                    # 当最新一个趋势状态栏为上升趋势结束时
                                    elif last_trend_signal in (1, 10):
                                        # 上升趋势最新关键点价格若存在
                                        c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                            3, 1, "comb", last_ID))
                                        last_up_price_list = c.fetchall()
                                        if last_up_price_list:
                                            last_up_price = last_up_price_list[-1][0]
                                            # 当此状态栏记录在上升趋势栏时
                                            if last_column == 3:
                                                if price >= last_up_price + 3 * coefficient or column * record == 3:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))
                                            # 当此时状态记录在自然回升栏时
                                            elif last_column == 2:
                                                if price >= last_down_price + 3 * coefficient or column * record == 2:
                                                    # 根据volume条件记录危险信号
                                                    if volume > last_volume * 0.99:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 5, last_trend_date))
                                                    else:
                                                        c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL, NOTE) \
                                                                    VALUES(?, ?, ?, ?, ?) ", ("comb", date, ts, 50, last_trend_date))

                                # 当最新价格上涨并且最新价格栏在下降趋势栏
                                if price > last_price and column == 4:
                                    # 下降趋势最新关键点价格若存在,最新价格上升到下降趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        4, 1, "comb", last_ID))
                                    last_down_price_list = c.fetchall()
                                    if last_down_price_list:
                                        last_down_price = last_down_price_list[-1][0]
                                        if price >= last_down_price + 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

                                # 当最新价格下跌且最新价格在上升趋势栏
                                if price < last_price and column == 3:
                                    # 上升趋势最新关键点价格若存在,最新价格下跌到上升趋势栏最新关键点以上3点则记录危险信号
                                    c.execute("select price from STOCK_LIST where COLUMN = {0} and KEYSPOT = {1} and name = '{2}' and ID < {3}".format(
                                        3, 1, "comb", last_ID))
                                    last_up_price_list = c.fetchall()
                                    if last_up_price_list:
                                        last_up_price = last_up_price_list[-1][0]
                                        if price <= last_up_price - 3 * coefficient:
                                            # 根据volume条件记录危险信号
                                            if volume > last_volume * 0.99:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 6))
                                            else:
                                                c.execute("insert into COMB_TREND(NAME, DATE, TIMESTICKER, TRENDSIGNAL) \
                                                            VALUES(?, ?, ?, ?) ", ("comb", date, ts, 60))

        rule("XAUUSD", 1, 7/3)
        rule("TNX", 2, 0.03/3)
        rule("comb", 3, 6/3)

        # 关闭数据库连接
        conn.commit()
        conn.close()
        print("趋势测定成功")