#coding=utf-8
import base64
import time
import md5
import urllib2
import json
from bs4 import BeautifulSoup

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
	response = urllib2.urlopen(request)
	page=json.load(response)
	#print page['phish']
	phish = page['phish']
	if phish==1 or phish==2:
		phish=(phish)%2+1
	return phish

#function for use jinshan API to judge whether it have vicious download link
def isdownload(scanurl):
	#the paraments for function
	q=base64.urlsafe_b64encode(scanurl)
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
	request = urllib2.Request(phishurl)
	response = urllib2.urlopen(request)
	page=json.load(response)
	print page['down_type']
	return page['down_type']

#function for use isdownload() to judge whether it include dangerous download link
def isIncDangerDownload(scanurl):
	#get the content of the web and extract the link of download
	content=urllib2.urlopen(scanurl).read()
	soup=BeautifulSoup(content)

	downloadscore=0
	downloadflag=0
	#judge all a links from the scanurl
	downloadurls=soup.findAll('a')
	#downloadurls.append(soup.findAll('script'))
	for link in downloadurls:
		tmp_url=link.get('href')
		if tmp_url=='':
			continue
		if tmp_url[:4]!='http':
			tmp_url=scanurl+tmp_url
		score=isdownload(tmp_url)
		if score!=2:
			downloadflag=1
			if score==3:
				downloadscore+=1

	return downloadflag