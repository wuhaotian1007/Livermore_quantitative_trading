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
import configparser

from lib.pull_data.pull_from_MT5 import pull_from_MT5_H1,pull_from_MT5_M1
from lib.pull_data.pull_from_yfinance import pull_from_yfinance_H1,pull_from_yfinance
from lib.standardization.XAUUSD_std import XAUUSD_std,DXY_std,TNX_std
from lib.standardization.comb import comb
from lib.trend_and_signal.trend_est import def_down_XAUUSD_DXY_TNX
from lib.trend_and_signal.current_signal import current_signal

# 读取全局配置
def load_config():
    conf= configparser.ConfigParser()
    conf.read('global.conf')
    onedrive_path = conf.get("global", "Onedrive_path")

# 读取组合价格配置
def load_XAUUSD_DXY_TNX_coef():

    global XAUUSD_coef,DXY_coef,TNX_coef

    conf = configparser.ConfigParser()
    conf.read('XAUUSD_DXY_TNX_comb.conf')

    # 读取组合各品类组合系数
    XAUUSD_coef = conf.get("XAUUSD_DXY_TNX_comb_coef","XAUUSD")
    DXY_coef = conf.get("XAUUSD_DXY_TNX_comb_coef","DXY")
    TNX_coef = conf.get("XAUUSD_DXY_TNX_comb_coef","TNX")
