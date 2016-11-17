#coding=utf-8
import base64
import time
import md5
import urllib
import urllib2
import json
from bs4 import BeautifulSoup

TIMEOUT=12
MAX_DOWNLOAD_ERROR_TIME=3

#function for use jinshan API to judge whether it is phish web or not
def isphish(scanurl):
	#the paraments for function
	q=base64.urlsafe_b64encode(scanurl)
	appkey="k-33356"
	timestamp=time.time()
	secret="a176201e188a0969cd7b7fa2ef3c8d14"

	#caculate the sign
	APIurl='/phish/?appkey='+appkey+'&q='+q+'&timestamp='+str(timestamp)
	signmd5=md5.new()
	signmd5.update(APIurl+secret)
	sign=signmd5.hexdigest()

	#send the request
	phishurl="http://open.pc120.com/phish/?q="+q+"&appkey="+appkey+"&timestamp="+str(timestamp)+"&sign="+str(sign)
	request = urllib2.Request(phishurl)
	try:
		response = urllib2.urlopen(request,timeout=TIMEOUT)
	except:
		print "* jinshan.py:isphish():network Error!"
		return -1
	page=json.load(response)
	#print page['phish']
	phish = page['phish']
	if phish==1 or phish==2:
		phish=(phish)%2+1
	return phish

#function for use jinshan API to judge whether it have vicious download link
def isdownload(scanurl):
	#the paraments for function
	try:
		q=base64.urlsafe_b64encode(scanurl)
	except:
		return 1
	appkey="k-33356"
	timestamp=time.time()
	secret="a176201e188a0969cd7b7fa2ef3c8d14"

	#caculate the sign
	APIurl='/download/?appkey='+appkey+'&q='+q+'&timestamp='+str(timestamp)
	signmd5=md5.new()
	signmd5.update(APIurl+secret)
	sign=signmd5.hexdigest()

	#send the request
	phishurl="http://open.pc120.com/download/?q="+q+"&appkey="+appkey+"&timestamp="+str(timestamp)+"&sign="+str(sign)
	try:
		request = urllib2.Request(phishurl)
		response = urllib2.urlopen(request,timeout=TIMEOUT)
		page=json.load(response)
		#print page
		#print page['down_type']
		return page['down_type']
	except:
		print '* jinshanpy:isdownload():Download judge apart Error!'
		return None

#function for use isdownload() to judge whether it include dangerous download link
def isIncDangerDownload(scanurl):
	#get the content of the web and extract the link of download
	if scanurl[:4]!='http':
		scanurl=r'http://'+scanurl
	headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
	}
	try:
		request = urllib2.Request(scanurl,headers=headers)
		response = urllib2.urlopen(request,timeout=TIMEOUT)
		content=response.read()
	except:
		print '* jinshan.py:isIncDangerDownload():Network Error during scan '+scanurl
		return 0
	soup=BeautifulSoup(content,'html.parser')

	downloadscore=0
	downloadflag=0
	errortime=0
	#judge all a links from the scanurl
	downloadurls=soup.findAll('a')
	for link in downloadurls:
		tmp_url=link.get('href')
		if tmp_url=="" or tmp_url==None or tmp_url[:1]=='#' or tmp_url[:11]=='javascript:' or tmp_url[:7]=='mailto:' or tmp_url[-4:]=='html' or tmp_url[-3:]=='htm':
			continue
		#print tmp_url
		if tmp_url[0]=='/' and scanurl[-1]=='/':
			tmp_url=scanurl[:-1]+tmp_url
		if tmp_url[0]=='?' or tmp_url[0:2]=='..':
			tmp_url=scanurl+tmp_url
		score=isdownload(tmp_url)
		if score==None:
			errortime+=1
		if errortime>=MAX_DOWNLOAD_ERROR_TIME:
			downloadflag=-1
			break
		if score!=2:
			downloadflag=1
			if score==3:
				downloadscore+=1

	#print downloadflag
	#print downloadscore
	#safe
	if downloadflag==0:
		return 0
	#unknow
	if downloadscore==0:
		return -1
	#dangerous
	else:
		return 2