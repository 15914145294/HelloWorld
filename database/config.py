# -*- coding: utf-8 -*-

import time
import sys

'''
   环境选择1
'''

if len(sys.argv) > 1:
	env = sys.argv[6]
else:
	env = 'sit'
connectionType = 'direct'  # 接口连接方式  @openAPI 或者 @direct

'''配置全局变量
'''
publicParam = {

}

testDataPath = {
	"dev": "testdata_sit.ini",
	"uat": "testdata_uat.ini",
	"sit": "testdata_sit.ini",
	"product": "testdata_dev.ini"
}


def selectFile():
	# from bin.testexecute import TestExecute #调试的时候请屏蔽
	# env = sys.argv[len(sys.argv) - 2]
	return testDataPath[env]


def selectEnv(module):
	# from bin.testexecute import TestExecute #调试的时候请屏蔽
	data = env + '_' + module
	data = eval(data)
	return data


'''测试环境配置
'''

sit_snow = {
	"connectionURL": {
		#        "openAPI": "",
		"direct": "http://stock.xueqiu.com"
	}
}

sit_market = {
	"connectionURL": {
		#        "openAPI": "",
		"direct": "http://127.0.0.1"
	},
	"symboldb": {
		"host": "127.0.0.1",
		"user": "hq",
		"passwd": "QPbFI57V",
		"port": 3306,
		"db_name": "symdb"
	}
}

sit_tiger = {
	"connectionURL": {
		#        "openAPI": "",
		"direct": ""
	}
}

sit_news = {
	"connectionURL": {
		#        "openAPI": "",
		"direct": "http://127.0.0.1:8080"
	},

	"selfstockdb": {
		"host": "127.0.0.1",
		"user": "testdb",
		"passwd": "QPbFI57V",
		"port": 3306,
		"db_name": "selfdb"
	},

	"test": {
		"host": "127.0.0.1",
		"user": "root",
		"passwd": "Test123456!",
		"port": 3306,
		"db_name": "test",
		"type":"mysql"
	},

	"redis": [
		{"host": "127.0.0.1", "port": 6386, "password": "",},
		{"host": "127.0.0.1", "port": 6387, "password": "",},
		{"host": "127.0.0.1", "port": 6388, "password": "",}
	]
}
