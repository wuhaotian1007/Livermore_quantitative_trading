# -*- encoding: utf-8 -*-
'''
@File    :   launcher.py
@Time    :   2021/05/07 16:37:57
@Author  :   Wuhaotian 
@Version :   1.2
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import os
import sys

# 数据库路径
db_Path = "C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\database"

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
del_file(db_Path)

# 运行文件


def launcher(default_trend):
    # 运行数据拉取部分
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\data_pull_storage\\from_yfinance.py")
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\data_pull_storage\\from_MT5.py")

    # 运行数据入库部分
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\standardization_storage\\XAUUSD_std.py")
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\standardization_storage\\DXY_std.py")
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\standardization_storage\\TNX_std.py")
    os.system(
        "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\standardization_storage\\comb.py")

    # 运行趋势测量部分与可视化部分
    if default_trend == "up":
        # 趋势测量部分
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_uptrend.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_uptrend2.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_uptrend3.py")
        # 可视化部分
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\uptrend_vis.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\uptrend_vis2.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\uptrend_vis3.py")
    if default_trend == "down":
        # 趋势测量部分
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_downtrend.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_downtrend_2.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\est_trend\\default_downtrend_3.py")
        # 可视化部分
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\downtrend_vis.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\downtrend_vis_2.py")
        os.system(
            "python C:\\Users\\sgnjim\\Desktop\\for_python\\Livermore1.2\\lib\\visualization\\downtrend_vis_3.py")


launcher("down")
