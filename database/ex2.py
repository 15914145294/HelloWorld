# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ex2
   Description :
   Author :       Administrator
   date：          2019/7/7 0007
-------------------------------------------------
"""
import pickle
with open("md5.pickle", "rb") as f:
    file_map = pickle.load(f)
print(file_map)