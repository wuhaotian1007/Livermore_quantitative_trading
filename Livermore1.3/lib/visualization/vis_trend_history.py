# -*- encoding: utf-8 -*-
'''
@File    :   vis_downtrend_history.py
@Time    :   2021/08/11 09:49:22
@Author  :   Wuhaotian
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
# here put the import lib
from datetime import date
import datetime
from os import write
import sqlite3
import xlsxwriter
import calendar
from xlsxwriter import workbook


class vis_trend_history:
    def __init__(self, trading_record_db_path, trendsignal_db_path, output_xlsx_path):

        # 建立数据库连接
        conn_trading_record_db = sqlite3.connect(trading_record_db_path)
        cur_trading_record_db = conn_trading_record_db.cursor()

        conn_trendsignal_db = sqlite3.connect(trendsignal_db_path)
        cur_trendsignal_db = conn_trendsignal_db.cursor()

        # 创建一个工作簿
        xl = xlsxwriter.Workbook(filename=output_xlsx_path)

        # 创建一个sheet对象
        sheet = xl.add_worksheet('趋势信号与交易历史')

        format_border = xl.add_format({'border': 1})   # 设置边框格式
        sheet.conditional_format(
            'A1:XFD1048576', {'type': 'no_blanks', 'format': format_border})

        # 初始化样式
        style_big = xl.add_format({'font_size': 20, 'bold': True, 'align': 'center',
                                   'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_bold = xl.add_format({'bold': True, 'align': 'center',
                                    'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_red_fg_black = xl.add_format({'font_color': '#FF0000', 'fg_color': '#000000', 'align': 'center',
                                            'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_red = xl.add_format({'font_color': '#FF0000', 'align': 'center',
                                   'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_blue_fg_black = xl.add_format({'font_color': '#00BFFF', 'fg_color': '#000000', 'align': 'center',
                                             'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑'})

        style_blue_fg_red = xl.add_format({'font_color': '#00BFFF', 'fg_color': '#FF0000', 'align': 'center',
                                           'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_black_fg_red = xl.add_format({'font_color': '#000000', 'fg_color': '#FF0000', 'align': 'center',
                                            'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_blue = xl.add_format({'font_color': '#00BFFF', 'align': 'center',
                                    'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_green = xl.add_format({'font_color': '#008000', 'align': 'center',
                                     'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_white = xl.add_format({'font_color': '#FFFFFF', 'align': 'center',
                                     'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_def = xl.add_format(
            {'align': 'center', 'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        style_new_line = xl.add_format(
            {'align': 'center', 'border': 1, 'valign': 'vcenter', 'font_name': '微软雅黑', 'text_wrap': True})

        # 绘制框架
        # 表格框架样式
        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 25, 10)
        sheet.set_column(26, 26, 80)
        sheet.set_column(27, 27, 10)
        sheet.set_column(28, 28, 50)
        sheet.set_column(29, 35, 10)

        # 表格框架内容
        sheet.write(0, 0, "日期", style_big)
        sheet.merge_range(0, 1, 0, 7, 'XAUUSD 7=3点', style_big)
        sheet.merge_range(0, 8, 0, 13, 'DXY 0.3=3点', style_big)
        sheet.merge_range(0, 14, 0, 19, '^TNX 0.03=3点', style_big)
        sheet.merge_range(0, 20, 0, 25, 'comb 9=3点', style_big)
        sheet.write(1, 1, 'VOLUME', style_def)
        sheet.write(1, 1, 'VOLUME', style_def)
        sheet.write(1, 2, '次级回升', style_blue)
        sheet.write(1, 8, '次级回升', style_blue)
        sheet.write(1, 14, '次级回升', style_blue)
        sheet.write(1, 20, '次级回升', style_blue)
        sheet.write(1, 3, '自然回升', style_blue)
        sheet.write(1, 9, '自然回升', style_blue)
        sheet.write(1, 15, '自然回升', style_blue)
        sheet.write(1, 21, '自然回升', style_blue)
        sheet.write(1, 4, '上升趋势', style_def)
        sheet.write(1, 10, '上升趋势', style_def)
        sheet.write(1, 16, '上升趋势', style_def)
        sheet.write(1, 22, '上升趋势', style_def)
        sheet.write(1, 5, '下降趋势', style_red)
        sheet.write(1, 11, '下降趋势', style_red)
        sheet.write(1, 17, '下降趋势', style_red)
        sheet.write(1, 23, '下降趋势', style_red)
        sheet.write(1, 6, '自然回撤', style_blue)
        sheet.write(1, 12, '自然回撤', style_blue)
        sheet.write(1, 18, '自然回撤', style_blue)
        sheet.write(1, 24, '自然回撤', style_blue)
        sheet.write(1, 7, '次级回撤', style_blue)
        sheet.write(1, 13, '次级回撤', style_blue)
        sheet.write(1, 19, '次级回撤', style_blue)
        sheet.write(1, 25, '次级回撤', style_blue)
        sheet.write(1, 26, '趋势信号', style_def)
        sheet.write(1, 27, '操作', style_def)
        sheet.write(1, 28, '交易历史', style_def)
        sheet.write(1, 29, '日利润率', style_def)
        sheet.write(1, 30, '月度利润率', style_def)
        sheet.write(1, 31, '季度利润率', style_def)
        sheet.write(1, 32, '年度利润率', style_def)
        sheet.write(1, 33, '总利润率', style_def)

        # 读取所有数据获得列表
        cur_trendsignal_db.execute("select * from STOCK_list")
        data_list = cur_trendsignal_db.fetchall()

        # 创建空变量用于收集数据
        last_month = ""
        last_quarter = ""
        last_year = ""
        month_sum_profit = 0
        quarter_sum_profit = 0
        year_sum_profit = 0
        total_sum_profit = 0

        # 创建季度变换方法
        quarter_trans = {"01": "Q1", "02": "Q1", "03": "Q1", "04": "Q2", "05": "Q2", "06": "Q2",
                         "07": "Q3", "08": "Q3", "09": "Q3", "10": "Q4", "11": "Q4", "12": "Q4", }

        # 创建日期ID对应字典
        time_to_ID = {}

        # 获取初识净值
        cur_trading_record_db.execute(
            "select surplus,net_profit from history_list where ID = 1")
        i = cur_trading_record_db.fetchone()
        initial_surplus = i[0] - i[1]

        # 针对列表元素获得写入excel所需特征
        for data in data_list:
            ID = data[0]
            NAME = data[1]
            DATE = data[2]
            TIMESTICKER = data[3]
            PRICE = data[4]
            VOLUME = data[5]
            REC = data[6]
            COL = data[7]
            KEY = data[8]
            year = str(DATE[0:4])
            month = str((DATE[5:7]))
            day = str(DATE[8:])
            quarter = quarter_trans[month]

            # price所在行列
            row = (ID-1)//4 + 2
            column = COL + 6 * ((ID + 3) % 4) + 1

            # 补齐时间
            if ID % 4 == 1:
                sheet.write(ID//4 + 2, 0, DATE, style_bold)
            # 如果被记录
            if REC == 1:
                # 如果是自然回升回撤或次级回升回撤
                if COL == 1 or COL == 2 or COL == 5 or COL == 6:
                    # 如果是自然回撤关键点
                    if KEY == 1 and COL == 5:
                        sheet.write(row, column, PRICE, style_blue_fg_red)
                    elif KEY == 1 and COL == 2:
                        sheet.write(row, column, PRICE, style_blue_fg_black)
                    else:
                        sheet.write(row, column, PRICE, style_blue)
                # 如果是上升趋势和下降趋势
                else:
                    if KEY == 1 and COL == 3:
                        sheet.write(row, column, PRICE, style_black_fg_red)
                    elif KEY == 0 and COL == 3:
                        sheet.write(row, column, PRICE, style_def)
                    elif KEY == 1 and COL == 4:
                        sheet.write(row, column, PRICE, style_red_fg_black)
                    elif KEY == 0 and COL == 4:
                        sheet.write(row, column, PRICE, style_red)

            # 如果未被记录用白色字体记下
            elif REC == 0:
                sheet.write(row, column, PRICE, style_white)

            # 加上XAUUSD的volume
            if NAME == "XAUUSD":
                sheet.write(row, 1, VOLUME, style_def)

            # 加上comb的趋势信号和交易历史
            if NAME == "comb":
                cur_trendsignal_db.execute(
                    "select trendsignal from COMB_TREND where TIMESTICKER = {}".format(TIMESTICKER))
                if cur_trendsignal_db.fetchall():
                    cur_trendsignal_db.execute(
                        "select trendsignal from COMB_TREND where TIMESTICKER = {}".format(TIMESTICKER))
                    TREND = cur_trendsignal_db.fetchall()
                    signal_content = ""
                    if (1,) in TREND:
                        signal_content += "上升趋势结束"
                    if (2,) in TREND:
                        signal_content += "上升趋势恢复"
                    if (3,) in TREND:
                        signal_content += "下降趋势结束"
                    if (4,) in TREND:
                        signal_content += "下降趋势恢复"
                    if (10,) in TREND:
                        signal_content += "上升趋势结束(volume不足)"
                    if (20,) in TREND:
                        signal_content += "上升趋势恢复(volume不足)"
                    if (30,) in TREND:
                        signal_content += "下降趋势结束(volume不足)"
                    if (40,) in TREND:
                        signal_content += "下降趋势恢复(volume不足)"

                    if len(TREND) >= 2:
                        signal_content = signal_content[0:6]
                        signal_content += "//"

                    if (5,) in TREND:
                        cur_trendsignal_db.execute("select NOTE from COMB_TREND where TIMESTICKER = {} and TRENDSIGNAL = 5   ".format(
                            TIMESTICKER))
                        note = cur_trendsignal_db.fetchall()[-1][0]
                        cur_trendsignal_db.execute(
                            "select TRENDSIGNAL from COMB_TREND where DATE = '{}' and TRENDSIGNAL not in (5, 6, 50, 60)".format(note))
                        last_signal = cur_trendsignal_db.fetchall()[-1][0]

                        if last_signal == 1:
                            signal_content += "[{}的上升趋势结束]的[危险信号]".format(note)
                        elif last_signal == 2:
                            signal_content += "[{}的上升趋势恢复]的[危险信号]".format(note)
                        elif last_signal == 3:
                            signal_content += "[{}的下降趋势结束]的[危险信号]".format(note)
                        elif last_signal == 4:
                            signal_content += "[{}的下降趋势恢复]的[危险信号]".format(note)
                        elif last_signal == 10:
                            signal_content += "[{}的上升趋势结束(volume不足)]的[危险信号]".format(
                                note)
                        elif last_signal == 20:
                            signal_content += "[{}的上升趋势恢复(volume不足)]的[危险信号]".format(
                                note)
                        elif last_signal == 30:
                            signal_content += "[{}的下降趋势结束(volume不足)]的[危险信号]".format(
                                note)
                        elif last_signal == 40:
                            signal_content += "[{}的下降趋势恢复(volume不足)]的[危险信号]".format(
                                note)

                    if (50,) in TREND:
                        cur_trendsignal_db.execute("select NOTE from COMB_TREND where TIMESTICKER = {} and TRENDSIGNAL = 50".format(
                            TIMESTICKER))
                        note = cur_trendsignal_db.fetchall()[-1][0]
                        cur_trendsignal_db.execute(
                            "select TRENDSIGNAL from COMB_TREND where DATE = '{}' and TRENDSIGNAL not in (5, 6, 50, 60)".format(note))
                        last_signal = cur_trendsignal_db.fetchall()[-1][0]

                        if last_signal == 1:
                            signal_content += "[{}的上升趋势结束]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 2:
                            signal_content += "[{}的上升趋势恢复]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 3:
                            signal_content += "[{}的下降趋势结束]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 4:
                            signal_content += "[{}的下降趋势恢复]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 10:
                            signal_content += "[{}的上升趋势结束(volume不足)]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 20:
                            signal_content += "[{}的上升趋势恢复(volume不足)]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 30:
                            signal_content += "[{}的下降趋势结束(volume不足)]的[危险信号(volume不足)]".format(
                                note)
                        elif last_signal == 40:
                            signal_content += "[{}的下降趋势恢复(volume不足)]的[危险信号(volume不足)]".format(
                                note)

                    if (6,) in TREND:
                        signal_content += "[当前危险信号]"
                    if (60,) in TREND:
                        signal_content += "[当前危险信号(volume不足)]"

                    # 增加八月平仓预警
                    cur_trendsignal_db.execute(
                        "select AUG from COMB_TREND where TIMESTICKER = {0}".format(TIMESTICKER))
                    Aug_danger = cur_trendsignal_db.fetchone()[0]
                    if Aug_danger == "1":
                        sheet.write_rich_string(
                            row, 26, style_def, signal_content, style_red, "<八月平仓预警>", style_new_line)
                    else:
                        sheet.write(row, 26, signal_content, style_def)

                # 增加交易历史内容
                record_content = ""
                record_content2 = ""
                date_record = str(year) + "-" + str(month) + "-" + str(day)
                month_record = str(year) + "-" + str(month)
                year_record = str(year)

                # 记录买入数据
                cur_trading_record_db.execute(
                    "select trading_time, trading_type, trading_volume, trading_price from history_list where trading_time like '{0}'".format(date_record + "%"))

                trade_record = cur_trading_record_db.fetchall()

                # 记录平仓数据
                cur_trading_record_db.execute(
                    "select trading_time, trading_type, trading_volume, close_price, net_profit, surplus from history_list where close_time like '{0}'".format(date_record + "%"))

                close_record = cur_trading_record_db.fetchall()

                cur_trading_record_db.execute(
                    "select * from history_list where close_time like '{0}'".format(date_record + "%"))

                history_list = cur_trading_record_db.fetchall()

                # 如果只有买入操作
                if trade_record and not close_record:
                    sheet.write(row, 27, "买入", style_blue)

                    for n, i in enumerate(trade_record):
                        trading_time = i[0]
                        sim_date = trading_time[0:11].replace(".", "")
                        record_ID = "<" + sim_date + "#" + str(n + 1) + ">"
                        time_to_ID[trading_time] = record_ID
                        trading_type = str(i[1])
                        trading_volume = str(i[2])
                        trading_price = str(i[3])
                        record_content += record_ID + trading_type + " " + \
                            trading_volume + "@" + trading_price + "\n"

                    # 求平均价格
                    sum_price = 0
                    for i in trade_record:
                        sum_price += i[3]
                    average_price = round(sum_price/len(trade_record), 2)
                    record_content += "总平均价格：" + str(average_price)

                    sheet.write(row, 28, record_content, style_blue)

                # 如果只有平仓操作
                elif close_record and not trade_record:
                    sheet.write(row, 27, "平仓", style_red)

                    for i in close_record:
                        trading_time = i[0]
                        record_ID = time_to_ID[trading_time]
                        trading_type = str(i[1])
                        trading_volume = str(i[2])
                        close_price = str(i[3])
                        record_content += record_ID + trading_type + \
                            " " + trading_volume + "@" + close_price + "\n"

                    # 求单日利润率
                    sum_day_profit = 0
                    day_surplus = close_record[0][5] - close_record[0][4]
                    for i in close_record:
                        sum_day_profit += i[4]

                    sum_day_profit_margin = sum_day_profit / day_surplus
                    sum_day_profit_margin = "%.2f%%" % (
                        sum_day_profit_margin * 100)

                    if sum_day_profit >= 0:
                        sheet.write(
                            row, 29, sum_day_profit_margin, style_green)
                    else:
                        sheet.write(row, 29, sum_day_profit_margin, style_red)

                    record_content += "日净利润：" + str(round(sum_day_profit, 2))
                    sheet.write(row, 28, record_content, style_red)

                # 如果既有平仓也有买入操作
                elif trade_record and close_record:

                    sheet.write_rich_string(
                        row, 27, style_blue, "买入" + "\n", style_red, "平仓", style_new_line)

                    for n, i in enumerate(trade_record):
                        trading_time = i[0]
                        sim_date = trading_time[0:11].replace(".", "")
                        record_ID = "<" + sim_date + "#" + str(n + 1) + ">"
                        time_to_ID[trading_time] = record_ID
                        trading_type = str(i[1])
                        trading_volume = str(i[2])
                        trading_price = str(i[3])
                        record_content += record_ID + trading_type + " " + \
                            trading_volume + "@" + trading_price + "\n"

                    # 求平均价格
                    sum_price = 0
                    for i in trade_record:
                        sum_price += i[3]
                    average_price = round(sum_price/len(trade_record), 2)
                    record_content += "\t" + "总平均价格：" + \
                        str(average_price) + "\n"

                    for i in close_record:
                        trading_time = i[0]
                        record_ID = time_to_ID[trading_time]
                        trading_type = str(i[1])
                        trading_volume = str(i[2])
                        close_price = str(i[3])
                        record_content2 += record_ID + trading_type + \
                            " " + trading_volume + "@" + close_price + "\n"

                    # 求单日利润率
                    sum_day_profit = 0
                    day_surplus = close_record[0][5] - close_record[0][4]
                    for i in close_record:
                        sum_day_profit += i[4]

                    sum_day_profit_margin = sum_day_profit / day_surplus
                    sum_day_profit_margin = "%.2f%%" % (
                        sum_day_profit_margin * 100)

                    record_content2 += "日净利润：" + str(round(sum_day_profit, 2))

                    if sum_day_profit >= 0:
                        sheet.write(
                            row, 29, sum_day_profit_margin, style_green)
                    else:
                        sheet.write(row, 29, sum_day_profit_margin, style_red)

                    sheet.write_rich_string(
                        row, 28, style_blue, record_content, style_red, record_content2, style_new_line)

                # 合并单元格计算月利润率
                # 如果本月信息和上月不同即为新的一月时
                if month != last_month and ID != len(data_list):
                    end_row_index_month = row - 1

                    # 如果上个月度有交易
                    if month_sum_profit != 0:
                        # 上个月月度利润率
                        month_profit_margin = month_sum_profit / last_month_surplus
                        month_profit_margin = "%.2f%%" % (
                            month_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_month, 30, end_row_index_month,
                                          30, month_profit_margin, style_def)

                    # 开始记录本月月度利润率
                    # 总利润归0
                    month_sum_profit = 0
                    begin_row_index_month = row
                    cur_trading_record_db.execute(
                        "select net_profit,surplus from history_list where close_time like '{0}'".format(month_record + "%"))
                    month_info = cur_trading_record_db.fetchall()
                    if month_info:
                        last_month_surplus = month_info[0][1] - \
                            month_info[0][0]
                        for i in month_info:
                            month_sum_profit += i[0]

                elif ID == len(data_list):
                    # 如果上个月度有交易
                    if month_sum_profit != 0:
                        end_row_index_month = row
                        # 上个月月度利润率
                        month_profit_margin = month_sum_profit / last_month_surplus
                        month_profit_margin = "%.2f%%" % (
                            month_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_month, 30, end_row_index_month,
                                          30, month_profit_margin, style_def)

                last_month = month

                # 合并单元格计算季度利润率
                # 如果本季信息和上月不同即为新的一季时
                if quarter != last_quarter and ID != len(data_list):
                    end_row_index_quarter = row - 1

                    # 如果上个月度有交易
                    if quarter_sum_profit != 0:
                        # 上个季度季度利润率
                        quarter_profit_margin = quarter_sum_profit / last_quarter_surplus
                        quarter_profit_margin = "%.2f%%" % (
                            quarter_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_quarter, 31, end_row_index_quarter,
                                          31, quarter_profit_margin, style_def)

                    # 开始记录本季度季度利润率
                    # 总利润归0
                    quarter_sum_profit = 0
                    begin_row_index_quarter = row
                    if quarter == "Q1":
                        quarter_record = (
                            year + ".01%", year + ".02%", year + ".03%")
                    elif quarter == "Q2":
                        quarter_record = (
                            year + ".04%", year + ".05%", year + ".06%")
                    elif quarter == "Q3":
                        quarter_record = (
                            year + ".07%", year + ".08%", year + ".09%")
                    elif quarter == "Q4":
                        quarter_record = (
                            year + ".10%", year + ".11%", year + ".12%")

                    cur_trading_record_db.execute(
                        "select net_profit,surplus from history_list where close_time like '{0}' or close_time like '{1}' or close_time like '{2}'".format(*quarter_record))
                    quarter_info = cur_trading_record_db.fetchall()
                    if quarter_info:
                        last_quarter_surplus = quarter_info[0][1] - \
                            quarter_info[0][0]
                        for i in quarter_info:
                            quarter_sum_profit += i[0]

                elif ID == len(data_list):
                    # 如果上个月度有交易
                    if quarter_sum_profit != 0:
                        end_row_index_quarter = row
                        # 上个季度季度利润率
                        quarter_profit_margin = quarter_sum_profit / last_quarter_surplus
                        quarter_profit_margin = "%.2f%%" % (
                            quarter_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_quarter, 31, end_row_index_quarter,
                                          31, quarter_profit_margin, style_def)

                last_quarter = quarter

                # 合并计算年度利润率
                if year != last_year and ID != len(data_list):
                    end_row_index_year = row - 1

                    # 如果上个年度有交易
                    if year_sum_profit != 0:
                        # 上年年度利润率
                        year_profit_margin = year_sum_profit / last_year_surplus
                        year_profit_margin = "%.2f%%" % (
                            year_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_year, 32, end_row_index_year,
                                          32, year_profit_margin, style_def)

                    # 开始记录本年年度利润率
                    # 总利润归0
                    year_sum_profit = 0
                    begin_row_index_year = row
                    cur_trading_record_db.execute(
                        "select net_profit,surplus from history_list where close_time like '{0}'".format(year_record + "%"))
                    year_info = cur_trading_record_db.fetchall()
                    if year_info:
                        last_year_surplus = year_info[0][1] - year_info[0][0]
                        for i in year_info:
                            year_sum_profit += i[0]

                elif ID == len(data_list):
                    # 如果上个年度有交易
                    if year_sum_profit != 0:
                        end_row_index_year = row
                        # 上年年度利润率
                        year_profit_margin = year_sum_profit / last_year_surplus
                        year_profit_margin = "%.2f%%" % (
                            year_profit_margin * 100)

                        # 合并单元格并记录
                        sheet.merge_range(begin_row_index_year, 32, end_row_index_year,
                                          32, year_profit_margin, style_def)

                last_year = year

        # 合并计算总利润率
        cur_trading_record_db.execute(
            "select net_profit,surplus from history_list")
        total_info = cur_trading_record_db.fetchall()
        if total_info:
            total_surplus = total_info[0][1] - total_info[0][0]
            for i in total_info:
                total_sum_profit += i[0]
        total_profit_margin = total_sum_profit / total_surplus
        total_profit_margin = "%.2f%%" % (total_profit_margin * 100)
        sheet.merge_range(2, 33, 1 + len(data_list)//4,
                            33, total_profit_margin, style_def)
        # 断开xlsx连接
        xl.close()
        print("可视化报表成功生成")

