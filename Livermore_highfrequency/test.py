import datetime
import schedule
import time
def func():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func  time :',ts)
def func2():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func2 time：',ts)
def tasklist():
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    schedule.every(1).seconds.do(func)
    #创建一个按2秒间隔执行任务
    schedule.every(2).seconds.do(func2)
    #执行10S
    while True:
        schedule.run_pending()   
tasklist()
