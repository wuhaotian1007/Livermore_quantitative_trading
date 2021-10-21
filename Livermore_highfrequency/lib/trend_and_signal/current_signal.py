# -*- encoding: utf-8 -*-
'''
@File    :   current_signal.py
@Time    :   2021/10/17 16:17:45
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3


class current_signal:
    def __init__(self, hf_db_path, D1_db_path, XAUUSD_coef, comb_coef, process_length):
        # hf_db_path:高频数据库路径，D1_db_path日线数据库路径，XAUUSD_coef:XAUUSD系数，comb_coef：comb系数，process_length:倒数处理长度，all为首次入库

        # 建立日线数据库和高频数据库连接
        conn_hf_db = sqlite3.connect(hf_db_path)
        conn_D1_db = sqlite3.connect(D1_db_path)

        cur_hf_db = conn_hf_db.cursor()
        cur_D1_db = conn_D1_db.cursor()

        cur_hf_db.execute("select * from ")

        process_time = 0
        # 指针i遍历高频数据db
        
