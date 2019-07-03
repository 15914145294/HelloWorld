# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name： search
   Description :
   Author :   Administrator
   date：  2019/7/3 0003
-------------------------------------------------
"""
from django.http import HttpResponse
from django.shortcuts import render_to_response

def search_form(request):
	return render_to_response("search_from.html")

# 接收请求数据
def search(request):  
	request.encoding='utf-8'
	if 'q' in request.GET:
		message = '你搜索的内容为: ' + request.GET['q']
	else:
		message = '你提交了空表单'
	return HttpResponse(message)
