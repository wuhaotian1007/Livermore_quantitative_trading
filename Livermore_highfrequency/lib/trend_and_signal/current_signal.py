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
    def __init__(self, hf_db_path, D1_db_path, XAUUSD_coef, comb_coef, match_mode, process_length):
        # hf_db_path:高频数据库路径，D1_db_path日线数据库路径，XAUUSD_coef:XAUUSD系数，comb_coef：comb系数，process_length:倒数处理长度，all为首次入库

        # 建立日线数据库和高频数据库连接
        conn_hf_db = sqlite3.connect(hf_db_path)
        conn_D1_db = sqlite3.connect(D1_db_path)

        cur_hf_db = conn_hf_db.cursor()
        cur_D1_db = conn_D1_db.cursor()

        cur_hf_db.execute("select * from ")

        process_time = 0

        def iter_XAUUSD():
            # 遍历高频数据db
            # 遍历XAUUSD
            cur_hf_db.execute("select * from XAUUSD_list")
            XAUUSD_list = cur_hf_db.fetchall()

            # 判断处理长度，根据处理长度截取数据范围
            if process_length == "all":
                print("首次处理实时信号")
            else:
                XAUUSD_list = XAUUSD_list[-process_length:]

            last_date = ""
            last_up_key_spot = 0
            last_down_key_spot = 0
            # 开始遍历XAUUSD
            for XAUUSD_info in XAUUSD_list:
                date = XAUUSD_info[0][:10]
                close = XAUUSD_info[2]
                ts = XAUUSD_info[3]

                if date != last_date:
                    # 查询XAUUSD日线关键点价格
                    cur_D1_db.execute(
                        "select price from STOCK_LIST where name == {0} and keyspot == {1} and timesticker <= {2} and ".format("XAUUSD", 1, ts))
                
