# -*- encoding: utf-8 -*-
'''
@File    :   launcher.py
@Time    :   2021/07/14 20:44:14
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
from lib.category import create_category_db
from lib.pull_XAUUSD_from_MT5 import pull_XAUUSD_from_MT5
from lib.IO_storage import IO_storage
from lib.chart import draw_chart
from lib.visualization import vis_by_excel
import os
import sys

# 设置各路径

# 数据库路径
db_path = r"database"
# 品类信息数据库路径
category_db_path = r"database\category.db"

# XAUUSD 原始数据路径
XAUUSD_data_path = r"raw_data\XAUUSDDaily.csv"
XAUUSD_db_path = r"database\XAUUSD.db"

# 交易记录数据库路径
trading_record_db_path = r"database\trading_records.db"

# 交易历史输入xlsx路径
trading_history_input_path = r"C:\Users\sgnjim\OneDrive\work\Trading_history\交易历史输入.xlsx"

# 交易历史输出xlsx路径
output_xlsx_path = r"trade_history.xlsx"

# 月度信息图片路径
monthly_info_png_path = r"chart\monthly_info.png"
# 月度利润率图片路径
monthly_surplus_png_path = r"chart\monthly_surplus.png"

# 删除数据库文件


def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


del_file(db_path)

# 运行
create_category_db(category_db_path)

pull_XAUUSD_from_MT5(XAUUSD_data_path, XAUUSD_db_path)

IO_storage(category_db_path, trading_record_db_path,
           trading_history_input_path, XAUUSD_db_path)

draw_chart(trading_record_db_path, monthly_info_png_path,
           monthly_surplus_png_path)

vis_by_excel(trading_record_db_path, output_xlsx_path,
             monthly_info_png_path, monthly_surplus_png_path)
