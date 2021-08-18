# -*- encoding: utf-8 -*-
'''
@File    :   launcher.py
@Time    :   2021/05/07 16:37:57
@Author  :   Wuhaotian 
@Version :   1.2
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
from lib.visualization.vis_trend_history import vis_trend_history
import os
import sys
import configparser
from lib.data_pull_storage.from_MT5 import pull_from_MT5
from lib.data_pull_storage.from_yfinance import pull_from_yfinance
from lib.standardization_storage.XAUUSD_std import XAUUSD_std, DXY_std, TNX_std
from lib.standardization_storage.comb import comb
from lib.est_trend.default_downtrend import def_down_XAUUSD_DXY_TNX, def_down_XAU_DXY, def_down_XAU_TNX
from lib.visualization.vis_trend_history import vis_trend_history
from lib.cal_of_trading_inf.category import create_category_db
from lib.cal_of_trading_inf.pull_XAUUSD_from_MT5 import pull_XAUUSD_from_MT5
from lib.cal_of_trading_inf.IO_storage import IO_storage
from lib.cal_of_trading_inf.chart import draw_chart
from lib.cal_of_trading_inf.visualization import vis_by_excel

# 读取全局设置
conf= configparser.ConfigParser()
'''读取配置文件'''
conf.read('global.conf') # 文件路径
onedrive_path = conf.get("global", "Onedrive_path") # 获取指定section 的option值

# 设置各路径
# 数据库路径
database_path = r"database"

# 品类信息数据库路径
category_db_path = r"database\category.db"

# XAUUSD 原始数据路径
XAUUSD_1H_data_path = r"raw_data\XAUUSD_1H.csv"
XAUUSD_data_path = r"raw_data\XAUUSDDaily.csv"
DXY_data_path = r"raw_data\DXY.csv"
TNX_data_path = r"raw_data\TNX.csv"

raw_data_db_path = r"database\raw_data.db"
XAUUSD_1H_db_path = r"database\XAUUSD_1H.db"
XAUUSD_db_path = r"database\XAUUSD.db"

database_path = r"database"

# 可视化总表输出路径
total_output_xlsx_path = r"report\XAUUSD_TNX_DXY_total.xlsx"
# 交易记录数据库路径
trading_record_db_path = r"database\trading_records.db"

# 交易历史输入xlsx路径
trading_history_input_path = onedrive_path + r"\work\Trading_history\交易历史输入.xlsx"

# 趋势信号数据库路径
trendsignal_db_path = r"database\XAUUSD_DXY_TNX.db"
# 交易历史输出xlsx路径
his_output_xlsx_path = r"report\trade_history.xlsx"

# 月度信息图片路径  
monthly_info_png_path = r"chart\monthly_info.png"
# 月度利润率图片路径
monthly_surplus_png_path = r"chart\monthly_surplus.png"


# 删除文件函数
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


# 清空数据库
del_file(database_path)


# 运行
def calculate_profit_margin():
    create_category_db(category_db_path)

    pull_XAUUSD_from_MT5(XAUUSD_1H_data_path, XAUUSD_1H_db_path)

    IO_storage(category_db_path, trading_record_db_path,
               trading_history_input_path, XAUUSD_1H_db_path)

    draw_chart(trading_record_db_path, monthly_info_png_path,
               monthly_surplus_png_path)

    vis_by_excel(trading_record_db_path, his_output_xlsx_path,
                 monthly_info_png_path, monthly_surplus_png_path)


calculate_profit_margin()


def launcher(default_trend):
    if default_trend == "down":
        # 如果默认趋势为下降趋势
        # 拉取数据
        pull_from_MT5(XAUUSD_data_path)
        pull_from_yfinance(DXY_data_path, TNX_data_path, raw_data_db_path)

        # 数据标准化后入库
        XAUUSD_std(XAUUSD_db_path, XAUUSD_data_path)
        DXY_std(XAUUSD_db_path, DXY_data_path)
        TNX_std(XAUUSD_db_path, TNX_data_path)

        # 生成组合价格 (核心品类名称，3点，数据库路径，截距参数，*辅助元素名称 = 3点)
        comb("XAUUSD", 3/7, database_path, 600, DXY=- 3/0.3, TNX=- 3/0.03)
        comb("XAUUSD", 3/7, database_path, 600, DXY=- 3/0.3)
        comb("XAUUSD", 3/7, database_path, 600, TNX=- 3/0.03)

        # 测定趋势
        def_down_XAUUSD_DXY_TNX(database_path)
        def_down_XAU_DXY(database_path)
        def_down_XAU_TNX(database_path)

        # 可视化
        vis_trend_history(trading_record_db_path,
                          trendsignal_db_path, total_output_xlsx_path)


launcher("down")
