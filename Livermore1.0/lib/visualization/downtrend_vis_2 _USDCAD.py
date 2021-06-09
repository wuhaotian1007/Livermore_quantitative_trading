# -*- encoding: utf-8 -*-
'''
@File    :   visualization.py
@Time    :   2021/04/24 14:25:17
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   460205923@qq.com
'''

# here put the import lib
import sqlite3
import xlwt
import time

# 创建一个工作簿
xl = xlwt.Workbook(encoding='utf-8')
# 创建一个sheet对象
sheet = xl.add_sheet('Livermore行情记录')

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

# 创建蓝色字体
font_blue = xlwt.Font()
font_blue.colour_index = 40

# 创建红色字体
font_red = xlwt.Font()
font_red.colour_index = 10

# 创建白色字体
font_white = xlwt.Font()
font_white.colour_index = 1

# 创建粉色背景
pattern_pink = xlwt.Pattern()
pattern_pink.pattern = xlwt.Pattern.SOLID_PATTERN
pattern_pink.pattern_fore_colour = 10

# 创建灰色背景
pattern_grey = xlwt.Pattern()
pattern_grey.pattern = xlwt.Pattern.SOLID_PATTERN
pattern_grey.pattern_fore_colour = 0

# 画excel框架
# 初始化样式
style_big = xlwt.XFStyle()
style_big.font = font_title
style_big.alignment = alignment
style_big.borders = borders

style_bold = xlwt.XFStyle()
style_bold.font = font_bold
style_bold.alignment = alignment
style_bold.borders = borders

style_blue = xlwt.XFStyle()
style_blue.font = font_blue
style_blue.alignment = alignment
style_blue.borders = borders

style_red = xlwt.XFStyle()
style_red.font = font_red
style_red.alignment = alignment
style_red.borders = borders

style_white = xlwt.XFStyle()
style_white.font = font_white
style_white.alignment = alignment
style_white.borders = borders

style_def = xlwt.XFStyle()
style_def.alignment = alignment
style_def.borders = borders

sheet.write(0, 0, "日期", style_big)
sheet.col(0).width = 4000
sheet.write_merge(0, 0, 1, 7, 'USDCAD 0.0035=3点', style_big)
sheet.write_merge(0, 0, 8, 13, 'DXY 0.3=3点', style_big)
sheet.write_merge(0, 0, 14, 19, 'comb 6=3点', style_big)
sheet.write(1, 1, 'VOLUME', style_def)
sheet.write(1, 2, '次级回升', style_blue)
sheet.write(1, 8, '次级回升', style_blue)
sheet.write(1, 14, '次级回升', style_blue)
sheet.write(1, 3, '自然回升', style_blue)
sheet.write(1, 9, '自然回升', style_blue)
sheet.write(1, 15, '自然回升', style_blue)
sheet.write(1, 4, '上升趋势', style_def)
sheet.write(1, 10, '上升趋势', style_def)
sheet.write(1, 16, '上升趋势', style_def)
sheet.write(1, 5, '下降趋势', style_red)
sheet.write(1, 11, '下降趋势', style_red)
sheet.write(1, 17, '下降趋势', style_red)
sheet.write(1, 6, '自然回撤', style_blue)
sheet.write(1, 12, '自然回撤', style_blue)
sheet.write(1, 18, '自然回撤', style_blue)
sheet.write(1, 7, '次级回撤', style_blue)
sheet.write(1, 13, '次级回撤', style_blue)
sheet.write(1, 19, '次级回撤', style_blue)


# 连接数据库data.db和指针
conn = sqlite3.connect(
    'C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\database\\USDCAD_DXY.db')
c = conn.cursor()

# 读取所有数据获得列表
c.execute("select * from STOCK_list")
data_list = c.fetchall()

# 针对列表元素获得写入excek所需特征
for data in data_list:
    ID = data[0]
    NAME = data[1]
    DATE = data[2]
    PRICE = data[3]
    VOLUME = data[4]
    REC = data[5]
    COL = data[6]
    KEY = data[7]

    # price所在行列
    row = (ID-1)//3 + 2
    column = COL + 6 * ((ID + 2) % 3) + 1

    # 补齐时间
    if ID % 3 == 1:
        sheet.write(ID//3 + 2, 0, DATE, style_bold)
    # 如果被记录
    if REC == 1:
        # 如果是自然回升回撤或次级回升回撤
        if COL == 1 or COL == 2 or COL == 5 or COL == 6:
            # 如果是自然回撤关键点
            if KEY == 1 and COL == 5:
                style_blue_pink = xlwt.XFStyle()
                style_blue_pink.font = font_blue
                style_blue_pink.pattern = pattern_pink
                style_blue_pink.alignment = alignment
                style_blue_pink.borders = borders
                sheet.write(row, column, PRICE, style_blue_pink)
            elif KEY == 1 and COL == 2:
                style_blue_grey = xlwt.XFStyle()
                style_blue_grey.font = font_blue
                style_blue_grey.pattern = pattern_grey
                style_blue_grey.alignment = alignment
                style_blue_grey.borders = borders
                sheet.write(row, column, PRICE, style_blue_grey)
            else:
                sheet.write(row, column, PRICE, style_blue)
        # 如果是上升趋势和下降趋势
        else:
            if KEY == 1 and COL == 3:
                style_pink = xlwt.XFStyle()
                style_pink.pattern = pattern_pink
                style_pink.alignment = alignment
                style_pink.borders = borders
                sheet.write(row, column, PRICE, style_pink)
            elif KEY == 0 and COL == 3:
                sheet.write(row, column, PRICE, style_def)
            elif KEY == 1 and COL == 4:
                style_red_grey = xlwt.XFStyle()
                style_red_grey.font = font_red
                style_red_grey.pattern = pattern_grey
                style_red_grey.alignment = alignment
                style_red_grey.borders = borders
                sheet.write(row, column, PRICE, style_red_grey)
            elif KEY == 0 and COL == 4:
                sheet.write(row, column, PRICE, style_red)

    # 如果未被记录用白色字体记下
    elif REC == 0:
        sheet.write(row, column, PRICE, style_white)

    # 加上USDCAD的volume
    if NAME == "USDCAD":
        sheet.write(row, 1, VOLUME, style_def)


# 保存文件
xl.save('C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.0\\report\\USDCAD-DXY-{0}-downtrend.xls'.format(
    time.strftime("%Y-%m-%d")))
xl.save('C:\\Users\\sgnjim\\OneDrive\\work\\Livermore_report\\archive\\USDCAD-DXY-{0}-downtrend.xls'.format(
    time.strftime("%Y-%m-%d")))
xl.save('C:\\Users\\sgnjim\\OneDrive\\work\\Livermore_report\\latest_report\\USDCAD-DXY-latest-downtrend.xls')
