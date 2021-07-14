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

class create_category_db:
    def __init__(self, category_db_path):
        # 连接category交易品类信息数据库
        conn_category_db = sqlite3.connect(category_db_path)
        cur_category_db = conn_category_db.cursor()

        cur_category_db.execute('''CREATE TABLE IF NOT EXISTS currency_list
            (ID                     INTEGER        PRIMARY KEY,
                NAME                   TEXT           NOT NULL,
                closing_line           UNSIGNED INT   NOT NULL,
                leverage_ratio         UNSIGNED INT   NOT NULL,
                volume_per_hand        UNSIGNED INT   NOT NULL,
                soft_limit             UNSIGNED INT   NOT NULL,
                points                 UNSIGNED INT   NOT NULL);''')

        # 加入新币种类


        def add_new_currency(name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points):
            cur_category_db.execute("insert into currency_list(name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points) \
                        VALUES(?, ?, ?, ?, ?, ?) ", (name, closing_line, leverage_ratio, volume_per_hand, soft_limit, points))
            print("加入新币种",name,"成功")


        add_new_currency("XAUUSD", 0.5, 500, 100, 4500, 0.01)

        # 关闭数据库连接
        conn_category_db.commit()
        conn_category_db.close()

        print("交易品类信息数据库创建完毕")