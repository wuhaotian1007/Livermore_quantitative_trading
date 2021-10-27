# -*- encoding: utf-8 -*-
'''
@File    :   launcher.py
@Time    :   2021/10/25 13:12:30
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import os
import sys
import schedule
import configparser

from lib.pull_data.pull_from_MT5 import pull_from_MT5_H1, pull_from_MT5_M1
from lib.pull_data.pull_from_yfinance import pull_from_yfinance_H1, pull_from_yfinance
from lib.standardization.XAUUSD_std import XAUUSD_std, DXY_std, TNX_std
from lib.standardization.comb import comb
from lib.trend_and_signal.trend_est import def_down_XAUUSD_DXY_TNX
from lib.trend_and_signal.current_signal import current_signal
from lib.visualization.vis_trend import vis_trend

# 读取全局配置


def load_config():
    global onedrive_path, bot_token, user_id, group_id
    conf = configparser.ConfigParser()
    conf.read('global.conf')
    onedrive_path = conf.get("global", "Onedrive_path")
    bot_token = conf.get("global", "bot_token")
    user_id = conf.get("global", "user_id")
    group_id = conf.get("global", "group_id")


load_config()

# 读取组合价格配置

# 字符型分数转换为小数


def frac_to_float(frac: str):
    molecure = float(frac.split("/")[0])
    denominator = float(frac.split("/")[1])
    out_float = molecure/denominator
    return out_float


def load_XAUUSD_DXY_TNX_coef():

    global XAUUSD_coef, DXY_coef, TNX_coef, constant, XAUUSD_3_price, DXY_3_price, TNX_3_price

    conf = configparser.ConfigParser()
    conf.read('XAUUSD_DXY_TNX_comb.conf')

    # 读取组合各品类组合系数
    XAUUSD_coef = frac_to_float(conf.get("XAUUSD_DXY_TNX_comb_coef", "XAUUSD"))
    DXY_coef = frac_to_float(conf.get("XAUUSD_DXY_TNX_comb_coef", "DXY"))
    TNX_coef = frac_to_float(conf.get("XAUUSD_DXY_TNX_comb_coef", "TNX"))
    XAUUSD_3_price = 1/abs(XAUUSD_coef)
    DXY_3_price = 1/abs(DXY_coef)
    TNX_3_price = 1/abs(TNX_coef)
    constant = float(conf.get("XAUUSD_DXY_TNX_comb_coef", "constant"))


load_XAUUSD_DXY_TNX_coef()

# 设置各个路径
XAUUSD_M1_csv_path = r"raw_data\XAUUSD_M1.csv"
XAUUSD_H1_csv_path = r"raw_data\XAUUSD_H1.csv"
DXY_M1_csv_path = r"raw_data\DXY_M1.csv"
DXY_M2_csv_path = r"raw_data\DXY_M2.csv"
DXY_H1_csv_path = r"raw_data\DXY_H1.csv"
TNX_M1_csv_path = r"raw_data\TNX_M1.csv"
TNX_M2_csv_path = r"raw_data\TNX_M2.csv"
TNX_H1_csv_path = r"raw_data\TNX_H1.csv"

# 数据库路径
XAUUSD_M_db_path = r"database\XAUUSD_M.db"
XAUUSD_H_db_path = r"database\XAUUSD_H.db"
XAUUSD_DXY_TNX_D1_bem_exchange_db_path = r"database\XAUUSD_DXY_TNX_D1_bem_exchange.db"
XAUUSD_DXY_TNX_D1_sm_est_db_path = r"database\XAUUSD_DXY_TNX_D1_sm_est.db"

# 输出路径
XAUUSD_DXY_TNX_comb_bem_exchange_txt_path = r"report\XAUUSD_DXY_TNX_comb_exchange_bem.txt"
XAUUSD_DXY_TNX_comb_sm_est_txt_path = r"report\XAUUSD_DXY_TNX_comb_sm_est.txt"
XAUUSD_bem_exchange_txt_path = r"report\XAUUSD_bem_exchange.txt"
XAUUSD_sm_est_txt_path = r"report\XAUUSD_sm_est.txt"
XAUUSD_DXY_TNX_D1_bem_exchange_xlsx_path = r"report\XAUUSD_DXY_TNX_D1_bem_exchange.xlsx"
XAUUSD_DXY_TNX_D1_sm_est_xlsx_path = r"report\XAUUSD_DXY_TNX_D1_sm_est.xlsx"

# 首次运行程序


def initial_launcher():

    # 拉取XAUUSD,DXY,TNX数据
    pull_from_MT5_M1(XAUUSD_M1_csv_path, 90000)
    pull_from_MT5_H1(XAUUSD_H1_csv_path)
    pull_from_yfinance(DXY_M1_csv_path, TNX_M1_csv_path, "1m", "5d")
    pull_from_yfinance_H1(DXY_H1_csv_path, TNX_H1_csv_path)

    # 价格标准化后组合和入库处理
    XAUUSD_std(XAUUSD_M1_csv_path, XAUUSD_M_db_path)
    DXY_std(DXY_M1_csv_path, XAUUSD_M_db_path)
    TNX_std(TNX_M1_csv_path, XAUUSD_M_db_path)

    XAUUSD_std(XAUUSD_H1_csv_path, XAUUSD_H_db_path)
    DXY_std(DXY_H1_csv_path, XAUUSD_H_db_path)
    TNX_std(TNX_H1_csv_path, XAUUSD_H_db_path)

    # 价格组合
    comb(XAUUSD_H_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "best_effort_match", "all")
    comb(XAUUSD_H_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "strict_match", "all")
    comb(XAUUSD_M_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "best_effort_match", "all")
    comb(XAUUSD_M_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "strict_match", "all")

    # 趋势测定
    def_down_XAUUSD_DXY_TNX(
        XAUUSD_DXY_TNX_D1_bem_exchange_db_path, XAUUSD_3_price, DXY_3_price, TNX_3_price, 9/3)
    def_down_XAUUSD_DXY_TNX(
        XAUUSD_DXY_TNX_D1_sm_est_db_path, XAUUSD_3_price, DXY_3_price, TNX_3_price, 9/3)

    # 实时信号
    current_signal(XAUUSD_M_db_path, XAUUSD_DXY_TNX_D1_bem_exchange_db_path, XAUUSD_bem_exchange_txt_path,
                   XAUUSD_DXY_TNX_comb_bem_exchange_txt_path, "exchange", XAUUSD_3_price, 9/3, "best_effort_match", "all", bot_token)
    current_signal(XAUUSD_M_db_path, XAUUSD_DXY_TNX_D1_sm_est_db_path, XAUUSD_sm_est_txt_path,
                   XAUUSD_DXY_TNX_comb_sm_est_txt_path, "est", XAUUSD_3_price, 9/3, "strict_match", "all", bot_token)

    # 生成各时区日线行情表
    vis_trend(XAUUSD_DXY_TNX_D1_bem_exchange_db_path,
              XAUUSD_DXY_TNX_D1_bem_exchange_xlsx_path)
    vis_trend(XAUUSD_DXY_TNX_D1_sm_est_db_path,
              XAUUSD_DXY_TNX_D1_sm_est_xlsx_path)

# 分钟循环过程


def minute_cycle():
    # 拉取数据
    pull_from_MT5_M1(XAUUSD_M1_csv_path, 5)
    pull_from_yfinance(DXY_M1_csv_path, TNX_M1_csv_path, "1m", "2d")

    # 分钟数据入库
    XAUUSD_std(XAUUSD_M1_csv_path, XAUUSD_M_db_path, 5)
    DXY_std(DXY_M1_csv_path, XAUUSD_M_db_path, 5)
    TNX_std(TNX_M1_csv_path, XAUUSD_M_db_path, 5)

    # 分钟价格组合
    comb(XAUUSD_M_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "best_effort_match", 5)
    comb(XAUUSD_M_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "strict_match", 5)

    # 实时信号
    current_signal(XAUUSD_M_db_path, XAUUSD_DXY_TNX_D1_bem_exchange_db_path, XAUUSD_bem_exchange_txt_path,
                   XAUUSD_DXY_TNX_comb_bem_exchange_txt_path, "exchange", XAUUSD_3_price, 9/3, "best_effort_match", 1, bot_token, user_id, group_id)
    current_signal(XAUUSD_M_db_path, XAUUSD_DXY_TNX_D1_sm_est_db_path, XAUUSD_sm_est_txt_path,
                   XAUUSD_DXY_TNX_comb_sm_est_txt_path, "est", XAUUSD_3_price, 9/3, "strict_match", 1, bot_token, user_id, group_id)

# 每日循环过程


def daily_cycle():
    # 拉取interval=1h的数据
    pull_from_MT5_H1(XAUUSD_H1_csv_path)
    pull_from_yfinance_H1(DXY_H1_csv_path, TNX_H1_csv_path)

    # 小时级数据入库
    XAUUSD_std(XAUUSD_H1_csv_path, XAUUSD_H_db_path, 60)
    DXY_std(DXY_H1_csv_path, XAUUSD_H_db_path, 60)
    TNX_std(TNX_H1_csv_path, XAUUSD_H_db_path, 60)

    # 小时级价格组合
    comb(XAUUSD_H_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "best_effort_match", 60)
    comb(XAUUSD_H_db_path, XAUUSD_coef, DXY_coef,
         TNX_coef, constant, "strict_match", 60)

    # 趋势测定
    def_down_XAUUSD_DXY_TNX(
        XAUUSD_DXY_TNX_D1_bem_exchange_db_path, XAUUSD_3_price, DXY_3_price, TNX_3_price, 9/3)
    def_down_XAUUSD_DXY_TNX(
        XAUUSD_DXY_TNX_D1_sm_est_db_path, XAUUSD_3_price, DXY_3_price, TNX_3_price, 9/3)

    # 生成各时区日线行情表
    vis_trend(XAUUSD_DXY_TNX_D1_bem_exchange_db_path,
              XAUUSD_DXY_TNX_D1_bem_exchange_xlsx_path)
    vis_trend(XAUUSD_DXY_TNX_D1_sm_est_db_path,
              XAUUSD_DXY_TNX_D1_sm_est_xlsx_path)


# schedule 定期执行
def carry_out():
    execute_way = input("execute_way:(initial/normal):")

    if execute_way == "initial":
        print("开始执行首次入库")
        initial_launcher()

    elif execute_way == "normal":
        print("开始执行日常实时常驻程序")
        # 每分钟执行一次minute_cycle
        schedule.every().minute.do(minute_cycle)
        # 每天执行一次daily_cycle
        schedule.every().day.do(daily_cycle)

carry_out()
