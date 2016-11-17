#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# User:Zhuyawei
# 2016-8-30 08:54
# Use for web Static Detection
# Reference resources:基于分类算法的恶意网页检测技术研究_王维光
# Reference resources:基于植入特征的网页恶意代码检测_黄建军
# Reference resources:基于内容的网页恶意代码检测的研究与实现_魏为
# Reference resources:Web环境下脚本攻击检测与防御研究_黎满
# Reference resources:Evernote 静态检测-分类

from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import re
import os
import math
import string
import urllib2

TIMEOUT=12

#class for parse html
class MyHTMLParser(HTMLParser):
	flag_iframe=True
	flag_script=True
	readscript=False
	count_html=0
	count_head=0
	count_title=0
	count_body=0
	notpair_iframe=0
	notpair_script=0
	len_script=0
	insidescript=[]

	def __init__(self):
		HTMLParser.__init__(self)
		self.scriptlinks = []
		self.iframelinks = []
 
	def handle_starttag(self,tag,attrs):
		if tag== "html":
			self.count_html=self.count_html+1;
		if tag== "head":
			self.count_head=self.count_head+1;
		if tag== "title":
			self.count_title=self.count_title+1;
		if tag== "body":
			self.count_body=self.count_body+1;
		if tag == "iframe":
			self.flag_iframe=False
			if len(attrs) == 0:
				pass
			else:
				for (variable, value)  in attrs:
					if variable == "src":
						self.iframelinks.append(value)
		if tag == "script":
			self.readscript=True
			self.flag_script=False
			if len(attrs) == 0:
				pass
			else:
				for (variable, value)  in attrs:
					if variable == "src":
						self.scriptlinks.append(value)

	def handle_endtag(self,tag):
		if tag == 'iframe':
			if self.flag_iframe!=False:
				self.notpair_iframe+=1
			self.flag_iframe=True
		if tag == 'script':
			self.readscript=False
			if self.flag_script!=False:
				self.notpair_script+=1
			self.flag_script=True
		if tag == 'html':
			if self.flag_iframe==False:
				self.notpair_iframe+=1
			if self.flag_script==False:
				self.notpair_script+=1

	def handle_data(self,data):  
		if self.readscript:  
			self.insidescript.append(data)
			self.len_script+=len(data)

#function for extract the url from link
def Geturl(s):
	keyword=u'href\s*?=[\'\"]?((http|ftp|https):\/\/)?(\w+\.){1,}((\w)|(\/\w)|(\.\w))+[^>]*'
	return re.search(keyword,s,re.I|re.M).group()

#function for calculate shannon ent
def calcShannonEnt(dataSet):
 	numEntries = len(dataSet)
 	labelCounts = {}
 	for featVec in dataSet:
 		currentLabel = featVec[-1]
 		if currentLabel not in labelCounts.keys(): 
 			labelCounts[currentLabel] = 0
 		labelCounts[currentLabel] += 1
 	shannonEnt = 0.0
 	for key in labelCounts:
 		prob = float(labelCounts[key])/numEntries
 		shannonEnt -= prob*math.log(prob, 2)
 	return shannonEnt

#function for extract darkchain
def DarkChainDetection(s):
	#display the keywords
	#keyword1 is for hidden link
	keyword1=u'<[^>!]*((width\s*?=\s*?0)|(visibility:\s*?hidden)|(display:\s*?none)|(style\s*?=\s*?"hidden")|(top\s*?-[0-9]{3,}\s*?px)|(left\s*?:\s*?-[0-9]{3,}\s*?px))[^>]*>(\s*?<a\s*?href\s*?=[\'\"]?((http|ftp|https):\/\/)?(\w+\.){1,}((\w)|(\/\w)|(\.\w))+[^>]*>)+'
	#keyword2 is for unnormal position link
	keyword2=u'<[^>!]*((top\s*?:\s*?-[0-9]{3,}\s*?px)|(left\s*?:\s*?-[0-9]{3,}\s*?px))[^>]*>(\s*?<a\s*?href\s*?=[\'\"]?((http|ftp|https):\/\/)?(\w+\.){1,}((\w)|(\/\w)|(\.\w))+[^>]*>)+'
	#keyword3 is for unnormal font-size link
	keyword3=u'<a\s*?href\s*?=[\'\"]?((http|ftp|https):\/\/)?(\w+\.){1,}((\w))+\s*?[^>]*?font-size\s*?:\s*?1px[^>]*>'
	#keyword4 is for Marquee
	keyword4=u'<[^>!]*(MARQUEE|[Mm]arquee)[^>!]*>([^<]*?<a\s*?href\s*?=[\'\"]?((http|ftp|https):\/\/)?(\w+\.){1,}((\w)|(\/\w)|(\.\w))+[^>]*>)+'

	#judge and print the result
	grade=0
	index=0
	matchObj=[]
	DCDweight=[0.4,0.4,0.5,0.3]

	matchObj.append(re.findall(keyword1,s,re.I|re.M))
	matchObj.append(re.findall(keyword2,s,re.I|re.M))
	matchObj.append(re.findall(keyword3,s,re.I|re.M))
	matchObj.append(re.findall(keyword4,s,re.I|re.M))
	for i in matchObj:
		grade+=len(i)*DCDweight[index]
		index+=1

	#print("DarkChainDetection:"+str(grade))
	return grade

#function for extract jump feature
def JumpFeatureDetection(s):
	#display the keywords
	#keyword1 is for invisible iframe or frame
	keyword1=u'<\s*(iframe|frame)[^>!]*((width\s*?=\s*?0)|(width\s*?=\s*?1)|(height\s*?=\s*?0)|(display:\s*?none)|(style\s*?=\s*?"hidden")|(top\s*?:\s*?-[0-9]{3,}\s*?px)|(left\s*?:\s*?-[0-9]{3,}\s*?px))[^>]*>'
	#keyword2 is for Absolute position div
	keyword2=u'<\s*(div)[^>!]*((top\s*?:\s*?-[0-9]{3,}\s*?px)|(left\s*?:\s*?-[0-9]{3,}\s*?px))[^>]*>'

	#judge and print the result
	grade=0
	index=0
	matchObj=[]
	JFDweight=[0.8,0.2]

	matchObj.append(re.findall(keyword1,s,re.I|re.M))
	matchObj.append(re.findall(keyword2,s,re.I|re.M))
	for i in matchObj:
		grade+=len(i)*JFDweight[index]
		index+=1

	#print("JumpFeatureDetection:"+str(grade))
	return grade

#function for extract Environmantal feature
def EnvironmentalFeatureDetection(s):
	#display the keywords
	#keyword1 is for Shellcode
	#keyword1=u'(.{2,4})[0-9A-Fa-f]{4}((.{2,4})[0-9A-Fa-f]{4}){15,}(.{2,4})([0-9A-Fa-f]{4}(.{2,4}))+'
	#keyword=u'(?:(?:%u|%x|\/u|\/x)+[a-fA-F0-9]{2,4}){15,}'
	keyword=u'(?:(?:.{2})[a-fA-F0-9]{2,4}){15,}'
	keyword1=re.compile(keyword)
	#keyword2 is for overlong string
	keyword2=u'[0-9A-Za-z]{255,}'

	#judge and print the result
	grade=0
	index=0
	matchObj=[]
	len_string=0
	EFDShannonthreshold=3.0
	EFDOverlongthreshold=255
	EFDRatiothreshold=0.3

	matchObj.append(keyword1.findall(s,re.I|re.M))
	matchObj.append(re.findall(keyword2,s,re.I|re.M))
	EFDweight=[0.8,0.8,0.3,0.9]

	for i in matchObj:
		if i==[]:
			continue
		#print(i)
		grade+=len(i)*EFDweight[index]
		index+=1
		for j in i:
			#print("calcShannonEnt:"+str(calcShannonEnt(j)))
			if calcShannonEnt(j)>EFDShannonthreshold:
				grade+=EFDweight[2]
			len_string+=len(j)
			#print("len(j):"+str(len(j)))

	#print("len_string/len(s):"+str(len_string/len(s)))
	if len_string/len(s)>EFDRatiothreshold:
		grade+=EFDweight[3]

	#print("-EnvironmentalFeatureDetection:"+str(grade))
	return grade

#function for extract attack feature
def AttackFeatureDetection(s,lens):
	#display the keywords
	#keyword1 is for ActiveXObject()、createElement()、createObject()、shellExecute()
	keyword1=u'([Aa]CtiveXObject\()+|([Cc]reateElement\()+|([Cc]reateObject\()+|(shellExecute\()+'
	#keyword2 is for object、Shellcode、heapspray、payload、downloader、victim
	keyword2=u'(object)+|(Shellcode)+|(heapspray)+|(payload)+|(downloader)+|(victim)+'
	#keyword3 is for .exe
	keyword3=u'(\.exe)+'

	#judge and print the result
	grade=0
	index=0
	matchObj=[]
	AFDweight=[0.2,0.2,0.5]

	matchObj.append(re.findall(keyword1,s,re.I|re.M))
	matchObj.append(re.findall(keyword2,s,re.I|re.M))
	matchObj.append(re.findall(keyword3,s,re.I|re.M))
	for i in matchObj:
		grade+=AFDweight[index]*len(i)*16/lens
		index+=1

	#print("AttackFeatureDetection:"+str(grade))
	return grade

#function for extract confusion feature
def ConfusionFeatureDetection(s,lens):
	#display the keywords
	#keyword1 is for eval()、document.write()、escape()、fromCharCode()、charCodeAt()、split()、replace()、substr()、slice()、indexOf()、strcomp()
	keyword1=u'(eval\()+|([Dd]ocument\.write\()+|(escape\()+|(fromCharCode\()+|(charCodeAt\()+|(split\()+|(replace\()+|(substr\()+|(slice\()+|(indexOf\()+|(strcomp\()+'
	#keyword2 is for decode、encode、Shellcode、heapspray、payload、downloader、victim、JScript.Encode、Scripting.encoder、EncodeScriptFile()、window.exeScript()
	keyword2=u'(decode)+|(encode)+|(heapspray)+|(payload)+|(downloader)+|(victim)+|(JScript\.Encode)+|(Scripting\.encoder)+|(EncodeScriptFile\()+|(window\.execScript\()+'
	#keyword3 is for =、+
	#keyword3=u'(=)+|(\+)+'

	#judge and print the result
	grade=0
	index=0
	matchObj=[]
	CFDShannonthreshold=1.5
	CFDthresholds=[1,1,15]
	CFDweight=[0.3,0.8,1.0,0]

	#print("ShannonEnt of s:"+str(calcShannonEnt(s)))
	if calcShannonEnt(s)>CFDShannonthreshold:
		grade+=CFDweight[index]
	index+=1

	matchObj.append(re.findall(keyword1,s,re.I|re.M))
	matchObj.append(re.findall(keyword2,s,re.I|re.M))
	#matchObj.append(re.findall(keyword3,s,re.I|re.M))
	for i in matchObj:
		if len(i)>CFDthresholds[index-1]:
			grade+=CFDweight[index]*len(i)*1024/lens
		index+=1

	#print("ConfusionFeatureDetection:"+str(grade))
	return grade

#function for extract other feature
def OtherFeatureDetection(s,host):
	#count the num of suffix name wrong
	count_scriptsufwrong=0
	#count the num of different url from other web
	count_iframedifurl=0

	#keyword1 is for extract suffix name of script tag
	keyword1=u'\.\w{1,3}\Z'
	#keyword2 is for extrace different url from other web
	keyword2=u'('+host+')+'

	#prase html file
	grade=0
	index=0
	OFDRatiothreshold=0.5
	OFDweight=[1.0,1.0,0.6,1.0,0.5]

	hp = MyHTMLParser()
	try:
		hp.feed(s)
		hp.close()
	except:
		pass

	if (hp.count_html>1) or (hp.count_head>1) or (hp.count_title>1) or (hp.count_body>1):
		#print("hp.count_html:"+str(hp.count_html))
		#print("hp.count_head:"+str(hp.count_head))
		#print("hp.count_title:"+str(hp.count_title))
		#print("hp.count_body:"+str(hp.count_body))
		grade+=OFDweight[index]
	index+=1
	if (hp.notpair_iframe>=1) or (hp.notpair_script>=1):
		#print("hp.notpair_iframe:"+str(hp.notpair_iframe))
		#print("hp.notpair_script:"+str(hp.notpair_script))
		grade+=OFDweight[index]
	index+=1
	#print("hp.scriptlinks:"+str(hp.scriptlinks))
	#print("hp.iframelinks:"+str(hp.iframelinks))
	for i in hp.scriptlinks:
		matchObj=re.search(keyword1,i,re.I|re.M)
		if matchObj==None:
			continue
		if matchObj.group()!='.js':
			count_scriptsufwrong+=1
	count_iframedifurl=len(hp.iframelinks)
	for i in hp.iframelinks:
		matchObj=re.search(keyword2,i,re.I|re.M)
		if matchObj!=None:
			count_iframedifurl-=1

	#print("count_scriptsufwrong:"+str(count_scriptsufwrong))
	if count_scriptsufwrong>=1:
		grade+=OFDweight[index]
	index+=1
	#print("count_iframedifurl:"+str(count_iframedifurl))
	if count_iframedifurl>=1:
		grade+=OFDweight[index]
	index+=1
	#print("hp.len_script:"+str(hp.len_script))
	#print(hp.len_script/len(s))
	if hp.len_script/len(s)>OFDRatiothreshold:
		grade+=OFDweight[index]

	#call EnvironmentalFeatureDetection(s)
	Envgrade=0
	for i in hp.insidescript:
		Envgrade+=EnvironmentalFeatureDetection(i)
	#print("EnvironmentalFeatureDetection:"+str(Envgrade))

	#print("OtherFeatureDetection:"+str(grade))
	return grade

def StaticDetection(scanurl,ftype):
	#get the content of the web and extract the link of download
	host=scanurl
	if scanurl[:4]!='http' and scanurl[:2]!="//":
		scanurl=r'http://'+scanurl
	headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
	}
	try:
		request = urllib2.Request(scanurl,headers=headers)
		response = urllib2.urlopen(request,timeout=TIMEOUT)
		s=response.read()
	except:
		print '* StaticDetection.py:Network Error during scan '+str(scanurl)
		if ftype=="html":
			return -1
		else:
			return 0

	jsscore=[]
	jsnum=0
	totaljsscore=0
	tmpscore=0
	if ftype=="html":
		soup=BeautifulSoup(s,'html.parser')
		#do the static detection for javacript in this web
		jsurls=soup.findAll('script')
		for link in jsurls:
			tmp_url=link.get('src')
			#print tmp_url
			if tmp_url=="" or tmp_url==None or tmp_url[:1]=='#' or tmp_url[:11]=='javascript:' or tmp_url[:7]=='mailto:' or tmp_url[-4:]=='html' or tmp_url[-3:]=='htm':
				continue
			if tmp_url[:4]!="http" and tmp_url[:3]!="www" and tmp_url[:2]!="//":
				tmp_url=scanurl+'/'+tmp_url
			tmpscore=StaticDetection(tmp_url,'js')
			if tmpscore!=-1:
				jsnum+=1
				jsscore.append(tmpscore**3)
		if jsnum>=2:
			totaljsscore+=max(jsscore)
			jsscore.remove(max(jsscore))
			totaljsscore+=max(jsscore)
			jsscore.remove(max(jsscore))
			jsnum=2
		elif jsnum==1:
			totaljsscore=jsscore[0]


	'''
	#open the weight file of each item
	weightfile=open("weight.txt","rt")
	weightstring=weightfile.readline()
	DCDweight=weightstring.split(',')
	weightstring=weightfile.readline()
	JFDweight=weightstring.split(',')
	weightstring=weightfile.readline()
	EFDweight=weightstring.split(',')
	weightstring=weightfile.readline()
	AFDweight=weightstring.split(',')
	weightstring=weightfile.readline()
	CFDweight=weightstring.split(',')
	weightstring=weightfile.readline()
	OFDweight=weightstring.split(',')
	weightfile.close()
	'''

	#Calculate the grade of the web
	totalgrade=0
	lens=len(s)
	if lens==0:
		return -1
	totalgrade=DarkChainDetection(s)+JumpFeatureDetection(s)
	if ftype == 'js' or ftype == 'html':
		#totalgrade+=EnvironmentalFeatureDetection(s)+AttackFeatureDetection(s)+ConfusionFeatureDetection(s)
		totalgrade+=AttackFeatureDetection(s,lens)+ConfusionFeatureDetection(s,lens)
	if ftype == 'html':
		totalgrade+=OtherFeatureDetection(s,host)

	#write the weight back
	'''
	for i in range(0,len(DCDweight)):
		DCDweight[i]=int(DCDweight[i])
	weightstring=str(DCDweight)[1:-1]+'\n'
	for i in range(0,len(JFDweight)):
		JFDweight[i]=int(JFDweight[i])
	weightstring+=str(JFDweight)[1:-1]+'\n'
	for i in range(0,len(EFDweight)):
		EFDweight[i]=int(EFDweight[i])
	weightstring+=str(EFDweight)[1:-1]+'\n'
	for i in range(0,len(AFDweight)):
		AFDweight[i]=int(AFDweight[i])
	weightstring+=str(AFDweight)[1:-1]+'\n'
	for i in range(0,len(CFDweight)):
		CFDweight[i]=int(CFDweight[i])
	weightstring+=str(CFDweight)[1:-1]+'\n'
	for i in range(0,len(OFDweight)):
		OFDweight[i]=int(OFDweight[i])
	weightstring+=str(OFDweight)[1:-1]

	weightfile=open("weight.txt","w")
	weightfile.write(weightstring)
	weightfile.close()
	'''

	if ftype == "js":
		return totalgrade
	if jsnum>0:
			totalgrade=(totalgrade+(totaljsscore)/jsnum)
	#print totalgrade
	if totalgrade<4:
		return 0
	elif totalgrade<10:
		return 1
	else:
		return 2