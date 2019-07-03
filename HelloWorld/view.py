# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     view
   Description :
   Author :       Administrator
   date：          2019/7/2 0002
-------------------------------------------------
"""
from django.shortcuts import render


def hello(request):
	context = {}
	context['hello'] = 'Hello tny!'
	return render(request, 'hello.html', context)
