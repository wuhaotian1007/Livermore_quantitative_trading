# -*- encoding: utf-8 -*-
'''
@File    :   visualization.py
@Time    :   2021/07/06 10:48:10
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
from os import write
import sqlite3
import xlsxwriter
from xlsxwriter import workbook


class vis_by_excel:
    def __init__(self, trading_record_db_path, output_xlsx_path, monthly_info_png_path, monthly_surplus_png_path):
        # 建立数据库连接
        conn_trading_record_db = sqlite3.connect(trading_record_db_path)
        cur_trading_record_db = conn_trading_record_db.cursor()

        cur_trading_record_db.execute(
            "select surplus,net_profit from history_list where ID = 1")
        i = cur_trading_record_db.fetchone()
        initial_surplus = i[0] - i[1]

        # 创建一个工作簿
        xl = xlsxwriter.Workbook(filename=output_xlsx_path)
        xl.formats[0].set_align('center')
        xl.formats[0].set_border(1)
        xl.formats[0].set_valign('vcenter')
        xl.formats[0].set_font_name('微软雅黑')
        # 创建一个sheet对象
        sheet = xl.add_worksheet('交易历史')

        # 初始化样式
        style_big = xl.add_format({'font_size': 25, 'bold': True, 'align': 'center',
                                   'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})
        style_blue = xl.add_format({'fg_color': '#87CEEB', 'align': 'center',
                                    'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})
        style_red = xl.add_format({'font_color': '#FF0000', 'align': 'center',
                                   'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})

        style_red2 = xl.add_format({'font_color': '#FF0000', 'align': 'center', 'fg_color': '#F0F8FF',
                                    'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})
        style2 = xl.add_format({'align': 'center', 'fg_color': '#F0F8FF',
                                'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})

        # 绘制xlsx框架
        sheet.write(0, 0, "初始净值", style_big)
        sheet.set_column(1, 4, 12)
        sheet.set_column(0, 0, 25)
        sheet.set_column(5, 5, 25)
        sheet.set_column(6, 23, 12)
        sheet.set_row(0, 50)
        sheet.set_row(1, 22)
        sheet.merge_range(0, 1, 0, 22, initial_surplus, style_big)
        sheet.write(1, 0, '交易时间', style_blue)
        sheet.write(1, 1, '交易品种', style_blue)
        sheet.write(1, 2, '类型', style_blue)
        sheet.write(1, 3, '交易量', style_blue)
        sheet.write(1, 4, '交易价位', style_blue)
        sheet.write(1, 5, '平仓时间', style_blue)
        sheet.write(1, 6, '平仓价位', style_blue)
        sheet.write(1, 7, '手续费', style_blue)
        sheet.write(1, 8, '库存费', style_blue)
        sheet.write(1, 9, '预付款', style_blue)
        sheet.write(1, 10, '净利润', style_blue)
        sheet.write(1, 11, '期间最高价', style_blue)
        sheet.write(1, 12, '期间最低价', style_blue)
        sheet.write(1, 13, '极限利润', style_blue)
        sheet.write(1, 14, '极限亏损', style_blue)
        sheet.write(1, 15, '名义利润率', style_blue)
        sheet.write(1, 16, '总利润率', style_blue)
        sheet.write(1, 17, '利润出金比例', style_blue)
        sheet.write(1, 18, '净值结余', style_blue)
        sheet.write(1, 19, '月度利润率', style_blue)
        sheet.write(1, 20, '季度利润率', style_blue)
        sheet.write(1, 21, '年度利润率', style_blue)
        sheet.write(1, 22, '历史总利润率', style_blue)
        sheet.write(1, 23, '备注', style_blue)

        # 选取数据库中的所有交易数据
        cur_trading_record_db.execute("select * from history_list")
        history_list = cur_trading_record_db.fetchall()

        # 创建空变量用于收集数据
        last_trade_month = ""
        last_trade_quarter = ""
        last_trade_year = ""
        month_sum_profit = 0
        quarter_sum_profit = 0
        year_sum_profit = 0
        total_sum_profit = 0

        for history in history_list:
            ID = history[0]
            # 设置行高
            sheet.set_row(1 + ID, 33)

            # 判断ID奇偶性，不同行用两种颜色区分开
            if ID % 2 == 0:
                if history[11] >= 0:
                    sheet.write(1 + ID, 0, history[1])
                    sheet.write(1 + ID, 1, history[2])
                    sheet.write(1 + ID, 2, history[3])
                    sheet.write(1 + ID, 3, history[4])
                    sheet.write(1 + ID, 4, history[5])
                    sheet.write(1 + ID, 5, history[6])
                    sheet.write(1 + ID, 6, history[7])
                    sheet.write(1 + ID, 7, history[8])
                    sheet.write(1 + ID, 8, history[9])
                    sheet.write(1 + ID, 9, history[10])
                    sheet.write(1 + ID, 10, history[11])
                    sheet.write(1 + ID, 11, history[12])
                    sheet.write(1 + ID, 12, history[13])
                    sheet.write(1 + ID, 13, history[14])
                    sheet.write(1 + ID, 14, history[15])
                    sheet.write(1 + ID, 15, history[16])
                    sheet.write(1 + ID, 16, history[17])
                    sheet.write(1 + ID, 17, history[18])
                    sheet.write(1 + ID, 18, history[19])
                    sheet.write(1 + ID, 23, history[20])
                else:
                    sheet.write(1 + ID, 0, history[1], style_red)
                    sheet.write(1 + ID, 1, history[2], style_red)
                    sheet.write(1 + ID, 2, history[3], style_red)
                    sheet.write(1 + ID, 3, history[4], style_red)
                    sheet.write(1 + ID, 4, history[5], style_red)
                    sheet.write(1 + ID, 5, history[6], style_red)
                    sheet.write(1 + ID, 6, history[7], style_red)
                    sheet.write(1 + ID, 7, history[8], style_red)
                    sheet.write(1 + ID, 8, history[9], style_red)
                    sheet.write(1 + ID, 9, history[10], style_red)
                    sheet.write(1 + ID, 10, history[11], style_red)
                    sheet.write(1 + ID, 11, history[12], style_red)
                    sheet.write(1 + ID, 12, history[13], style_red)
                    sheet.write(1 + ID, 13, history[14], style_red)
                    sheet.write(1 + ID, 14, history[15], style_red)
                    sheet.write(1 + ID, 15, history[16], style_red)
                    sheet.write(1 + ID, 16, history[17], style_red)
                    sheet.write(1 + ID, 17, history[18], style_red)
                    sheet.write(1 + ID, 18, history[19], style_red)
                    sheet.write(1 + ID, 23, history[20], style_red)
            else:
                if history[11] >= 0:
                    sheet.write(1 + ID, 0, history[1], style2)
                    sheet.write(1 + ID, 1, history[2], style2)
                    sheet.write(1 + ID, 2, history[3], style2)
                    sheet.write(1 + ID, 3, history[4], style2)
                    sheet.write(1 + ID, 4, history[5], style2)
                    sheet.write(1 + ID, 5, history[6], style2)
                    sheet.write(1 + ID, 6, history[7], style2)
                    sheet.write(1 + ID, 7, history[8], style2)
                    sheet.write(1 + ID, 8, history[9], style2)
                    sheet.write(1 + ID, 9, history[10], style2)
                    sheet.write(1 + ID, 10, history[11], style2)
                    sheet.write(1 + ID, 11, history[12], style2)
                    sheet.write(1 + ID, 12, history[13], style2)
                    sheet.write(1 + ID, 13, history[14], style2)
                    sheet.write(1 + ID, 14, history[15], style2)
                    sheet.write(1 + ID, 15, history[16], style2)
                    sheet.write(1 + ID, 16, history[17], style2)
                    sheet.write(1 + ID, 17, history[18], style2)
                    sheet.write(1 + ID, 18, history[19], style2)
                    sheet.write(1 + ID, 23, history[20], style2)
                else:
                    sheet.write(1 + ID, 0, history[1], style_red2)
                    sheet.write(1 + ID, 1, history[2], style_red2)
                    sheet.write(1 + ID, 2, history[3], style_red2)
                    sheet.write(1 + ID, 3, history[4], style_red2)
                    sheet.write(1 + ID, 4, history[5], style_red2)
                    sheet.write(1 + ID, 5, history[6], style_red2)
                    sheet.write(1 + ID, 6, history[7], style_red2)
                    sheet.write(1 + ID, 7, history[8], style_red2)
                    sheet.write(1 + ID, 8, history[9], style_red2)
                    sheet.write(1 + ID, 9, history[10], style_red2)
                    sheet.write(1 + ID, 10, history[11], style_red2)
                    sheet.write(1 + ID, 11, history[12], style_red2)
                    sheet.write(1 + ID, 12, history[13], style_red2)
                    sheet.write(1 + ID, 13, history[14], style_red2)
                    sheet.write(1 + ID, 14, history[15], style_red2)
                    sheet.write(1 + ID, 15, history[16], style_red2)
                    sheet.write(1 + ID, 16, history[17], style_red2)
                    sheet.write(1 + ID, 17, history[18], style_red2)
                    sheet.write(1 + ID, 18, history[19], style_red2)
                    sheet.write(1 + ID, 23, history[20], style_red2)

            # 合并单元格计算月利润率
            net_profit = history[11]
            row_index = 1 + ID
            trade_month = history[6][0:7]

            # 如果本月信息和上月不同即为新的一月时
            if trade_month != last_trade_month:
                end_row_index = row_index - 1

                # 当不是记录刚开始时时计算上个月月度利润率
                if end_row_index != 1:
                    # 上个月月度利润率
                    month_profit_margin = month_sum_profit / last_month_surplus
                    month_profit_margin = "%.2f%%" % (
                        month_profit_margin * 100)

                    # 合并单元格并记录
                    sheet.merge_range(begin_row_index, 19, end_row_index,
                                      19, month_profit_margin)

                # 开始记录本月月度利润率
                begin_row_index = row_index
                month_sum_profit = net_profit

                # 本月净值结余
                # 第一个月时净值结余等于初识净值
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
                    month_profit_margin = "%.2f%%" % (
                        month_profit_margin * 100)
                    sheet.merge_range(begin_row_index, 19, end_row_index,
                                      19,  month_profit_margin)

            last_trade_month = trade_month

            # 合并单元格计算季度利润率
            quarter = {"01": "Q1", "02": "Q1", "03": "Q1", "04": "Q2", "05": "Q2", "06": "Q2",
                       "07": "Q3", "08": "Q3", "09": "Q3", "10": "Q4", "11": "Q4", "12": "Q4", }
            trade_quarter = trade_month[0:4] + quarter[trade_month[5:7]]

            # 如果本月信息和上月不同即为新的一季度时
            if trade_quarter != last_trade_quarter:
                end_row_index_quarter = row_index - 1

                # 当不是记录刚开始时时计算上个季度季度利润率
                if end_row_index_quarter != 1:
                    # 上个季度季度利润率
                    quarter_profit_margin = quarter_sum_profit / last_quarter_surplus
                    quarter_profit_margin = "%.2f%%" % (
                        quarter_profit_margin * 100)

                    # 合并单元格并记录
                    sheet.merge_range(begin_row_index_quarter, 20, end_row_index_quarter,
                                      20, quarter_profit_margin)

                # 开始记录本季度利润率
                begin_row_index_quarter = row_index
                quarter_sum_profit = net_profit

                # 本季度净值结余
                # 第一个季度时净值结余等于初识净值
                if last_trade_quarter == "":
                    last_quarter_surplus = initial_surplus
                # 不是第一个季度时
                else:
                    cur_trading_record_db.execute(
                        "select surplus from history_list where ID = {}".format(ID-1))
                    last_quarter_surplus = cur_trading_record_db.fetchone()[0]
            else:
                quarter_sum_profit += net_profit
                if ID == len(history_list):
                    end_row_index_quarter = row_index
                    quarter_profit_margin = quarter_sum_profit / last_quarter_surplus
                    quarter_profit_margin = "%.2f%%" % (
                        quarter_profit_margin * 100)
                    sheet.merge_range(begin_row_index_quarter, 20, end_row_index_quarter,
                                      20, quarter_profit_margin)

            last_trade_quarter = trade_quarter

            # 计算年度利润率
            trade_year = trade_month[0:4]
            # 如果本年信息和上年不同即为新的一年时
            if trade_year != last_trade_year:
                end_row_index_year = row_index - 1

                # 当不是记录刚开始时时计算上个年度利润率
                if end_row_index_year != 1:
                    # 上年年度利润率
                    year_profit_margin = year_sum_profit / last_year_surplus
                    year_profit_margin = "%.2f%%" % (year_profit_margin * 100)

                    # 合并单元格并记录
                    sheet.merge_range(begin_row_index_year, 21, end_row_index_year,
                                      21,  year_profit_margin)

                # 开始记录本年年度利润率
                begin_row_index_year = row_index
                year_sum_profit = net_profit

                # 本本年净值结余
                # 第一年时净值结余等于初识净值
                if last_trade_year == "":
                    last_year_surplus = initial_surplus
                # 不是第一年时
                else:
                    cur_trading_record_db.execute(
                        "select surplus from history_list where ID = {}".format(ID-1))
                    last_year_surplus = cur_trading_record_db.fetchone()[0]
            else:
                year_sum_profit += net_profit
                if ID == len(history_list):
                    end_row_index_year = row_index
                    year_profit_margin = year_sum_profit / last_year_surplus
                    year_profit_margin = "%.2f%%" % (year_profit_margin * 100)
                    sheet.merge_range(begin_row_index_year, 21, end_row_index_year,
                                      21, year_profit_margin)

            last_trade_year = trade_year

            # 计算总利润率
            total_sum_profit += net_profit
            if ID == len(history_list):
                total_profit_margin = total_sum_profit / initial_surplus
                total_profit_margin = "%.2f%%" % (total_profit_margin * 100)
                sheet.merge_range(2, 22, ID + 1,
                                  22,  total_profit_margin)

         # 在xlsx中插入图标
        sheet.insert_image(len(history_list) + 5, 0, monthly_info_png_path)
        sheet.insert_image(len(history_list) + 5, 10, monthly_surplus_png_path)

        # 断开xlsx连接
        xl.close()

        print("交易历史可视化报表已生成")