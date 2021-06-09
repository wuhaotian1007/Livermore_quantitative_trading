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

# 连接数据库data.db和指针
conn = sqlite3.connect('C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\database\\XAUUSD_DXY_TNX.db')
c = conn.cursor()

# 获取时间长度
c.execute("SELECT max(ID) from STOCK_LIST")
length = int(c.fetchone()[0]/4)

# 设定第一个值 RECORD为1
c.execute("update STOCK_LIST SET RECORD = 1 where ID < 5")

# 设定第一个值 COLUMN为3
c.execute("update STOCK_LIST SET COLUMN = 3 where ID < 5")

# 根据livermore操盘法则确定RECORD,COLUMN,KEYSPOT
# i指针遍历XAUUSD


class rule:
    def __init__(self, name, fir_ID, coefficient):
        for i in range(1, length-1):
            # 获取判断所需数据
            # ID
            ID = fir_ID + 4 * i
            # 价格
            c.execute("select PRICE from STOCK_LIST where ID = ? ", (ID,))
            price = c.fetchone()[0]

            # 上一个被记录的ID，被记录的价格，被记录的行
            c.execute(
                "select max(ID) from STOCK_LIST where NAME = ? and RECORD = ?", (name, 1))
            pre_ID = c.fetchone()[0]
            # 指针选中上一个被记录的行
            c.execute("select PRICE from STOCK_LIST where ID = ?", (pre_ID,))
            # 上一个价格
            pre_PRICE = c.fetchone()[0]
            # 指针选中上一个被记录的行
            c.execute("select COLUMN from STOCK_LIST where ID = ?", (pre_ID,))
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
            if pre_COLUMN == 4:
                # 如果价格小于上一价格，记录在下降趋势栏
                if price < pre_PRICE:
                    c.execute(
                        "update STOCK_LIST set RECORD = ?, COLUMN = ?, KEYSPOT = ? where ID =?", (1, 4, 0, ID))
                # 如果价格大于上一价格6点(或12点）更多，尝试记录在自然回升栏
                elif price >= pre_PRICE + 6 * coefficient:
                    use = begin_2(price)
                # 其他情况不记录

            # 如果上一栏在自然回升栏
            if pre_COLUMN == 2:
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
            if pre_COLUMN == 1:
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
            if pre_COLUMN == 5:
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
                    else :
                        use = begin_2(price)
            
            # 如果上一栏在次级回撤栏
            if pre_COLUMN == 6:
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
                if pre_key_COLUMN == 2:
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


# 使用类处理
XAUUSD_rule = rule("XAUUSD", 1, 7/3)
DXY_rule = rule("DXY", 2, 0.3/3)
TNX_rule = rule("TNX", 3, 0.03/3)
combination_rule = rule("comb", 4, 9/3)

# 将所有未记录的数据的COLUMN修改为上一个被记录的COLUMN
c.execute("select ID,NAME  from STOCK_LIST where RECORD = 0")
unrec_list = c.fetchall()
for unrec in unrec_list:
    unrec_ID = unrec[0]
    unrec_name = unrec[1]
    c.execute("select max(ID) from STOCK_LIST where ID < ? and NAME = ? and RECORD = ?",
              (unrec_ID, unrec_name, 1))
    last_rec_ID = c.fetchall()[0][0]
    c.execute("select COLUMN from STOCK_LIST where ID = ?", (last_rec_ID,))
    last_rec_col = c.fetchall()[0][0]
    c.execute("update STOCK_list set COLUMN = ? where ID = ?",
              (last_rec_col, unrec_ID))


# 关闭数据库连接
conn.commit()
conn.close()
