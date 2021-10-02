import time
t1 = 1626714120
t2 = 1626710280

t1_str = time.strftime("%Y-%m-%d", time.localtime(t1))
t2_str = time.strftime("%Y-%m-%d", time.localtime(t2))

print(t1_str+t2_str)