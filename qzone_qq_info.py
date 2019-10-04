#!/usr/bin/env python3
# -*- conding:utf-8 -*-
import os
import re
import time
import json

import requests

from random import randint
from pymysql.err import InternalError

url = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all?uin={qq}&fupdate=1&g_tk={gtk}"

headers = {
	'User-Agent': 'Mozilla/5.0 (Linux; Android 9; PADT00 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 V1_AND_SQ_7.1.0_0_TIM_D TIM/2.3.1.1834 QQ/6.5.5  NetType/WIFI WebP/0.3.0 Pixel/1080',
	'Cookie': 'pgv_info=ssid=s2528652011; uin=o2386001503; skey=qwq; p_uin=o2386001503; p_skey=owo',
}

def get_info(qq, gtk): # 获取信息
	req = requests.get(url.format(qq=qq, gtk=gtk), headers=headers)
	try:
		data = json.loads(re.findall("_Callback\((.*?)\);", req.text, re.S)[0])
	except Exception as e:
		print(re.findall("_Callback\((.*?)\);", req.text, re.S)[0])
		raise e
	if data.get("data"):
		sourceData = data.get("data")
		sourceData = json.loads(json.dumps(sourceData).replace("&nbsp;", " "))
		info = parseData(sourceData)
		return (info, sourceData)
	else:
		if data.get("message") == "请先登录":
			print("[Error] 请先登录")
			exit()
		elif data.get("message") == "您无权访问":
			print("[Warning] 无权访问")
		else:
			print("[Error] 未知错误")
			print(data)
			print("="*50)
		return (None, None)

def parseCookie(cookie): # 解析cookie
	return dict([l.split("=", 1) for l in cookie.split("; ")])

def parseData(data): # 解析数据
	qq = data["uin"]

	spacename = data.get("spacename")

	nick = data.get("nickname")

	sex = data.get("sex")
	if sex == 1: sex = "男"
	elif sex == 2: sex = "女"
	else: sex = "未知"

	age = data.get("age")
	if not age:
		age = -1

	birthday = data.get("birthday")
	birthyear = str(data.get("birthyear"))
	birthday = (birthyear+"-"+birthday).strip("-")
	if not birthday:
		birthday = "nil"

	n = [
		"未填写",
		"白羊座",
		"金牛座",
		"双子座",
		"巨蟹座",
		"狮子座",
		"处女座",
		"天秤座",
		"天蝎座",
		"射手座",
		"魔羯座",
		"水瓶座",
		"双鱼座"
	]

	if data.get("constellation"):
		try:
			constellation = n[data.get("constellation")+1]
		except IndexError:
			constellation = "FLAG-"+str(data.get("constellation"))
	else:
		constellation = "nil"

	# occu = ["",
	# 	"IT 计算机/互联网/通信",
	# 	"制造 生产/工艺/制造",
	# 	"医疗 医疗/护理/制药",
	# 	"金融 金融/银行/投资/保险",
	# 	"商业 商业/服务业/个体经营",
	# 	"文化 文化/广告/传媒",
	# 	"艺术 娱乐/艺术/表演",
	# 	"法律 律师/法务",
	# 	"教育 教育/培训",
	# 	"行政 公务员/行政/事业单位",
	# 	"模特 模特",
	# 	"空姐 空姐",
	# 	"学生 学生",
	# 	"其他职业"]
	# if data.get("occupation"):
	# 	try:
	# 		occupation = occu[data.get("occupation")]
	# 	except IndexError:
	# 		occupation = "FLAG-"+str(data.get("occupation"))
	# else:
	# 	occupation = "nil"

	# company = data.get("company")
	# if not company:
	# 	company = "nil"

	# college = data.get("college")
	# if not college:
	# 	college = "nil"
	# elif len(college) > 1:
	# 	if college[:-1] == college[1:] and college[0] == "\x00":
	# 		college = "nil"

	hometown = "-".join([data.get("hco"),
						 data.get("hp"),
						 data.get("hc")]).strip("-")
	if not hometown:
		hometown = "nil"

	company_location = "-".join([data.get("cco"),
						 data.get("cp"),
						 data.get("cc"),
						 data.get("cb")]).strip("-")
	if not company_location:
		company_location = "nil"

	# telephone = data.get("telephone")
	# if not telephone:
	# 	telephone = "nil"

	# email = data.get("email")
	# if not email:
	# 	email = "nil"
	# elif len(email) > 1:
	# 	if email[:-1] == email[1:] and email[0] == "\x00":
	# 		email = "nil"

	# personal = data.get("personal")
	# if not personal:
	# 	personal = "nil"
	# elif len(personal) > 1:
	# 	if personal[:-1] == personal[1:] and personal[0] == "\x00":
	# 		personal = "nil"

	return {
		"QQ": qq,
		"空间名": spacename,
		"昵称": nick,
		"性别": sex,
		"年龄": age,
		"生日": birthday,
		"星座": constellation,
		# "职业": occupation,
		# "公司": company,
		# "教育经历": college,
		"故乡": hometown,
		"公司所在地": company_location,
		# "电话": telephone,
		# "邮箱": email,
		# "个人说明": personal,
	}

# def get_bkn(skey): 
# 	hash_ = 5381 
# 	for i in range(len(skey)): 
# 		hash_ += (hash_ << 5) + ord(skey[i]) 
# 	return hash_ & 2147483647

def get_gtk(cookie): # 计算gtk
	cookie_dict = parseCookie(cookie)
	skey = cookie_dict.get("p_skey") or cookie_dict.get("skey")
	hash_ = 5381 
	for i in range(len(skey)): 
		hash_ += (hash_ << 5) + ord(skey[i]) 
	return hash_ & 0x7fffffff

def initDatabase(): # 初始化数据库
	import pymysql
	# 打死不用Key-Value(NoSQL)数据库
	# Miko: NoSQL是数据库吗???

	conn = pymysql.connect(
		host="localhost",
		user="root",password="miko001.",
		charset="utf8")

	cursor = conn.cursor()
	
	sql_create_database = "CREATE DATABASE IF NOT EXISTS tencent"
	cursor.execute(sql_create_database) # 创建库:tencent

	cursor.execute("use tencent")

	sql_create_table = '''CREATE TABLE QZONE_USER_INFO (
		id INT auto_increment PRIMARY KEY ,
		qq varchar(11),
		nick varchar(100),
		spacename varchar(100),
		sex varchar(2),
		age INT,
		birthday varchar(10),
		constellation varchar(3),
		hometown varchar(50),
		company_location varchar(50)
		)ENGINE=innodb DEFAULT CHARSET=utf8;'''
	# 	company varchar(50),
	# 	occupation varchar(50),
	# 	college varchar(50),
	# 	telephone varchar(50),
	# 	email varchar(50),
	# 	personal varchar(520)
	# 	)ENGINE=innodb DEFAULT CHARSET=utf8;
	# '''
	cursor.execute(sql_create_table)# 创建库:QZONE_USER_INFO
	conn.commit()
	cursor.close()
	conn.close()

def save_to_mysql(data):
	import pymysql
	# 打死不用Key-Value(NoSQL)数据库
	# Miko: NoSQL是数据库吗???
	conn = pymysql.connect(
		host="localhost",
		user="root",password="miko001.",
		database="tencent",
		charset="utf8")

	cursor = conn.cursor()	

	sql_insert = f"""insert into QZONE_USER_INFO(
		qq,
		nick,
		spacename,
		sex,
		age,
		birthday,
		constellation,
		hometown,
		company_location
		) values(
		"{data.get("QQ")}",
		"{data.get("昵称")}",
		"{data.get("空间名")}",
		"{data.get("性别")}",
		"{data.get("年龄")}",
		"{data.get("生日")}",
		"{data.get("星座")}",
		"{data.get("故乡")}",
		"{data.get("公司所在地")}")
		"""
		# occupation,
		# company,
		# college,
		# telephone,
		# email,
		# personal) values(
		# "{data.get("职业")}",
		# "{data.get("公司")}",
		# "{data.get("教育经历")}",
		# "{data.get("电话")}",
		# "{data.get("邮箱")}",
		# "{data.get("个人说明")}")"""

	sql_insert = sql_insert.replace("\n\t\t", " ")
	try:#"alter table QQ_USER_INFO modify column nick varchar(100);"
		cursor.execute("SET NAMES utf8mb4") # utf8 3字节  utf8mb4 4字节(存放emoji表情)
		cursor.execute(sql_insert) # 插入数据
	except Exception as e:
		print(sql_insert)
		raise e
	conn.commit()
	cursor.close()
	conn.close()

# def save_to_excel(filename, data):
# 	import pandas as pd
# 	data = json.dumps(data, ensure_ascii=False).replace(": ", ":").replace(", ", ",")
# 	pd_data = pd.read_json(data)
# 	pd_data.to_excel(filename)

def save_to_text(path, filename, data, writh_function):
	filename = filename.replace("/", "_").replace("\\", "_")
	if not os.path.exists(path):
		os.makedirs(path)
	if path[-1] != os.sep:
		path += os.sep
	if not os.path.exists(path + filename) and ("w" not in writh_function or "+" not in writh_function):
		f = open(path + filename, "w")
		f.close()
	with open(path + filename, writh_function) as f:
		f.write(data)

def sleep(end, start=0):
	for i in range(end):
		one = "="*int(round(start/end*100,2)/2) 
		two = " "*int(50-round(start/end*100,2)/2) 
		print(f"\r{end}s Sleep %3d%% [%s>%s] "%(start/end*100, one, two), end="") 
		time.sleep(1)
		start += 1
	print("\n"+("="*50))

def main():
	if headers.get("cookie"):
		cookie = headers.get("cookie")
	elif headers.get("Cookie"):
		cookie = headers.get("Cookie")
	else:
		print("[Error] Cookie not found.")
		return
	# skey = [i.split("=", 1)[1] for i in cookie.split("; ") if i.split("=")[0] == "skey"]
	# if not skey:
	# 	print("[Error] skey not in Cookie.")
	# 	return
	# bkn = get_bkn(skey[0])
	gtk = get_gtk(cookie)

	try:
		initDatabase()
	except InternalError:
		print("花Q!")

	# qq_5 = [i for i in range(10000, 100000)] # 5位QQ
	# qq_6 = [i for i in range(100000, 1000000)] # 6位QQ
	# qq_7 = [i for i in range(1000000, 10000000)] # 7位QQ
	# qq_8 = [i for i in range(10000000, 100000000)] # 8位QQ
	# qq_9 = [i for i in range(100000000, 1000000000)] # 9位QQ
	# qq_10 = [i for i in range(1000000000, 10000000000)] # 10位QQ
	# qq_11 = [i for i in range(10000000000, 100000000000)] # 11位QQ

	# qq = 10343
	# qq = 2000000000
	qq_list = [randint(100000000, 3500000000) for _ in range(100)]
	# while qq < 100000000000:
	for qq in qq_list:
		# info, sourceData = get_info(qq, bkn)
		info, sourceData = get_info(qq, gtk)

		if not info:
			# qq += 1
			# sleep(randint(3,10))
			continue

		info_texts = ""
		for k, v in info.items():
			text = k+" => "+repr(v)
			info_texts += text+"\n"
		info_texts += ("="*50)+"\n"
		print(info_texts)

		sourceData_texts = ""
		for k, v in sourceData.items():
			text = k+" => "+repr(v)
			sourceData_texts += text+"\n"
		sourceData_texts += ("="*50)+"\n"

		save_to_mysql(info)
		save_to_text("QzoneInfo", "QzoneInfo.txt", info_texts, "a+")
		save_to_text("QzoneSourceData", "soueceData.txt", sourceData_texts, "a+")
		# qq += 1

		# end = randint(3,23)
		end = randint(0,3)
		sleep(end=end)
		# break

if __name__ == '__main__':
	main()