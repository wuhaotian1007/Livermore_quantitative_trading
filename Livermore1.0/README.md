# TradingTools

Trading tools to avoid human errors in recording data through Jessie Livermore's methodology based on https://github.com/ranaroussi/yfinance

# 股票

## 需求背景

​	简化价格记录及趋势判断流程，并增加策略收益预期测试，减少因为人为因素导致的记录出错所引发的交易损失。并且通过收益预期测试，持续优化策略以提升总体收益率。

## 预期效果

### 源数据更新程序

update_source_data.py，通过https://github.com/ranaroussi/yfinance或其它项目，读取stock_list表中的股票列表名称以获取对应的股票日收盘价格。并按照Livermore操盘法则对股价进行更新。默认是获取最近一个交易日的价格入库后更新，如增加时间周期参数则为获取该时间范围内的历史数据并入库后更新；使用示例如下：

- ./update_source_data.py，更新stock_list里的所有股票的最后一个交易日的收盘价格并入库+更新属性；
- ./update_source_data.py 6mo，更新stock_list里所有股票过去6个月的收盘价格并入库+更新属性；
- ./update_source_data.py MSFT，更新MSFT最后一个加一日的收盘价并入库+更新属性；
- ./update_source_data.py MSFT 6mo，更新MSFT过去6个月的收盘价格并入库+更新属性；

#### stock_list表结构

   - 表名：stock_list
   - 字段：
     - ID：自增ID
     - 股票名称：股票代号，如MSFT为微软
     - 3点步进：该股票用作衡量趋势变化的3点所代表的实际价格，默认为3usd

#### 入库后表结构及字典

   - 表名：股票名称+默认记录所在栏
   - 字段：
     - ID：自增ID
     - 日期：交易日，格式为2021-02-24
     - 收盘价：该股票在对应交易日的收盘价，精确到小数点后3位，四舍五入
     - “是否记录”：unsigned int，1为需要记录，0为不需要记录；第一条记录为1，其余默认为0
     - “记录所在栏”：以表名来命名默认值，增加新股票时都新建全量6张不同初始状态的表
       - 不记录：0
       - 次级回升栏:1
       - 自然回升栏:2
       - 上升趋势栏:3
       - 下降趋势栏:4
       - 自然回撤栏:5
       - 次级回撤栏:6
     - “是否关键点”：unsigned int，1为是，0为否。默认值为0，需要通过更新逻辑来更新

     

### 生成报表程序

gen_livermore_table.py，根据Livermore操盘法则，从数据库中读取对应记录，生成可读报表，并给出操作建议。格式为xlsx。其中关键点对应的双下划线改为单下划线，其它格式不变。其中主报表格式参照word版本行情记录即可（对于股票群需要增加组合价格）。其中操作建议格式如下：

- 最新价格：本组合本日最新价格为：A、B、C、sum（ABC）
- 趋势判断：当前股票A、B、C及其组合价格均处于上升趋势结束/小幅波动
- 操作指引：
  - 平掉所有做多单
  - 开始做空

关于组合价格的与单只股票的信号，等数据跑出来以后，需要写模拟交易程序在做空与做多方向下验证以下场景：

- 在组合价格趋势出现交易信号时：

  1. 所有股票都出现与组合价格一样的趋势：

     - 所有股票与组合价格都不在同样的记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系
     - 部分股票与组合价格在相同的记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系
     - 所有股票和组合价格都在相同记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系

  2. 部分股票出现与组合价格一样的趋势：

     - 所有股票与组合价格都不在同样的记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系

     - 部分股票与组合价格在相同的记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系

     - 所有股票和组合价格都在相同记录栏：
       - 测试交易的结果为正或者负
       - 如交易结果为正，观察股票逆转幅度、组合价格逆转幅度与利润率的关系

  3. 所有股票均与组合价格不一样的趋势：要根据实际股票情况来决定是否存在这种可能性

     

### 收益预测程序

可能需要加入日内最低价、最高价、开盘价数据，待细化



### 自动选择程序

根据每个板块交易量+交易额 Top N的股票，计算Cn2~Cnn的组合下，在过去一段无重大流动性变化的事件内（如利率变化、资产负债表变化等）的收益预测



## 实现细节

### update_source_data.py

1. 不带任何参数的情况下，使用当前日期作为获取源数据的日期，使用stock_list中的所有股票作为股票参数。并将最新数据插入后，按照数据标记逻辑进行属性更新。
2. 当只传入时间周期参数时，将stock_list中的所有股票均作为股票参数（无表则建），时间周期作为时间周期来更新数据源并插入表。插入完成后从第二行开始到最后新一行，按照数据标记逻辑进行属性更新；
3. 当只传入股票参数时，使用当前日期作为获取源数据的日期，传入的股票作为股票参数。并将最新数据插入后，按照数据标记逻辑进行属性更新。
4. 当同时传入时间周期参数和股票参数时，使用时间周期作为时间周期，使用传入的股票作为股票参数。将数据全部插入后，按照标记逻辑进行属性更新。

#### 数据更新逻辑：

##### 当上一条记录所在栏为上升趋势栏（3）

###### 价格上升

- 需要记录
	- 在上升趋势栏记录：如本条记录的收盘价大于上一条的收盘价，则本条的“是否记录”值为1，“是否关键点”为0，“记录所在栏”值为3

###### 价格下降					

- 不需要记录：如本条记录的收盘价小于上一条的收盘价，但差值不超过6点，则本条的“是否记录”值为0，“是否关键点为0”，“记录所在栏”值为0

- 需要记录
	- 在自然回撤栏记录
	  - 更新本条记录到自然回撤栏记录：如本条记录的收盘价小于上一条的收盘价，并且差值超过6点，则本条的“是否记录”值为1，“是否关键点为”0；“记录所在栏”值为5；
	    - 由于从上升趋势栏切换至自然回撤栏，所以对于自然回撤栏来说这算是新的“第一条”记录，所以需要：
	    	- 更新最新一条上升趋势栏记录为关键点：将最新一条“记录所在栏”值为3（上升趋势栏）的记录的“是否为关键点”update为1
	    	- 更新最新一条自然回升栏记录为关键点：将最新一条“记录所在栏”值为2（自然回升栏）的记录的“是否为关键点”update为1
	    - 在下降趋势栏记录：
	      - 如果该记录小于最新一条下降趋势栏的关键点（最新一条“所在记录栏”为4+“是否为关键点”为1的记录），则本条的“是否记录”值为1，“是否关键点”为0，“记录所在栏”值为4。（由于转换到自然回撤栏的流程已经将自然回升栏设置为关键点，所以无需再重复设置）
	
	      - 如果该记录小于最新一条自然回撤栏关键点以下3点或以上（最新一条“所在记录栏”为5+“是否为关键点”为1的记录），则本条的“是否记录”值为1，“是否关键点”为0，“记录所在栏”值为4。（由于转换到自然回撤栏的流程已经将自然回升栏设置为关键点，所以无需再重复设置）
###### 价格不变：
- 不需要记录：如本条记录的收盘价等于上一条的收盘价，但差值不超过6点，则本条的“是否记录”值为0，“是否关键点为0”，“记录所在栏”值为0



##### 当上一条”是否记录“为1的记录的”记录所在栏“为自然回撤栏（5）
###### 价格上升

- 需要记录：
  - 在次级回升栏记录：如果本条记录与上一条记录的差值大于或等于6点，但并没有大于自然回升栏内的最新记录（”记录所在栏“值为2的最新一条记录），则本条记录的”是否记录“值为1，”是否关键点“为0，”记录所在栏“值为1；
  - 在自然回升栏记录：
    - 如果
    - 在上升趋势栏记录：
- 不需要记录：如本条记录的收盘价大于上一条记录的收盘价，但差值不超过6点，则本条记录的“是否记录”值为0，“是否关键点”为0，“记录所在栏”值为0

###### 价格下降

- 需要记录：
  - 在自然回撤栏记录：如果本条记录的收盘价小于上一条记录的收盘价，但未小于下降趋势栏的最新关键点（最新一条“记录所在栏”值为4+“是否关键点”为1的记录）+未小于自然回撤栏最新关键点（最新一条“记录所在栏”为5+“是否关键点”为1的记录）以下3点，则本条记录的“是否记录”为1，“是否关键点”为0，“记录所在栏”为5
  - 在下降趋势栏记录：
    - 低于下降趋势栏最新关键点或低于自然回撤栏最新关键点以下3点：如果本条记录小于下降趋势栏最新关键点（最新一条“记录所在栏”值为4+“是否为关键点”为1的记录）或本条记录小于自然回撤栏最新关键点（最新一条“记录所在栏”为5+“是否关键点”为1的记录）以下3点，则：
      - 将本条记录记录在下降趋势栏：将本条记录的“是否记录”置为1，“是否关键点”置为0，“记录所在栏”置为4；
      - 由于从自然回撤栏切换到下降趋势栏记录，所以对于下降趋势栏来说这一条记录相当于新的“第一条”记录，所以需要
  - 在次级回升栏记录
  - 在自然回升栏记录
  - 在上升趋势栏记录

###### 价格不变

- 不需要记录：如本条记录的收盘价等于上一条记录的收盘价，但差值不超过6点，则本条记录的“是否记录”值为0，“是否关键点”为0，“记录所在栏”值为0

  


##### 当上一条”是否记录“为1的记录的”记录所在栏“为下降趋势栏（4）

- 如本条记录的收盘价小于上一条的收盘价，并且差值超过6点，则本条的“是否记录”值为1，“是否关键点为”0；“记录所在栏”值为5，并且将上一条记录的“是否关键点” update为1；并更新最新一条“记录所在栏”为“自然回升栏”（2），并且“是否记录”为1的行的“是否关键点”为1；
- 如本条记录的收盘价小于上一条的收盘价，则本条的“是否记录”值为1，“是否关键点”为0，“记录所在栏”为4；
- 如本条记录的收盘价大于上一条的收盘价，但差值不超过6点，则本条的“是否记录”值为0，“是否关键点”为0，“记录所在栏”值为0；
- 如本条记录的收盘价大于上一条的收盘价，并且差值超过6点，则本条的“是否记录”值为1，“是否关键点”为0，“记录所在栏”值为2；并且将上一条记录的“是否关键点”update为1，

##### 当上一条”是否记录“为1的记录的”记录所在栏“为自然回升栏（2）

##### 当上一条”是否记录“为1的记录的”记录所在栏“为次级回升栏（1）

##### 当上一条”是否记录“为1的记录的”记录所在栏“为次级回撤栏（6）

### gen_livermore_table.py

### profit_estimation.py






# 外汇

- [ ] 获取一段时间内的指定交易对与DXY的数据，按照设定的初始参数，生成Livermore行情表格，并给出信号提示

- [ ] 参数列表：
  - [ ] 交易对代号，需要支持多个
  - [ ] 开始日期
  - [ ] 3点步进
  - [ ] 初始记录位置（可选，可以考虑4个主要栏都各输出一份，自然回升/自然回撤/上升趋势/下降趋势）
- [ ] 最终效果：
  - [ ] 输出表格形式Livermore行情记录表格，自动标注关键点
  - [ ] 每次运行时将**开始日期-上一个交易日**缺失的数据进行补充，保存成tab分隔纯文本的csv文件
  - [ ] 根据策略给出信号建议和详细理由
  - [ ] 生成按日期为文件名和latest的pdf+csv
