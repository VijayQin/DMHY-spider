# 关于DMHY-spider

**`ACGL`** | `DMHY` `spider`

**DMHY-spider**目的在于爬取动漫花园网站，并将字幕组上传的每一条动画所对应的网页和种子分文别类保存到本地文件系统和数据库中。目前数据库使用的是SQLite3，但是今天使用发现数据库大小增长比较快，后续可能更换为PostgresSQL。最终目的是要能够建立一系列规则，智能识别每一条记录是否为我们在追的番剧(根据剧名，但能识别简体繁体日语罗马音和剧名的缩写甚至错写)。功能概述：
 
- [x] **爬取[动漫花园][1]网站** ：为了降低对服务器的压力，将访问间隔设为了10s；
- [x] **存储到文件系统和数据库** ：将每一条记录的网页和种子保存到文件系统，并将标题文件大小类型等记录到数据库[SQLite3][2]，以便后续挖掘；
- [ ] **智能识别番剧** ：目前还没实现，也没想好要做成什么样，有想法的可以联系我。

-------------------

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->

- [关于DMHY-spider](#关于dmhy-spider)
    - [用法](#用法)
    - [数据库](#数据库)
    - [模块调用](#模块调用)
    - [参数](#参数)
    - [配置文件编写](#配置文件编写)

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

<kbd>1</kbd>更新昨天

<kbd>2</kbd>更新指定日期

<kbd>3</kbd>更新一个时间段(注意输入格式，第一个和最后一个字符随意，我输入[]是为了提醒你们左右都是闭区间)

<kbd>4</kbd>自动更新模式是更新到数据库当前最后一条记录，如果数据库为空，那么会一直读取到1970年，也就是把网站全爬下来。不过因为到后面会因为读不到页面所以抛出异常，所以不要第一次运行就使用，否则。。。你会爬几个月。。。然后一个异常导致你数据库一条都没有commit进去，嗯。

<kbd>5</kbd>就更新前几页。

除了**第一次运行不要使用<kbd>4</kbd>**以外没有别的提醒。建议是使用<kbd>1</kbd>和<kbd>3</kbd>。每天只更新昨天的比较好。嗯？问我为什么是昨天？因为今天还没过完啊。

**第一次运行不要使用4**

**第一次运行不要使用4**

**第一次运行不要使用4**

重要的事情说三遍。

## 数据库
``` python
create table if not exists DMHY_DataBase (
    id INTEGER PRIMARY KEY,
    date VARCHAR(20),
    type VARCHAR(10),
    title VARCHAR(255),
    link VARCHAR(255),
    magnet VARCHAR(255),
    size VARCHAR(10),
    uploader VARCHAR(30),
    HTML TEXT,
    attach VARCHAR(255),
    finish BOOLEAN
)
```
id是数据库自增的主键。

date是该条记录字幕组的上传日期。

type, title, link, magnet, size, uploader分别对应资源的类型, 标题, 网页链接, 资源磁链, 资源总大小和上传者。

**其中link字段为2.0.0及以后版本新增, 会导致1.X版本的数据库不可用，请1.X版本使用者删除数据库重建。**

HTML是资源对应网页的数据库备份, 虽然会占比较大的空间, 但出于后续挖掘现在没有的字段数据的考量, 还是决定先保存着。

attach是资源网页和种子在本地磁盘存储的位置。如果由于设置auto_download = False, 使得网页和种子没有下载, 那么该字段为空''。

finish是资源是否已经提醒我更新，对应第三项功能，目前尚未完成所以暂时全为False。

## 模块调用
``` python
import DMHY_DataBase.py
# url = r"https://share.dmhy.org/topics/list/page/"
# domain = r"https://share.dmhy.org"

# path = os.getcwd()

# # sqlite_db = r"D:\Data\Desktop\Workspace\test\DMHY\DMHY.db"
# sqlite_db = os.path.join(path, 'DMHY.db')
# time_delay = 0

# # warehouse = r'D:\Data\Desktop\Workspace\test\DMHY\Warehouse'
# warehouse = os.path.join(path, 'Warehouse')

# DataBase = DMHY_DataBase(mode, attr, url, domain, sqlite_db, time_delay, warehouse, auto_download)
DataBase = DMHY_DataBase(mode, attr)
DataBase.start_requests()
```
自己写一个模块来调用也可以。
``` python
DMHY_DataBase(mode, attr, url=None, domain=None, 
        sqlite_db=None, time_delay=None, warehouse=None,
        auto_download=None):
```
模式mode，和参数attr是必须要输入的。其余的参数都有默认值。

其中url和domain默认是DMHY现在的域名, time_delay默认是0。以上三项可在同目录底下的配置文件DMHY_Configuration.cfg中设置。

其余的数据库路径sqlite_db，和种子仓库路径warehouse，如果不设，默认在当前目录底下。设了就按设的来。

auto_download设置的是检查网页的时候除了插进数据库，是否需要将网页和种子保存到本地。Boolean类型。默认为真，即要保存到本地。

## 参数
mode就是前面的1,2,3,4,5.

attr就是2,3,5里面输入的时间段和页码。1,4的时候attr随便。

url和domain是DMHY的域名。

sqlite_db是数据库存放的路径。

time_delay是访问间隔。

warehouse是网页和种子存放的路径。

auto_download是要不要自动下载网页和种子到本地。

## 配置文件编写
空行随便空，井号#开头是注释。

格式是key = value。不读取空格，所以key和value(尤其是路径)，不要包含空格。

**路径不要包含空格**

**路径不要包含空格**

**路径不要包含空格**

**其中url和domain两项为必配项。调用的参数和配置文件两处中至少有一处有设置，其中调用时参数的优先级高于配置文件中的设置。**

time_delay是访问间隔。

auto_download是要不要自动下载网页和种子到本地。

https_security_certificate_check为False表示不检查https的安全性。

  [1]: http://share.dmhy.org
  [2]: https://sqlite.org/
