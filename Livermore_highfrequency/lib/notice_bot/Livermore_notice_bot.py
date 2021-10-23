# -*- encoding: utf-8 -*-
'''
@File    :   Livermore_notice_bot.py
@Time    :   2021/10/22 10:43:56
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import telegram


# 创建telegram_bot类

class telegram_bot:
    def __init__(self, bot_taken):

        # 根据bot_taken替换机器人
        self.bot = telegram.Bot(token=bot_taken)
        print("bot已连接")


if __name__ == "__main__":
    Livermore_notice_bot = telegram.Bot(
        "2052847212:AAGBBhtGr01kvru6iwBB3V8nmcdPpbhTh9c")
    Livermore_notice_bot.send_message(chat_id="@1748558438", text="1")