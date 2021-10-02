# -*- encoding: utf-8 -*-
'''
@File    :   full_buy_price.py
@Time    :   2021/09/04 15:28:37
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
from os import close
import sqlite3

'''
根据已准备进入买入组合的趋势信号调用交易策略中的买入信号
与历史交易品类价格信息碰撞生成模拟买入记录
'''


class full_buy_price:
    def __init__(self, database_path):

        # 各个基础数据库路径
        strategy_db_path = database_path + r"\strategy.db"
        signal_comb_db_path = database_path + r"\trading_signal_comb.db"
        buy_strategy_db_path = database_path + r"\buy_strategy.db"
        trading_category_db_path = database_path + r"\trading_category.db"

        # 建立各个基础数据库连接
        conn_strategy = sqlite3.connect(strategy_db_path)
        cur_strategy = conn_strategy.cursor()

        conn_signal_comb = sqlite3.connect(signal_comb_db_path)
        cur_signal_comb = conn_signal_comb.cursor()

        conn_buy_strategy = sqlite3.connect(buy_strategy_db_path)
        cur_buy_strategy = conn_buy_strategy.cursor()

        conn_trading_category = sqlite3.connect(trading_category_db_path)
        cur_trading_category = conn_trading_category.cursor()

        # 获取各个策略基础信息
        cur_strategy.execute(
            "select trading_comb_ID, buy_strategy_ID, signal_comb_ID_list from strategy_list")
        strategy_info_list = cur_strategy.fetchall()

        # 开始策略遍历
        for strategy_info in strategy_info_list:
            trading_comb_ID = strategy_info[0]
            buy_strategy_ID = strategy_info[1]
            signal_comb_ID_list = strategy_info[2].split(",")

            # 读取买入策略信息
            cur_buy_strategy.execute("select step_method, buy_mode from buy_strategy_list where buy_strategy_ID = {0}".format(buy_strategy_ID))
            buy_strategy_info = cur_buy_strategy.fetchone()
            step_method_list = buy_strategy_info[0].split(",")
            buy_mode_list = buy_strategy_info[0].split(",")

            # 建立交易组合价格产生的趋势信号数据库连接
            signal_for_strategy_db_path = database_path + r"\trading_comb_signal\{}.db".format(trading_comb_ID)
            conn_signal_for_strategy = sqlite3.connect(signal_for_strategy_db_path)
            cur_signal_for_strategy = conn_signal_for_strategy.cursor()

            # 读取交易品类和三点取值
            cur_signal_for_strategy.execute("select TRADING_CATEGORY from TREND_FOR_STRATEGY")
            trading_category = cur_signal_for_strategy.fetchone()[0]

            cur_trading_category.execute("select THREE_POINTS from TRADING_CATEGORY_LIST where CATEGORY_NAME = {0}".format(trading_category))
            three_points = cur_trading_category.fetchone()[0]

            # 建立与交易品类高频数据连接
            trading_category_M12_db_path = database_path + r"\{0}_M12".format(trading_category)
            conn_trading_category_M12 = sqlite3.connect(trading_category_M12_db_path)
            cur_trading_category_M12 = conn_trading_category_M12.cursor()

            # 逐行遍历交易组合产生的趋势信号与交易品类高频数据碰撞
            # 碰撞时使用全信号全步进方法，生成全交易可能
            def full_trade():
                cur_signal_for_strategy.execute("select * from TREND_FOR_STRATEGY")
                signal_info_list = cur_signal_for_strategy.fetchall()
                for signal_info in signal_info_list:
                    ID = signal_info[0]
                    ts = signal_info[3]
                    trendsignal = signal_info[4]
                    aug =signal_info[5]
                    cur = signal_info[6]
                    close = signal_info[7]
                    SMA_5d = signal_info[8]
                    SMA_10d = signal_info[9]
                    SMA_30d = signal_info[10]
                    SMA_200d = signal_info[11]

                    # 根据趋势信号和交易信号组合判断交易方向
                    cur_signal_comb.execute("select trading_direction from trading_signal_comb_list where buy_siganal = {0}".format(trendsignal))
                    trading_direction = cur_signal_comb.fetchone()[0]

                    # 根据交易方向计算反向3点与反向6点取值
                    if trading_direction == "buy":
                        oppo_three = close - three_points
                        oppo_six = close - three_points * 2
                    elif trading_direction == "sell":
                        oppo_three = close + three_points
                        ojippo_six = close + three_points * 2
                    
                    # 建立潜在可行碰撞价格列表
                    aval_price_list = [cur, close, oppo_three, oppo_six, SMA_5d, SMA_10d, SMA_30d, SMA_200d]
                    prob_price_list = []

                    # 以实时价格为基准，舍弃比实时价格更差的价格，较优的价格加入可能价格列表中与历史价格记录碰撞
                    if trading_direction == "buy":
                        for price in aval_price_list:
                            if price <= cur:
                                prob_price_list.append(price)
                    elif trading_direction == "sell":
                        for price in aval_price_list:
                            if price >= cur:
                                prob_price_list.append(price)   
                    


            
