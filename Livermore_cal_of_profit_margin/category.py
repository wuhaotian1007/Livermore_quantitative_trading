# -*- encoding: utf-8 -*-
'''
@File    :   category.py
@Time    :   2021/07/01 21:19:42
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3

# 连接category交易品类信息数据库
conn = sqlite3.connect(
    r'C:\Users\sgnjim\Desktop\Livermore\Livermore_quantitative_trading\Livermore interest_rate\category.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS currency_list
       (ID                     INTEGER        PRIMARY KEY,
        NAME                   TEXT           NOT NULL,
        closing_line           UNSIGNED INT   NOT NULL,
        leverage_ratio         UNSIGNED INT   NOT NULL,
        volume_per_hand        UNSIGNED INT   NOT NULL,
        soft_limit             UNSIGNED INT   NOT NULL,
        points                 UNSIGNED INT   NOT NULL);''')

# 加入新币种类


class add_new_currency:
    def __init__(self, name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points) -> None:
        c.execute("insert into currency_list(name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points) \
                     VALUES(?, ?, ?, ?, ?, ?) ", (name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points))
        print("加入新币种",name,"成功")


add_new_currency("XAUUSD", 0.5, 500, 100, 4500, 0.01)

# 关闭数据库连接
conn.commit()
conn.close()