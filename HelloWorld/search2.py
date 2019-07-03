# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     search2
   Description :
   Author :       Administrator
   date：          2019/7/3 0003
-------------------------------------------------
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators import csrf

"""
request对象属性:
['COOKIES', 'FILES', 'GET', 'META', 'POST', '__class__',
'__delattr__', '__dict__', '__dir__', '__doc__', '__eq__',
'__format__', '__ge__', '__getattribute__', '__gt__', '__hash__',
'__init__', '__init_subclass__', '__iter__', '__le__', '__lt__',
 '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
  '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
   '__weakref__', '_body', '_current_scheme_host', '_encoding', '_files',
    '_get_full_path', '_get_post', '_get_raw_host', '_get_scheme',
    '_initialize_handlers', '_load_post_and_files', '_mark_post_parse_error',
     '_messages', '_post', '_read_started', '_set_post', '_stream',
     '_upload_handlers', 'body', 'build_absolute_uri', 'close', 'content_params',
      'content_type', 'csrf_processing_done', 'encoding', 'environ', 'get_full_path',
       'get_full_path_info', 'get_host', 'get_port', 'get_raw_uri', 'get_signed_cookie',
        'headers', 'is_ajax', 'is_secure', 'method', 'parse_file_upload', 'path',
         'path_info', 'read', 'readline', 'readlines', 'resolver_match',
         'scheme', 'session', 'upload_handlers', 'user', 'xreadlines']
"""


def search_post(request):
	ctx = {}
	if request.POST:
		# ctx['rlt'] = request.POST['q']
		ctx['rlt'] = request.get_full_path()
	return render(request, "post.html", ctx)
