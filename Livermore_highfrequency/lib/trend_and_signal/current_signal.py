# -*- encoding: utf-8 -*-
'''
@File    :   current_signal.py
@Time    :   2021/10/17 16:17:45
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import sqlite3
import telegram


class current_signal:
    def __init__(self, hf_db_path, D1_db_path, XAUUSD_signal_txt_path, comb_signal_txt_path, timezone, XAUUSD_coef, comb_coef, match_mode, process_length, bot_token, *receiver_id):
        # hf_db_path:高频数据库路径，D1_db_path日线数据库路径，XAUUSD_coef:XAUUSD3点价格，comb_coef：comb3点价格，process_length:倒数处理长度，all为首次入库, timezone为时区，matchmode为匹配模式, process_length为处理长度， bot_token为tg机器人token，receiver_id为接收人id

        # 建立日线数据库和高频数据库连接
        conn_hf_db = sqlite3.connect(hf_db_path)
        conn_D1_db = sqlite3.connect(D1_db_path)

        cur_hf_db = conn_hf_db.cursor()
        cur_D1_db = conn_D1_db.cursor()

        XAUUSD_signal_file = open(XAUUSD_signal_txt_path, "w+")
        comb_signal_file = open(comb_signal_txt_path, "w+")

        # 建立tg机器人连接
        def connect_tg_bot():
            global tg_bot

            tg_bot = telegram.Bot(token=bot_token)
            print("tg机器人{0}已启用".format(bot_token))

        connect_tg_bot()

        # tg机器人发送消息函数
        def bot_send_notification(text):
            # 遍历接受人id数组发送信息
            for id in receiver_id:
                tg_bot.send_message(chat_id=id, text=text)

        # XAUUSD遍历与信号
        def iter_XAUUSD():
            # 遍历高频数据db
            # 遍历XAUUSD
            cur_hf_db.execute("select * from XAUUSD_list")
            XAUUSD_list = cur_hf_db.fetchall()

            # 判断处理长度，根据处理长度截取数据范围
            if process_length == "all":
                print("首次处理实时信号")
            else:
                XAUUSD_list = XAUUSD_list[-process_length:]

            last_date = ""
            last_up_key_spot = 0
            last_down_key_spot = 0

            # today_n_times 为当天某一信号出现次数
            today_1_times = 0
            today_2_times = 0
            today_3_times = 0
            today_4_times = 0
            today_7u_times = 0
            today_7d_times = 0

            # 记录为当天最高价或最低价格
            today_max_price = 0
            today_min_price = 0

            # 开始遍历XAUUSD
            for XAUUSD_info in XAUUSD_list:
                total_date = XAUUSD_info[0]
                date = XAUUSD_info[0][:10]
                close = XAUUSD_info[2]
                ts = XAUUSD_info[3]
                signal = ""
                status = ""

                # 判断当日最高价与最低价，如果是新的一天将会在后面覆盖
                today_max_price = max(close, today_max_price)
                today_min_price = min(close, today_min_price)

                if date != last_date:
                    # 如果是新的一天，查询XAUUSD日线关键点信息
                    cur_D1_db.execute(
                        "select PRICE from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and TIMESTICKER <= {2} and COLUMN in {3} ".format("XAUUSD", 1, ts, (1, 2, 3)))
                    last_up_key_spot = cur_D1_db.fetchall()[-1][0]

                    cur_D1_db.execute(
                        "select PRICE from STOCK_LIST where NAME = '{0}' and KEYSPOT = {1} and TIMESTICKER <= {2} and COLUMN in {3} ".format("XAUUSD", 1, ts, (4, 5, 6)))
                    last_down_key_spot = cur_D1_db.fetchall()[-1][0]

                    # 如果是新的一天重新开始记录最高价和最低价
                    today_max_price = close
                    today_min_price = close

                    # today_n_times 为当天某一信号出现次数
                    today_1_times = 0
                    today_2_times = 0
                    today_3_times = 0
                    today_4_times = 0
                    today_7u_times = 0
                    today_7d_times = 0

                # 日期替换
                last_date = date

                # 查询当前记录栏（前一日线的记录栏）
                cur_D1_db.execute(
                    "select column from STOCK_LIST where name == '{0}' and timesticker <= {1}".format("XAUUSD", ts-86400))
                cur_column = cur_D1_db.fetchall()[-1][0]

                # 根据当前记录栏判断趋势信号
                # 当前趋势栏在上升趋势栏时，与上升趋势栏中的最新关键点比较，向下3点为上升趋势结束（记录为1），向上3点为上升趋势恢复（记录为2），若日内创新高但最新的价格比新高低6点则为日内上升趋势危险信号（记录为7u)
                if cur_column in (1, 2, 3):
                    if close <= last_up_key_spot - 3*XAUUSD_coef:
                        signal = "上升趋势结束"
                        today_1_times += 1

                        # 价格在下降时，判断当前价格是否低于本日最低价格，并记录statu状态
                        if close < today_min_price:
                            status = "status:lower"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_1_times) + status

                    elif close >= last_up_key_spot + 3*XAUUSD_coef:
                        signal = "上升趋势恢复"
                        today_2_times += 1

                        # 价格在上升时，判断当前价格与今日最高价格大小并记录status
                        if close > today_max_price:
                            status = "status:higher"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_2_times) + status

                    if close <= today_max_price - 6*XAUUSD_coef:
                        signal = "上升日内危险"
                        today_7u_times += 1
                        # 其余信号出现次数归0
                        today_1_times = 0
                        today_2_times = 0
                        today_3_times = 0
                        today_4_times = 0

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_7u_times) + status

                # 当前趋势栏在下降趋势栏时，与下降趋势栏中的最新关键点比较，向上3点为下降趋势结束（记录为3），向下3点为下降趋势恢复（记录为4），若日内创新低但最新的价格比新低高6点则为日内下降趋势危险信号（记录为7d）
                elif cur_column in (4, 5, 6):
                    if close >= last_down_key_spot + 3*XAUUSD_coef:
                        signal = "下降趋势结束"
                        today_3_times += 1

                        # 价格在上升时，判断当前价格与今日最高价格大小并记录status
                        if close > today_max_price:
                            status = "status:higher"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_3_times) + status

                        # 使用tg机器人发送信号

                    elif close <= last_down_key_spot - 3*XAUUSD_coef:
                        signal = "下降趋势恢复"
                        today_4_times += 1

                        # 价格在下降时，判断当前价格是否低于本日最低价格，并记录statu状态
                        if close < today_min_price:
                            status = "status:lower"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_4_times) + status

                    if close >= today_min_price + 6*XAUUSD_coef:
                        signal = "下降日内危险"
                        today_7d_times += 1
                        # 其余信号出现次数归0
                        today_1_times = 0
                        today_2_times = 0
                        today_3_times = 0
                        today_4_times = 0

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tXAUUSD价格：" + \
                            str(close)+"\tXAUUSD存在趋势信号：" + signal + \
                            "\t信号发生次数：" + str(today_7d_times) + status

                if signal == "":
                    signal_notification = "时区："+timezone + "\t" + \
                        total_date + "\tXAUUSD价格："+str(close)

                # 打印信号提示并使用tg机器人发送
                def notification_output():
                    print(signal_notification)
                    print(signal_notification, file=XAUUSD_signal_file)

                    # 当存在信号时用tg机器人发送信息
                    if signal != "":
                        signal_notification_tg = signal_notification.replace("\t","\n")
                        bot_send_notification(signal_notification_tg)

                notification_output()

        iter_XAUUSD()

        def iter_comb():
            # 遍历高频数据comb
            # 遍历comb
            if match_mode == "best_effort_match":
                cur_hf_db.execute("select * from comb_bem")
                comb_list = cur_hf_db.fetchall()
            elif match_mode == "strict_match":
                cur_hf_db.execute("select * from comb_sm")
                comb_list = cur_hf_db.fetchall()

            # 判断处理长度，根据处理长度截取数据范围
            if process_length == "all":
                print("首次处理实时信号")
            else:
                comb_list = comb_list[-process_length:]

            last_date = ""
            last_up_key_spot = 0
            last_down_key_spot = 0

            # today_n_times 为当天某一信号出现次数
            today_1_times = 0
            today_2_times = 0
            today_3_times = 0
            today_4_times = 0
            today_7u_times = 0
            today_7d_times = 0

            # 记录为当天最高价或最低价格
            today_max_price = 0
            today_min_price = 0

            # 开始遍历XAUUSD
            for comb_info in comb_list:
                total_date = comb_info[0]
                date = comb_info[0][:10]
                close = comb_info[2]
                ts = comb_info[3]
                signal = ""
                status = ""

                # 判断当日最高价与最低价，如果是新的一天将会在后面覆盖
                today_max_price = max(close, today_max_price)
                today_min_price = min(close, today_min_price)

                if date != last_date:
                    # 如果是新的一天，查询日线关键点信息
                    cur_D1_db.execute(
                        "select price from STOCK_LIST where name == '{0}' and keyspot == {1} and timesticker <= {2} and column in {3} ".format("comb", 1, ts, (1, 2, 3)))
                    last_up_key_spot = cur_D1_db.fetchall()[-1][0]

                    cur_D1_db.execute(
                        "select price from STOCK_LIST where name == '{0}' and keyspot == {1} and timesticker <= {2} and column in {3} ".format("comb", 1, ts, (4, 5, 6)))
                    last_down_key_spot = cur_D1_db.fetchall()[-1][0]

                    # 如果是新的一天重新开始记录最高价和最低价
                    today_max_price = close
                    today_min_price = close

                    # today_n_times 为当天某一信号出现次数
                    today_1_times = 0
                    today_2_times = 0
                    today_3_times = 0
                    today_4_times = 0
                    today_7u_times = 0
                    today_7d_times = 0

                # 日期替换
                last_date = date

                # 查询当前记录栏（前一日线的记录栏）
                cur_D1_db.execute(
                    "select column from STOCK_LIST where name == '{0}' and timesticker <= {1}".format("comb", ts-86400))
                cur_column = cur_D1_db.fetchall()[-1][0]

                # 根据当前记录栏判断趋势信号
                # 当前趋势栏在上升趋势栏时，与上升趋势栏中的最新关键点比较，向下3点为上升趋势结束（记录为1），向上3点为上升趋势恢复（记录为2），若日内创新高但最新的价格比新高低6点则为日内上升趋势危险信号（记录为7u)
                if cur_column in (1, 2, 3):
                    if close <= last_up_key_spot - 3*comb_coef:
                        signal = "上升趋势结束"
                        today_1_times += 1

                        # 价格在下降时，判断当前价格是否低于本日最低价格，并记录statu状态
                        if close < today_min_price:
                            status = "status:lower"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_1_times) + status

                    elif close >= last_up_key_spot + 3*comb_coef:
                        signal = "上升趋势恢复"
                        today_2_times += 1

                        # 价格在上升时，判断当前价格与今日最高价格大小并记录status
                        if close > today_max_price:
                            status = "status:higher"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_2_times) + status

                    if close <= today_max_price - 6*comb_coef:
                        signal = "上升日内危险"
                        today_7u_times += 1
                        # 其余信号出现次数归0
                        today_1_times = 0
                        today_2_times = 0
                        today_3_times = 0
                        today_4_times = 0

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_7u_times) + status

                # 当前趋势栏在下降趋势栏时，与下降趋势栏中的最新关键点比较，向上3点为下降趋势结束（记录为3），向下3点为下降趋势恢复（记录为4），若日内创新低但最新的价格比新低高6点则为日内下降趋势危险信号（记录为7d）
                elif cur_column in (4, 5, 6):
                    if close >= last_down_key_spot + 3*comb_coef:
                        signal = "下降趋势结束"
                        today_3_times += 1

                        # 价格在上升时，判断当前价格与今日最高价格大小并记录status
                        if close > today_max_price:
                            status = "status:higher"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_3_times) + status

                    elif close <= last_down_key_spot - 3*comb_coef:
                        signal = "下降趋势恢复"
                        today_4_times += 1

                        # 价格在下降时，判断当前价格是否低于本日最低价格，并记录statu状态
                        if close < today_min_price:
                            status = "status:lower"

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_4_times) + status

                    if close >= today_min_price + 6*comb_coef:
                        signal = "下降日内危险"
                        today_7d_times += 1
                        # 其余信号出现次数归0
                        today_1_times = 0
                        today_2_times = 0
                        today_3_times = 0
                        today_4_times = 0

                        signal_notification = "时区："+timezone + "\t" + total_date + "\tcomb价格：" + \
                            str(close)+"\tcomb:"+match_mode+"存在趋势信号：" + \
                            signal+"\t信号发生次数：" + str(today_7d_times) + status

                if signal == "":
                    signal_notification = "时区："+timezone + \
                        "\t" + total_date + "\tcomb价格："+str(close)

                # 打印信号提示并使用tg机器人发送
                def notification_output():
                    print(signal_notification)
                    print(signal_notification, file=XAUUSD_signal_file)

                    # 当存在信号时用tg机器人发送信息
                    if signal != "":
                        signal_notification_tg = signal_notification.replace("\t","\n")
                        bot_send_notification(signal_notification_tg)

                notification_output()

        iter_comb()

        XAUUSD_signal_file.close()
        comb_signal_file.close()


if __name__ == "__main__":
    current_signal(r"database/XAUUSD_M.db", r"database/XAUUSD_DXY_TNX_D1_bem_exchange.db", r"report/XAUUSD_exchange_bem.txt",
                   r"report/XAUUSD_DXY_TNX_comb_exchange_bem.txt", "exchange", 7/3, 9/3, "best_effort_match", "all", "2052847212:AAGBBhtGr01kvru6iwBB3V8nmcdPpbhTh9c", "422667436", "@Livermore_Notice")
    current_signal(r"database/XAUUSD_M.db", r"database/XAUUSD_DXY_TNX_D1_sm_est.db", r"report/XAUUSD_sm_est.txt",
                   r"report/XAUUSD_DXY_TNX_comb_sm_est.txt", "est", 7/3, 9/3, "strict_match", "all", "all", "2052847212:AAGBBhtGr01kvru6iwBB3V8nmcdPpbhTh9c", "422667436", "@Livermore_Notice")
