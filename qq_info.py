#!/usr/bin/env python3
# -*- conding:utf-8 -*-
import time
import json

import requests

from random import randint
from pymysql.err import InternalError

url = "https://ti.qq.com/cgi-bin/more_profile_card/more_profile_card"

headers = {
	'Origin': 'http://ti.qq.com',
	'User-Agent': 'Mozilla/5.0 (Linux; Android 9; PADT00 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 V1_AND_SQ_7.1.0_0_TIM_D TIM/2.3.1.1834 QQ/6.5.5  NetType/WIFI WebP/0.3.0 Pixel/1080',
	'Referer': 'http://ti.qq.com/qcard/index.html?qq=2386001503',
	'Cookie': 'pgv_info=ssid=s7796942920; pgv_pvid=5861781518; uin=o1426175909; p_uin=o1426175909; skey=MUAYzIk6Ux',
}

flag = 0
flag2 = 0

def get_info(qq, bkn):
	post_data = {
		'_q': str(qq),
		'bkn': str(bkn),
		'src': 'mobile'
		}
	req = requests.post(url, headers=headers, data=post_data)
	data = json.loads(req.text)
	if data.get("profile"):
		sourceData = data.get("profile")[0]
		sourceData["QQ"] = qq
		sourceData = json.loads(json.dumps(sourceData).replace("&nbsp;", " "))
		info = parseData(sourceData)
		return (info, sourceData)
	else:
		if data.get("ec") == "100000":
			print("[qwq] Cookie失效,请重新登录~")
		elif data.get("em") == "server&nbsp;busy":
			print(qq,"Not Found.")
		elif data.get("em") == "查看资料过于频繁":
			flag += 1
			flag2 = qq
			if flag == 2 and flag2 == qq:
				print("Stop!!!!花QQQQQ")
				exit()
			print(f"[Error] QQ => {qq} 查看资料过于频繁")

			end = randint(15,60)
			sleep(end=end)

			get_info(qq, bkn)
		elif data.get("msg") == "资料卡黑名单用户":
			print("[QAQ] 被腾讯拉黑惹=_=")
			print(data)
			exit()
		else:
			print("[Error] 未知错误")
			print(data)
			print("="*50)
		return (None, None)

def parseData(data):
	qq = data["QQ"]

	nick = data.get("nick")
	if not nick:
		print(data)

	gender = data.get("gender")
	if gender == 1: gender = "男"
	elif gender == 2: gender = "女"
	else: gender = "未知"

	age = data.get("age")
	if not age:
		age = -1

	birthday = data.get("birthday")
	birthday = f"{birthday.get('year')}-{birthday.get('month')}-{birthday.get('day')}"
	if not birthday:
		birthday = "nil"

	stl = ["未填",
		"水瓶座",
		"双鱼座",
		"白羊座",
		"金牛座",
		"双子座",
		"巨蟹座",
		"狮子座",
		"处女座",
		"天秤座",
		"天蝎座",
		"射手座",
		"摩羯座"]

	if data.get("constellation"):
		try:
			constellation = stl[data.get("constellation")]
		except IndexError:
			constellation = "FLAG-"+str(data.get("constellation"))
	else:
		constellation = "nil"

	occu = ["",
		"IT 计算机/互联网/通信",
		"制造 生产/工艺/制造",
		"医疗 医疗/护理/制药",
		"金融 金融/银行/投资/保险",
		"商业 商业/服务业/个体经营",
		"文化 文化/广告/传媒",
		"艺术 娱乐/艺术/表演",
		"法律 律师/法务",
		"教育 教育/培训",
		"行政 公务员/行政/事业单位",
		"模特 模特",
		"空姐 空姐",
		"学生 学生",
		"其他职业"]
	if data.get("occupation"):
		try:
			occupation = occu[data.get("occupation")]
		except IndexError:
			occupation = "FLAG-"+str(data.get("occupation"))
	else:
		occupation = "nil"

	company = data.get("company")
	if not company:
		company = "nil"

	college = data.get("college")
	if not college:
		college = "nil"
	elif len(college) > 1:
		if college[:-1] == college[1:] and college[0] == "\x00":
			college = "nil"

	location = "-".join([data.get("location_country"),
						 data.get("location_state"),
						 data.get("location_city"),
						 data.get("location_area")]).strip("-")
	if not location:
		location = "nil"

	hometown = "-".join([data.get("hometown_country"),
						 data.get("hometown_state"),
						 data.get("hometown_city"),
						 data.get("hometown_area")]).strip("-")
	if not hometown:
		hometown = "nil"

	telephone = data.get("telephone")
	if not telephone:
		telephone = "nil"

	email = data.get("email")
	if not email:
		email = "nil"
	elif len(email) > 1:
		if email[:-1] == email[1:] and email[0] == "\x00":
			email = "nil"

	personal = data.get("personal")
	if not personal:
		personal = "nil"
	elif len(personal) > 1:
		if personal[:-1] == personal[1:] and personal[0] == "\x00":
			personal = "nil"

	return {
		"QQ": qq,
		"昵称": nick,
		"性别": gender,
		"年龄": age,
		"生日": birthday,
		"星座": constellation,
		"职业": occupation,
		"公司": company,
		"教育经历": college,
		"所在地": location,
		"故乡": hometown,
		"电话": telephone,
		"邮箱": email,
		"个人说明": personal,
	}

def get_bkn(skey): 
	hash_ = 5381 
	for i in range(len(skey)): 
		hash_ += (hash_ << 5) + ord(skey[i]) 
	return hash_ & 2147483647

def initDatabase():
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

	sql_create_table = '''CREATE TABLE QQ_USER_INFO (
		id INT auto_increment PRIMARY KEY ,
		qq varchar(11),
		nick varchar(100),
		gender varchar(2),
		age INT,
		birthday varchar(10),
		constellation varchar(3),
		company varchar(50),
		occupation varchar(50),
		college varchar(50),
		location varchar(50),
		hometown varchar(50),
		telephone varchar(50),
		email varchar(50),
		personal varchar(520)
		)ENGINE=innodb DEFAULT CHARSET=utf8;
	'''
	cursor.execute(sql_create_table)# 创建库:QQ_USER_INFO
	conn.commit()
	cursor.close()
	conn.close()

def save_data_mysql(data):
	import pymysql
	# 打死不用Key-Value(NoSQL)数据库
	# Miko: NoSQL是数据库吗???
	conn = pymysql.connect(
		host="localhost",
		user="root",password="miko001.",
		database="tencent",
		charset="utf8")

	cursor = conn.cursor()	

	sql_insert = f"""insert into QQ_USER_INFO(
		qq,
		nick,
		gender,
		age,
		birthday,
		constellation,
		occupation,
		company,
		college,
		location,
		hometown,
		telephone,
		email,
		personal) values(
		"{data.get("QQ")}",
		"{data.get("昵称")}",
		"{data.get("性别")}",
		"{data.get("年龄")}",
		"{data.get("生日")}",
		"{data.get("星座")}",
		"{data.get("职业")}",
		"{data.get("公司")}",
		"{data.get("教育经历")}",
		"{data.get("所在地")}",
		"{data.get("故乡")}",
		"{data.get("电话")}",
		"{data.get("邮箱")}",
		"{data.get("个人说明")}")"""

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
	skey = [i.split("=", 1)[1] for i in cookie.split("; ") if i.split("=")[0] == "skey"]
	if not skey:
		print("[Error] skey not in Cookie.")
		return
	bkn = get_bkn(skey[0])

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

	qq = 10304
	while qq < 100000000000:
		info, sourceData = get_info(qq, bkn)

		if not info:
			qq += 1
			sleep(randint(3,10))
			continue

		for k, v in info.items():
			print(k, "=>", repr(v))
		print("="*50)

		save_data_mysql(info)
		qq += 1

		end = randint(3,23)
		sleep(end=end)
		# break

if __name__ == '__main__':
	main()