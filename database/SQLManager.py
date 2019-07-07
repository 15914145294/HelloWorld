# -*- coding: utf-8 -*-

"""
created on 2016-12-27
@author hechangshu1

updated on 2017-01-09

    1、解决中文不能查询的问题
    2、查询条件是字符串必须另外写引号的问题
    3、添加使用说明

updated on 2017-01-09

    1、解决merge的时候会发出警告的问题

update on 2017-12-25

    1、使用表的自动加载机制，免除了手动添加映射关系的麻烦
    2、增加了批量造数的方法insertMany和mergeMany
    3、更新使用说明文档

updata on 2018-01-30

    1、增加了一个模块下有多个数据库的兼容，如果有多个库需要在config添加多个配置
    2、如果只有一个库，原有方式不用改变，如果有多个库，需要在xxxTables文件中增加config_name
    3、如有多个库，使用的时候DatabaseOperation(模块名，库的配置名)
    4、同一个模块下面的config_name不能重复

update on 2018-03-20
    1、修改了query和update对数字的兼容，之前修改过，不知道为什么被覆盖了
    2、增加了oracle的兼容，如果要使用需要在配置中加上type，值可以是oracle和mysql，配置样例如下：
    "dataBase":{
         "host":"10.0.53.82",
         "user":"dorado",
         "passwd":"dorado",
         "port":1521,
         "db_name":"orcl",
         "type":"oracle"
    }

使用方法：

    1、针对模块添加对应的tables.py文件，如crtDsTables.py
    2、文件内容包含：每个表对应一个类，类data为数据库表的所有字段，如果需要
        insert或者merge操作，字段为必填，否则data可以为空{}
    (3、在文件末尾包含了一个字典，记录表和类的对应关系) -- 废弃
    update on 2017-12-25
    3、无需添加映射关系，但是需要在文件中定义数据库名字,database="xxx",字段名固定
    (4、在SQLManager中import（3）步中的字典) -- 废弃
    (5、在module_map中添加模块了（3）步中字典的对应关系) -- 废弃
    6、使用的时候先创建DatabaseOperation类的对象，传入参数为模块名字，如crt_ds,member
    7、最后调用insert,merge等方法进行数据库操作

方法说明：

    1、insert方法：data有默认值，只传入对应想要修改的字段既可，注意如果有主键冲突会报错，
        如果想要忽略主键冲突，用merge方法。
    2、merge方法：如果有对应主键，则进行update操作，如果没有，则insert
    3、query方法：传入参数可以为字典或者字符串
    4、delete方法：传入参数可以为字典或者字符串
    5、rawExecute方法：直接执行sql语句
    6、insertMany方法，参数同insert方法，但是第二个参数是一个列表，列表每个值为要插入的字典
    7、mergeMany方法，参数同insertMany方法

使用样例：

    1、创建对象：
        m=DatabaseOperation("crt_ds")
    2、insert或者merge方法：
        data=m.insert("fx_orders",{"m_real_name":"太坑了"})
        data保存了插入数据的对象，可以直接使用对应的字段：
        print data.m_real_name;
        print data.o_id
    3、query方法：
        data=m.query("fx_orders",{"m_real_name":"太坑了"})
        data=m.query("fx_orders","m_real_name='什么啊'")
        使用字典查询，字符串字段可以不用加''
        使用字符串方式，字符串字段需要加上''
        查询结果如果有多条数据，可以使用first()取出第一条，
        print data.first().o_id
        如果想要全部处理：
        print data.all(),然后自己处理列表
    4、delete使用和参数同query
    5、rawExecute直接执行sql语句
        同样的，如果字段名为字符串，需要加上引号
    print m.rawExecute("select * from fx_orders where m_real_name='什么啊'")\
        .first().o_id

"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import create_session
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from FirefoxDemo.database.config import *
from datetime import datetime
import os
import inspect
import warnings
import sys
import hashlib
import pickle

# oracle需要的特殊配置
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 获取当前stdout的编码
if sys.stdout.encoding is None:
    stdout_encode = "utf-8"
else:
    stdout_encode = sys.stdout.encoding

# 下面代码为自动加载同级目录下的文件，并解析自动生成映射关系
"""modules保存所有符合条件的数据库模块
    1、 是py结尾的文件，排除掉一些特殊文件
    2、必须含有database属性，否则也不会放入modules
    3、导入失败的话，会有错误提示，根据错误提示修正问题
"""


def PATH(p):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), p)
    )


# database的绝对路径
sys.path.append(PATH("."))


def is_not_py(name:str):
    if name.find("Tables") ==-1:
        return True
    return False


def get_file_md5(filename):
    """计算文件md5
    """
    if not os.path.isfile(PATH(filename)):
        print("not a file")
        return
    myhash = hashlib.md5()
    with open(filename, "rb") as f:
        while True:
            b = f.read(8096)
            if not b:
                break
            myhash.update(b)
    return myhash.hexdigest()


"""加载文件的md5信息，根据文件md5判断文件是否有进行修改
"""
# 配置文件的md5信息
_config_md5 = get_file_md5(os.path.join(PATH(".."), "config.py"))
"""
1)是否存在md5.pickle文件，如果存在则检查配置文件是否修改，
如果没有修改则什么也不做,如果修改了则表信息设置为_config_md5
2)如果不存在md5.pickle，则表信息"tables_info为_config_md5"""
if os.path.isfile(PATH("md5.pickle")):
    with open(PATH("md5.pickle"), "rb") as f:
        tables_info = pickle.load(f)
        # 未修改配置文件
        if tables_info.get("config.py", "") == _config_md5:
            pass
        else:
            tables_info = {}
else:
    tables_info = {}
tables_info["config.py"] = _config_md5
"""
1)如果tables.pickle存在，则加载信息
2）如果不存在，则为空d{}
"""
if os.path.isfile(PATH("tables.pickle")):
    with open(PATH("tables.pickle"), "rb") as f:
        file_map = pickle.load(f)
else:
    file_map = {}


def get_database_from_module(module, database):
    """导入对应的文件，并返回文件中的所有符合条件(包含属性__table__)的类
    """
    try:
        name = file_map[module][database]
        mapper = {}
        # name is the moudle name,
        module = __import__(name, locals(), globals())
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for cls in clsmembers:
            if hasattr(cls[1], "__table__"):
                mapper[str(cls[1].__table__)] = cls[1]
            else:
                continue
        return mapper
    except KeyError:
        raise Exception(
            u"你选择的模块%s或者数据库%s配置需要有对应的xxxTables.py文件，"
            u"或者xxxTables.py文件导入错误".encode(
                stdout_encode) % (module, database))
    except ImportError as e:
        warnings.warn(u"数据库模块%s导入失败，检查%s文件代码是否存在问题，导入失败原因:%s".encode(
            stdout_encode) % (name, name, repr(e)))

for name in os.listdir(os.path.dirname(__file__)):
    # 读取文件夹下的文件（newsTables.py,userTables.py），排除一些文件，并且将满足条件的模块import进来
    if is_not_py(name):
        continue
    try:
        # print "文件名", name
        _md5 = get_file_md5(PATH(name))
        # 表示没有修改，直接跳过
        # print "原始md5", tables_info.get(name, "")
        # print "新的md5", _md5
        if tables_info.get(name, "") == _md5:
            continue
        module = __import__(name[:-3], locals(), globals())
        try:
            # 获取数据库
            database = getattr(module, "database")
            file_map[database] = {} # {"news":{}}
            database_conf = getattr(module, "config_name", "dataBase")
            # file_map={"news":{"test":"newsTables"}}
            # file_map={"news:"{"test":"newsTables"},"user":{"userCenter":"userTables"}
            file_map[database][database_conf] = name[:-3]
        except AttributeError:
            warnings.warn(u"文件%s中没有database属性，文件将被忽略" % module.__name__)
    except Exception as e:
        warnings.warn(u"数据库模块%s导入失败，检查%s文件代码是否存在问题，导入失败原因:%s") % (name, name, repr(e))
    finally:
        tables_info[name] = _md5

with open(PATH("md5.pickle"), "wb") as f:
    pickle.dump(tables_info, f)
# # file_map={"news:"{"test":"newsTables"},"user":{"userCenter":"userTables"}持久化
with open(PATH("tables.pickle"), "wb") as f:
    pickle.dump(file_map, f)
del name

db_url = "{dbType}+{engineType}://{user}:{password}@{host}:{port}/{db_name}?charset=utf8"

def order(func):
    """装饰器额外处理fx_orders表中o_id不唯一的情况
    """

    def _deco(self, tableName, dataDict):
        tempDict = dataDict
        if tableName == "fx_orders":
            timeNow = datetime.now()
            orderId = timeNow.strftime("%Y%m%d%H%M%S%f")[0:19]
            tempDict["o_id"] = orderId
        return func(self, tableName, tempDict)

    return _deco


class DatabaseOperation(object):
    """操作数据库
    """

    def __init__(self, module, database="dataBase"):
        try:
            databaseInfo = selectEnv(module)[database]
        except KeyError:
            raise Exception(u"你要使用的数据库模块%s在config中没有对应的配置".encode(
                stdout_encode) % module)
        try:
            database_type = databaseInfo["type"]
        except KeyError:
            database_type = "mysql"
            # warnings.warn(u"建议在%s数据库配置中加上type，默认为mysql".encode(
            #    stdout_encode) % module)
        databaseUrl = db_url.format(
            dbType=database_type,
            engineType="mysqlconnector",
            user=databaseInfo["user"],
            password=databaseInfo["passwd"],
            host=databaseInfo["host"],
            port=databaseInfo["port"],
            db_name=databaseInfo["db_name"])
        self.Base = declarative_base()
        engine = create_engine(databaseUrl, echo=False)
        self.metadata = MetaData(bind=engine)
        # self.session = create_session(bind=engine)
        self.session = sessionmaker(bind=engine)()
        try:
            self.map = get_database_from_module(module, database)
        except KeyError:
            raise Exception(
                u"你选择的模块%s或者数据库%s配置需要有对应的xxxTables.py文件，"
                u"或者xxxTables.py文件导入错误".encode(
                    stdout_encode) % (module, database))

    def insert(self, tableName, insertData):
        """插入数据
        """
        try:
            table = self.map[tableName]
        except KeyError:
            raise Exception("insert方法要先在tables文件中定义表的结构")
        data = table().data

        dataToInsert = self.replaceData(data, insertData)

        insertLine = table(**dataToInsert)
        self.session.add(insertLine)
        self.session.commit()

        return insertLine

    def merge(self, tableName, mergeData):
        """如果数据存在update，不存在则insert
        """
        try:
            table = self.map[tableName]
        except KeyError:
            raise Exception("merge方法要先在tables文件中定义表的结构")
        data = table().data

        dataToMerge = self.replaceData(data, mergeData)

        mergeLine = table(**dataToMerge)
        self.session.merge(mergeLine)
        self.session.commit()

        return mergeLine

    def query(self, tableName, queryData):
        """查询数据，查询方式可以是字典或者字符串
        """
        if tableName not in self.map:
            table = type(tableName, (self.Base,), {"__table__": Table(
                tableName, self.metadata, autoload=True)})
            self.map[tableName] = table
        else:
            table = self.map[tableName]
        if isinstance(queryData, dict):
            """接收字典类型
            """
            queryCondition = []
            for key, value in queryData.iteritems():
                if isinstance(value, str):
                    queryCondition.append(u"%s='%s'" %
                                          (key, value.decode("utf-8")))
                else:
                    queryCondition.append(u"%s='%s'" % (key, value))
            queryString = text(u" and ".join(queryCondition))
            return self.session.query(table).filter(queryString)
        elif isinstance(queryData, str):
            """接收字符串类型
            """
            return self.session.query(table). \
                filter(text(queryData.decode("utf-8")))

    def update(self, tableName, queryData, updateData):
        """更新数据
        """
        resultsList = self.query(tableName, queryData)
        updateCondition = {}
        if isinstance(updateData, dict):
            """接收字典类型
            """
            for key, value in updateData.iteritems():
                if isinstance(value, str):
                    updateCondition[key.decode("utf-8")] = \
                        value.decode("utf-8")
                else:
                    updateCondition[key.decode("utf-8")] = value
        elif isinstance(updateData, str):
            """接收字符串类型
            """
            updateParams = updateData.split(",")
            for param in updateParams:
                paramList = param.split("=")
                updateCondition[paramList[0].strip().decode("utf-8")] = \
                    paramList[1].strip().decode("utf-8")

        resultsList.update(updateCondition, synchronize_session='fetch')
        self.session.commit()
        return resultsList

    def delete(self, tableName, deleteData):
        """删除数据
        """
        self.query(tableName, deleteData).delete(synchronize_session='fetch')
        self.session.commit()

    def rawExecute(self, sql):
        """直接执行SQL语句
        """
        resData = self.session.execute(text(sql.decode("utf-8")))
        self.session.commit()
        return resData

    def insertMany(self, tableName, insertDataList):
        """批量插入数据
        """
        try:
            table = self.map[tableName]
        except KeyError:
            raise Exception("insertMany方法要先在tables文件中定义表的结构")
        data = table().data
        insertLines = []
        for insertData in insertDataList:
            dataToInsert = self.replaceData(data, insertData)
            insertLines.append(dataToInsert)
        index = 0
        while index < len(insertLines):
            self.session.execute(
                table.__table__.insert(),
                insertLines[index:index + 200])
            index += 200
            self.session.commit()

    def mergeMany(self, tableName, mergeDataList):
        """批量merge数据
        """
        try:
            table = self.map[tableName]
        except KeyError:
            raise Exception("mergeMany方法要先在tables文件中定义表的结构")
        data = table().data
        for mergeData in mergeDataList:
            dataToMerge = self.replaceData(data, mergeData)
            self.session.merge(table(**dataToMerge))
        self.session.commit()

    def replaceData(self, before, after):
        """传入参数都为字典，第一个参数是原始数据，第二个参数是想要替换的值
        """
        tempDict = before.copy()
        for key, value in after.items():# type:str
            if isinstance(value, str):
                tempDict[key] = value.encode(encoding="utf-8").decode("utf-8")
            else:
                tempDict[key] = value
        for key, value in tempDict.items():
            if isinstance(value, str):
                tempDict[key] = value.encode(encoding="utf-8").decode("utf-8")
            else:
                tempDict[key] = value
        return tempDict

    def __delete__(self):
        self.session.close()


# if __name__ == '__main__':
    """
    ma=DatabaseOperation("crt_ds")
    aaa="select * from fx_orders where m_real_name='什么啊'"
    print ma.rawExecute(aaa).first().o_id
    ad=ma.query("fx_orders","m_real_name='什么啊'")
    print ad.first().o_id
    ad=ma.query("fx_orders",{"m_real_name":"什么啊"})
    print ad.first().o_id
    ad=ma.insert("fx_orders",{})
    print ad.o_id
    ad=ma.insert("fx_orders",{})
    print ad.o_id
    ad=ma.query("fx_orders_item",{})
    print ad.first().o_id

#     ad=ma.insert("fx_orders",{"m_real_name":"太坑了"})
#     print ad.o_id
    ad=ma.merge("fx_orders", {"o_id":"111111111111111111","m_real_name":"什么啊啊啊啊啊啊啊"})
    print ad.o_id

#     m=DatabaseOperation("member")
#     print m.query("member_info","nickname='2258外求'").first().member_id"""
    """
    db = DatabaseOperation("member")
    print db.query("make_card_order", {"id": 802016120700000001}).first().card_code
    db.update("make_card_order", {"id": 802016120700000001}, {
              "card_code": "0000000000800102"})
    print db.query("make_card_order", {"id": 802016120700000001}).first().card_code
    db.update("make_card_order", {"id": 802016120700000001}, {
              "card_code": "0000000000800101"})
    print db.query("make_card_order", {"id": 802016120700000001}).first().card_code
    db = DatabaseOperation("crt_ds")
    o_id = db.insert("fx_orders", {"o_status": "WAIT_BUYER_PAY"}).o_id
    db.insertMany("fx_orders", [{"o_status": "WAIT_BUYER_PAY"}])
    print o_id
    print db.insert("fx_orders_items", {"o_id": o_id}).o_id
    print db.query("fx_orders", {"o_id": "2018083009313208800"}).first().o_id
    db.delete("fx_orders", {"o_id": "2018083009313208800"})"""
    # db = DatabaseOperation("financing")
    # print(db.query("white_list", {"mobile": "15986640072"}).first().mobile)

#     db2 = DatabaseOperation("midconsole")
#     print db2.query("mid_module_api_t", {"api_key": "api.auto./w/p/c"}).first().api_key
#     db2.delete("mid_module_api_t",{"api_key":"api.auto./w/p/c"})
#     db2 = DatabaseOperation("settlement")
#     print db2.merge("ebusiness_transaction", {}).order_no
#     print db2.merge("mbr_ebusiness_daily_clearing", {}).p_order_no
# print db.query("fx_orders_items", {"o_id":
# "2017122609543315900"}).all()[0]
