# -*- coding: utf-8 -*-
"""
Created on 2016-12-27
@author hechangshu1
"""

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
# from lib import config
from datetime import datetime

# 获取公共帐号信息
database = "news"
config_name = "test"
# config_name = "selfstockdb"
# 获取对应模块的数据库信息
# databaseInfo=config.selectEnv(database)[config_name]
# databaseUrl="mysql://%s:%s@%s:%s/%s?charset=utf8"%(databaseInfo["user"],
#                                                    databaseInfo["passwd"],
#                                                    databaseInfo["host"],
#                                                    databaseInfo["port"],
#                                                    databaseInfo["db_name"]
#                                                    )
databaseUrl = "mysql+mysqlconnector://root:Test123456!@localhost:3306/test"
timeNow = datetime.now()
insertTime = timeNow.strftime("%Y-%m-%d %H:%M:%S")
orderId = timeNow.strftime("%Y%m%d%H%M%S%f")[0:19]
payId = timeNow.strftime("%Y%d%m%H%M%S%f")[0:19]
poId = timeNow.strftime("%Y%m%d%f%S%H%M")[0:19]

Base = declarative_base()
engine = create_engine(databaseUrl, echo=False)
metadata = MetaData(bind=engine)


class User(Base):
    __table__ = Table("user", metadata, autoload=True)
    data = {
        "id": "",
        "name": ""
    }


tableClassMapperMember = {
    "user": User
}


class Customer(Base):
    __table__ = Table("customer", metadata, autoload=True)
    data = {
        "id": "",
        "name": ""
    }


tableClassMapperMember = {
    "user": Customer
}