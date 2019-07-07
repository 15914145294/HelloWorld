# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ex1
   Description :
   Author :       Administrator
   date：          2019/7/6 0006
-------------------------------------------------
"""
from FirefoxDemo.database import  SQLManager

d =SQLManager.DatabaseOperation(module="news",database="test")
d.insert(tableName="user",insertData={"id":15,"name":"tny4"})
