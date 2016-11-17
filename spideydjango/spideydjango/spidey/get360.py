#coding=utf-8
import urllib
import urllib2
import gzip
import StringIO
import json
import re

TIMEOUT=12

def getscorefrom360(scanurl):
	#get the token and the timestamp
	url1=r"http://webscan.360.cn/index/checkwebsite?url="+scanurl
	headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
	}
	try:
		request = urllib2.Request(url1,headers=headers)  
		response = urllib2.urlopen(request,timeout=TIMEOUT)
	except:
		print '* get360.py:getscorefrom360():Network Error'
		return [-1,-1,-1,-1]
	page = response.read()
	matchObj=re.search('data:"url="\+url\+"&token=[0-9a-f]+&time=[0-9]+',page)
	#print (matchObj.group())

	headers = {
	'Host':'webscan.360.cn',
	'Connection':'keep-alive',
	'Cache-Control':'max-age=0',
	'Accept':'application/json, text/javascript, */*; q=0.01',
	'Origin':'http://webscan.360.cn',
	'X-Requested-With':'XMLHttpRequest',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
	'Content-Type':'application/x-www-form-urlencoded',
	'Referer':'http://webscan.360.cn/index/checkwebsite?url='+scanurl,
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.8'
	}
	values={}
	try:
		values['url']=scanurl
		values['token']=matchObj.group()[24:56]
		values['time']=matchObj.group()[62:72]
		data = urllib.urlencode(values)
		url2 = 'http://webscan.360.cn/index/gettrojan'
		request = urllib2.Request(url2,headers=headers,data=data)
		response = urllib2.urlopen(request)
		page=json.load(gzip.GzipFile(fileobj=StringIO.StringIO(response.read())))
	except:
		return [-1,-1,-1,-1]
	#print page

	result=ex360(page)

	#get the score of 360
	'''
	headers = {
		#POST /webscore/index HTTP/1.1
		'Host':'webscan.360.cn',
		'Connection':'keep-alive',
		#'Content-Length':'102',
		'Cache-Control':'max-age=0',
		'Accept':'application/json, text/javascript, */*; q=0.01',
		'Origin':'http://webscan.360.cn',
		'X-Requested-With':'XMLHttpRequest',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
		'Content-Type':'application/x-www-form-urlencoded',
		'Referer':'http://webscan.360.cn/index/checkwebsite?url='+scanurl,
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8',
		#'Cookie':r'__huid=108PVAx8iQ01%2By5V%2FfYolWcH8DzJ2Mzy0jUFngM9S8BRg%3D; __guid=156009789.1856201746112243000.1477314382681.305; PHPSESSID=c81e5bd95d9b738a0df1da579f726c18; __utmt=1; 360webscan_tongji_cookie=null; __utma=184508192.1490595888.1477314419.1477314419.1477358934.2; __utmb=184508192.3.10.1477358934; __utmc=184508192; __utmz=184508192.1477314419.1.1.utmcsr=360.cn|utmccn=(referral)|utmcmd=referral|utmcct=/download/; CNZZDATA1254937590=681896688-1477312504-http%253A%252F%252Fwww.360.cn%252F%7C1477355710'
	}
	values = {}
	values['isxujia']=result[1]
	values['iscuangai']=result[2]
	values['isviolation']='0'
	values['isguama']=result[4]
	values['high']='0'
	values['mid']='0'
	values['low']='0'
	values['info']='0'
	values['domain']=scanurl
	values['pangzhu']='0'
	data = urllib.urlencode(values)
	url = 'http://webscan.360.cn/webscore/index'
	request = urllib2.Request(url,headers=headers,data=data)
	response = urllib2.urlopen(request)
	page=json.load(gzip.GzipFile(fileobj=StringIO.StringIO(response.read())))
	#print str(page['total_score'])
	
	'''

	turnresult=[result[0],result[1],result[2],result[4]]
	'''
	result=[]
	for i in turnresult:
		if i==1:
			result.append(3)
		else:
			result.append(1)
	'''
	#print result
	return turnresult

def ex360(data):
	webtype = ""
	st = ""
	sc = ""
	ssc = ""
	isfake = 0				#fake web
	isdistort = 0			#distort
	iswoodenhorse = 0		#trojan web
	kx = 0					#authenticate or not
	kx_state = 0			#authenticate state
	kx_url = ''				#certurl
	trojan_list=''
	kneturl=''
	result=[0,0,0,'0',0,'0','0','0','0']

	if data['state'][:4]=="fail":
		return [-1,-1,-1,'0',-1,'0','0','0','0']
	if data.has_key('trojan'):		#dangerous web
		webtype = data['trojan']['type']
		st = data['trojan']['st']
		sc = data['trojan']['sc']
		if data['trojan'].has_key('ssc'):
			ssc = data['trojan']['ssc']
		trojan_list = data['trojan']['list']
	if data.has_key('kx'):
		kx_state = data['kx']['state']
		if data['kx'].has_key('url'):
			kx_url = data['kx']['url']
	if data.has_key('knet'):
		kneturl = data['knet']
	if kx_state == '1':		#if authenticated
		if len(kx_url) > 0:
			print 'authenticate url:'+kx_url
			result[0]=0
		return result
	if kneturl!='':
		print kneturl
		result[0]=0
		return result
	if webtype == '60' and st == '10' and sc == '115' and ssc == '1151':
		isdistort = 2
		result[0]=2
	elif webtype == '40' and st == '50':
		isdistort=2
		result[0]=2
	elif (webtype == '60' and st == '20') or webtype =='70':
		iswoodenhorse=2
		result[0]=2
	elif webtype == '60':
		isfake=2
		result[0]=2
	elif(webtype == '50' or (trojan_list != None and len(trojan_list) > 0)):
		iswoodenhorse=2
		result[0]=2
	else:
		result[0]=0

	result[1]=isfake
	result[2]=isdistort
	result[4]=iswoodenhorse
	#print result
	return result