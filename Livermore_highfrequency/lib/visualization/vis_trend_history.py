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


class vis_trend:
    def __init__(self,trendsignal_db_path, output_xlsx_path):

        # 建立数据库连接
        conn_trendsignal_db = sqlite3.connect(trendsignal_db_path)
        cur_trendsignal_db = conn_trendsignal_db.cursor()

        # 创建一个工作簿
        xl = xlsxwriter.Workbook(filename=output_xlsx_path)

        # 创建一个sheet对象
        sheet = xl.add_worksheet('趋势信号')

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


        # 读取所有数据获得列表
        cur_trendsignal_db.execute("select * from STOCK_list")
        data_list = cur_trendsignal_db.fetchall()

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


        # 断开xlsx连接
        xl.close()
        print("可视化报表成功生成")

if __name__ == "__main__":
    vis_trend(r"database/XAUUSD_DXY_TNX_D1_bem_exchange.db",r"report/XAUUSD_DXY_TNX_D1_bem_exchange.xlsx")

