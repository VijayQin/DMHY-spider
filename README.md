# 关于DMHY-spider

`**ACGL**` | `DMHY` `spider`

**DMHY-spider**目的在于爬取动漫花园网站，并将字幕组上传的每一条动画所对应的网页和种子分文别类保存到本地文件系统和数据库中。目前数据库使用的是SQLite3，但是今天使用发现数据库大小增长比较快，后续可能更换为PostgresSQL。最终目的是要能够建立一系列规则，智能识别每一条记录是否为我们在追的番剧(根据剧名，但能识别简体繁体日语罗马音和剧名的缩写甚至错写)。功能概述：
 
- [x] **爬取[动漫花园][1]网站** ：为了降低对服务器的压力，将访问间隔设为了10s；
- [x] **存储到文件系统和数据库** ：将每一条记录的网页和种子保存到文件系统，并将标题文件大小类型等记录到数据库[SQLite3][2]，以便后续挖掘；
- [ ] **智能识别番剧** ：目前还没实现，也没想好要做成什么样，有想法的可以联系我。

-------------------

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->

- [关于DMHY-spider](#关于dmhy-spider)
    - [用法](#用法)
    - [模块调用](#模块调用)
    - [参数](#参数)

<!-- markdown-toc end -->

## 用法

> 我只是想爬一下网页而已，请不要查我家水表。    —— Vijay

```
$ python DMHY_DataBase.py
```
我觉得我代码运行写的提示已经够多了。。。 
```
请输入模式:1、更新昨天 2、更新指定日期(格式:2016-08-23)"
           3、更新时间段(格式:[2016-08-22,2016-08-23])"
           4、自动更新模式 5、更新固定页数'
```
对，就是这么用的。

1更新昨天

2更新指定日期

3更新一个时间段(注意输入格式，第一个和最后一个字符随意，我输入[]是为了提醒你们左右都是闭区间)

4自动更新模式是更新到数据库当前最后一条记录，如果数据库为空，那么会一直读取到1970年，也就是把网站全爬下来。不过因为到后面会因为读不到页面所以抛出异常，所以不要第一次运行就使用，否则。。。你会爬几个月。。。然后一个异常导致你数据库一条都没有commit进去，嗯。

5就更新前几页。

除了**第一次运行不要使用4**以外没有别的提醒。建议是使用1和3。每天只更新昨天的比较好。嗯？问我为什么是昨天？因为今天还没过完啊。

**第一次运行不要使用4**
**第一次运行不要使用4**
**第一次运行不要使用4**

重要的事情说三遍。

## 模块调用
``` python
import DMHY_DataBase.py
url = r"https://share.dmhy.org/topics/list/page/"
domain = r"https://share.dmhy.org"

path = os.getcwd()

sqlite_db = os.path.join(path, 'DMHY.db')
time_delay = 0
	
warehouse = os.path.join(path, 'Warehouse')

DataBase = DMHY_DataBase(mode, attr, url, domain, sqlite_db, time_delay, warehouse)

DataBase.start_requests()
```
自己写一个模块来调用也可以。

## 参数
mode就是前面的1,2,3,4,5.
attr就是2,3,5里面输入的时间段和页码。1,4的时候attr随便。
url和domain是DMHY的域名。
sqlite_db是数据库存放的路径。
time_delay是访问间隔。
warehouse是网页和种子存放的路径


  [1]: http://share.dmhy.org
  [2]: https://sqlite.org/
