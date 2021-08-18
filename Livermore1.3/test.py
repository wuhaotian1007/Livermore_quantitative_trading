import os
import configparser

# 读取全局设置
conf = configparser.ConfigParser()
def readConf():
    '''读取配置文件'''
    conf.read('global.conf')  # 文件路径
    print(conf)
    onedrive_path = conf.get("global", "Onedrive_path")  # 获取指定section 的option值
    print(onedrive_path)


readConf()
