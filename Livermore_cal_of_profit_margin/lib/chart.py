# -*- encoding: utf-8 -*-
'''
@File    :   chart.py
@Time    :   2021/07/06 10:48:10
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter


class draw_chart:
    def __init__(self, trading_record_db_path, monthly_info_png_path, monthly_surplus_png_path):
        # 建立数据库连接
        conn_trading_record_db = sqlite3.connect(trading_record_db_path)
        cur_trading_record_db = conn_trading_record_db.cursor()

        cur_trading_record_db.execute(
            "select surplus,net_profit from history_list where ID = 1")
        i = cur_trading_record_db.fetchone()
        initial_surplus = i[0] - i[1]

        cur_trading_record_db.execute("select * from history_list")
        history_list = cur_trading_record_db.fetchall()

        last_trade_month = ""
        last_trade_quarter = ""
        last_trade_year = ""
        month_sum_profit = 0
        quarter_sum_profit = 0
        year_sum_profit = 0
        monthly_list = []

        for history in history_list:
            ID = history[0]
            # 计算月度信息
            net_profit = history[11]
            row_index = 1 + ID
            trade_month = history[1][0:7]
            trade_month = trade_month.replace(".", "-")

            # 如果本月信息和上月不同即为新的一月时
            if trade_month != last_trade_month:
                end_row_index = row_index - 1

                # 当不是记录刚开始时时计算上个月月度利润率,净值结余，净利润
                if end_row_index != 1:
                    # 上个月月度利润率
                    month_profit_margin = month_sum_profit / last_month_surplus
                    monthly_list.append([last_trade_month, round(
                        last_month_surplus + month_sum_profit, 2), round(month_sum_profit, 2), round(month_profit_margin, 3)])

                # 开始记录本月月度利润率
                begin_row_index = row_index
                month_sum_profit = net_profit

            # 本月净值结余
                # 第一个月时，净值结余等于初识净值
                if last_trade_month == "":
                    last_month_surplus = initial_surplus
                # 不是第一个月时
                else:
                    cur_trading_record_db.execute(
                        "select surplus from history_list where ID = {}".format(ID-1))
                    last_month_surplus = cur_trading_record_db.fetchone()[0]
            else:
                month_sum_profit += net_profit
                if ID == len(history_list):
                    end_row_index = row_index
                    month_profit_margin = month_sum_profit / last_month_surplus
                    monthly_list.append([last_trade_month, round(
                        last_month_surplus + month_sum_profit, 2), round(month_sum_profit, 2), round(month_profit_margin, 3)])

            last_trade_month = trade_month

        df = pd.DataFrame(monthly_list, columns=[
            'date', 'surplus', 'net_profit', 'profit_margin'])
        x = df.date
        y = df.surplus
        y2 = df.net_profit
        y3 = df.profit_margin
        # 定义颜色
        color1 = '#0085c3'
        color2 = '#7ab800'
        color3 = '#dc5034'

        # 设置图像大小
        fig = plt.figure(figsize=(10, 8))
        # 1x1网格，第一个子图
        ax = fig.add_subplot(111)
        # 绘制折线图
        ax.plot(x, y, label="surplus", marker='o', color=color1)
        ax.plot(x, y2, label="net_profit", marker='o', color=color2)
        for i, j in zip(x, y):
            ax.text(i, j, j, color=color1, fontsize=15)
        for i, j in zip(x, y2):
            ax.text(i, j, j, color=color2, fontsize=15)

        # 增加网格线并设置透明度
        plt.grid(alpha=0.4)
        # 增加标签
        plt.legend(loc='best')
        # 保存图片至路径
        plt.savefig(monthly_info_png_path)

        # 设置图像大小
        fig2 = plt.figure(figsize=(10, 8))
        ax2 = fig2.add_subplot(111)
        # 绘制折线图
        ax2.plot(x, y3, label="profit_margin", marker='o', color=color1)
        for i, j in zip(x, y3):
            ax2.text(i, j, j, color=color1, fontsize=15)

        # 增加网格线并设置透明度
        plt.grid(alpha=0.4)
        # 增加标签
        plt.legend(loc='best')
        # 保存图片至路径
        plt.savefig(monthly_surplus_png_path)

        print("图表绘制成功")
