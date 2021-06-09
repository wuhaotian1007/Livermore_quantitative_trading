# -*- encoding: utf-8 -*-
'''
@File    :   loop.py
@Time    :   2021/05/07 19:47:50
@Author  :   Wuhaotian 
@Version :   1.0
@Contact :   wuhaotian1007@gmail.com
'''

# here put the import lib
import os,threading,time,sys

curTime=time.strftime("%Y-%M-%D",time.localtime())#记录当前时间
execF=False
ncount=0
def execTask():
  #具体任务执行内容
  os.system("python from_MT5.py")
def timerTask():
  global execF
  global curTime
  global ncount
  if execF is False:
    execTask()#判断任务是否执行过，没有执行就执行
  ncount = ncount+1
  timer = threading.Timer(1800,timerTask)
  timer.start()
  print("定时器执行%d次"%(ncount))
if __name__=="__main__":
  timer = threading.Timer(1800,timerTask)
  timer.start()