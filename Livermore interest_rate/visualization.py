# -*- encoding: utf-8 -*-
'''
@File    :   summary.py
@Time    :   2021/07/06 10:48:10
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3

import xlwt

# 建立数据库连接
conn = sqlite3.connect(
    r'C:\Users\sgnjim\Desktop\Livermore\Livermore_quantitative_trading\Livermore interest_rate\trading_records.db')
c = conn.cursor()

c.execute("select surplus from history_list where ID = 1")
initial_surplus = c.fetchone()[0]

# 创建一个工作簿
xl = xlwt.Workbook(encoding='utf-8')
# 创建一个sheet对象
sheet = xl.add_sheet('交易历史')

# 创建居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER
alignment.vert = xlwt.Alignment.VERT_CENTER

# 创建框线
borders = xlwt.Borders()
borders.left = 1
borders.right = 1
borders.top = 1
borders.bottom = 1

# 创建加粗加大字体
font_title = xlwt.Font()
font_title.height = 300
font_title.bold = True

# 创建加粗字体
font_bold = xlwt.Font()
font_bold.bold = True


# 创建蓝色背景
pattern_blue = xlwt.Pattern()
pattern_blue.pattern = xlwt.Pattern.SOLID_PATTERN
pattern_blue.pattern_fore_colour = 40

# 创建红色背景
pattern_red = xlwt.Pattern()
pattern_red.pattern = xlwt.Pattern.SOLID_PATTERN
pattern_red.pattern_fore_colour = 10

# 初始化样式
style_big = xlwt.XFStyle()
style_big.font = font_title
style_big.alignment = alignment
style_big.borders = borders

style_bold = xlwt.XFStyle()
style_bold.font = font_bold
style_bold.alignment = alignment
style_bold.pattern = pattern_blue

style_def = xlwt.XFStyle()
style_def.alignment = alignment
style_def.borders = borders

style_red = xlwt.XFStyle()
style_red.alignment = alignment
style_red.borders = borders
style_red.pattern = pattern_red

sheet.write(0, 0, "初识净值", style_big)
sheet.col(0).width = 7000
sheet.col(1).width = 3000
sheet.col(2).width = 3000
sheet.col(3).width = 3000
sheet.col(4).width = 3000
sheet.col(5).width = 7000
sheet.col(6).width = 3000
sheet.col(7).width = 3000
sheet.col(8).width = 3000
sheet.col(9).width = 3000
sheet.col(10).width = 3000
sheet.col(11).width = 3000
sheet.col(12).width = 3000
sheet.col(13).width = 3000
sheet.col(14).width = 3000
sheet.col(15).width = 3000
sheet.col(16).width = 3000
sheet.col(17).width = 3000
sheet.col(18).width = 3000
sheet.col(19).width = 3000
sheet.col(20).width = 3000
sheet.col(21).width = 4000


sheet.row(0).height_mismatch = True
sheet.row(0).height = 20 * 40
sheet.row(1).height_mismatch = True
sheet.row(1).height = 20 * 30

sheet.write_merge(0, 0, 1, 17, initial_surplus, style_big)
sheet.write(1, 0, '交易时间', style_bold)
sheet.write(1, 1, '交易品种', style_bold)
sheet.write(1, 2, '类型', style_bold)
sheet.write(1, 3, '交易量', style_bold)
sheet.write(1, 4, '交易价位', style_bold)
sheet.write(1, 5, '平仓时间', style_bold)
sheet.write(1, 6, '平仓价位', style_bold)
sheet.write(1, 7, '手续费', style_bold)
sheet.write(1, 8, '库存费', style_bold)
sheet.write(1, 9, '预付款', style_bold)
sheet.write(1, 10, '净利润', style_bold)
sheet.write(1, 11, '净值结余', style_bold)
sheet.write(1, 12, '期间最高价', style_bold)
sheet.write(1, 13, '期间最低价', style_bold)
sheet.write(1, 14, '极限利润', style_bold)
sheet.write(1, 15, '极限亏损', style_bold)
sheet.write(1, 16, '名义利润率', style_bold)
sheet.write(1, 17, '总利润率', style_bold)
sheet.write(1, 18, '月度利润率', style_bold)
sheet.write(1, 19, '季度利润率', style_bold)
sheet.write(1, 20, '年度利润率', style_bold)
sheet.write(1, 21, '备注', style_bold)

c.execute("select * from history_list")
history_list = c.fetchall()

last_trade_month = ""
last_trade_quarter = ""
last_trade_year = ""
month_sum_profit = 0
quarter_sum_profit = 0
year_sum_profit = 0

for history in history_list:
    ID = history[0]
    sheet.row(1+ID).height_mismatch = True
    sheet.row(1+ID).height = 20 * 30
    if history[11] >= 0:
        sheet.write(1 + ID, 0, history[1], style_def)
        sheet.write(1 + ID, 1, history[2], style_def)
        sheet.write(1 + ID, 2, history[3], style_def)
        sheet.write(1 + ID, 3, history[4], style_def)
        sheet.write(1 + ID, 4, history[5], style_def)
        sheet.write(1 + ID, 5, history[6], style_def)
        sheet.write(1 + ID, 6, history[7], style_def)
        sheet.write(1 + ID, 7, history[8], style_def)
        sheet.write(1 + ID, 8, history[9], style_def)
        sheet.write(1 + ID, 9, history[10], style_def)
        sheet.write(1 + ID, 10, history[11], style_def)
        sheet.write(1 + ID, 11, history[12], style_def)
        sheet.write(1 + ID, 12, history[13], style_def)
        sheet.write(1 + ID, 13, history[14], style_def)
        sheet.write(1 + ID, 14, history[15], style_def)
        sheet.write(1 + ID, 15, history[16], style_def)
        sheet.write(1 + ID, 16, history[17], style_def)
        sheet.write(1 + ID, 17, history[18], style_def)
        sheet.write(1 + ID, 21, history[19], style_def)
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
        sheet.write(1 + ID, 21, history[19], style_def)

    # 合并单元格计算月利润率
    net_profit = history[11]
    row_index = 1 + ID
    trade_month = history[1][0:7]

    # 如果本月信息和上月不同即为新的一月时
    if trade_month != last_trade_month:
        end_row_index = row_index - 1

        # 当不是记录刚开始时时计算上个月月度利润率
        if end_row_index != 1:
            # 上个月月度利润率
            month_profit_margin = month_sum_profit / last_month_surplus
            month_profit_margin = "%.2f%%" % (month_profit_margin * 100)

            # 合并单元格并记录
            sheet.write_merge(begin_row_index, end_row_index,
                              18, 18, month_profit_margin, style_def)

        # 开始记录本月月度利润率
        begin_row_index = row_index
        month_sum_profit = net_profit

        # 本月净值结余
        # 第一个月时
        if last_trade_month == "":
            last_month_surplus = initial_surplus
        # 不是第一个月时
        else:
            c.execute(
                "select surplus from history_list where ID = {}".format(ID-1))
            last_month_surplus = c.fetchone()[0]
    else:
        month_sum_profit += net_profit
        if ID == len(history_list):
            end_row_index = row_index
            month_profit_margin = month_sum_profit / last_month_surplus
            month_profit_margin = "%.2f%%" % (month_profit_margin * 100)
            sheet.write_merge(begin_row_index, end_row_index,
                              18, 18, month_profit_margin, style_def)

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
            quarter_profit_margin = "%.2f%%" % (quarter_profit_margin * 100)

            # 合并单元格并记录
            sheet.write_merge(begin_row_index_quarter, end_row_index_quarter,
                              19, 19, quarter_profit_margin, style_def)

        # 开始记录本季度利润率
        begin_row_index_quarter = row_index
        quarter_sum_profit = net_profit

        # 本季度净值结余
        # 第一个季度时
        if last_trade_quarter == "":
            last_quarter_surplus = initial_surplus
        # 不是第一个季度时
        else:
            c.execute(
                "select surplus from history_list where ID = {}".format(ID-1))
            last_quarter_surplus = c.fetchone()[0]
    else:
        quarter_sum_profit += net_profit
        if ID == len(history_list):
            end_row_index_quarter = row_index
            quarter_profit_margin = quarter_sum_profit / last_quarter_surplus
            quarter_profit_margin = "%.2f%%" % (quarter_profit_margin * 100)
            sheet.write_merge(begin_row_index_quarter, end_row_index_quarter,
                              19, 19, quarter_profit_margin, style_def)
                              
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
            sheet.write_merge(begin_row_index_year, end_row_index_year,
                              20, 20, year_profit_margin, style_def)

        # 开始记录本年年度利润率
        begin_row_index_year = row_index
        year_sum_profit = net_profit

        # 本本年净值结余
        # 第一年时
        if last_trade_year == "":
            last_year_surplus = initial_surplus
        # 不是第一年时
        else:
            c.execute(
                "select surplus from history_list where ID = {}".format(ID-1))
            last_year_surplus = c.fetchone()[0]
    else:
        year_sum_profit += net_profit
        if ID == len(history_list):
            end_row_index_year = row_index
            year_profit_margin = year_sum_profit / last_year_surplus
            year_profit_margin = "%.2f%%" % (year_profit_margin * 100)
            sheet.write_merge(begin_row_index_year, end_row_index_year,
                              20, 20, year_profit_margin, style_def)

    last_trade_year = trade_year

xl.save("trading_history.xls")
