from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from spideydjango.spidey.jinshan import isphish,isIncDangerDownload
from spideydjango.spidey.get360 import getscorefrom360
from spideydjango.spidey.StaticDetection import StaticDetection
from spideydjango.spidey.models import  Scanresult
from spideydjango.spidey.models import  Safescanresult
from spideydjango.spidey import updatescanresult
from spideydjango.spidey import crawler
import threading
import string
import json
import time
import os


t1 = updatescanresult.Updatescanresult()
t1.start()
t2 = crawler.Addscanresult()
t2.start()

class ScanNum(object):
	"""docstring for ScanNum"""
	def __init__(self, sumnum, last24num):
		super(ScanNum, self).__init__()
		self.sumnum = sumnum
		self.last24num = last24num

#function for view the index page
def index(request):
	sumnum=0
	last24num=0
	for i in Scanresult.objects.filter():
		sumnum+=1
	for i in Safescanresult.objects.filter():
		sumnum+=1
	timefrom=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()-86400))
	timeto=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
	for i in Scanresult.objects.filter(lastscantime__range=(timefrom,timeto)):
		last24num+=1
	for i in Safescanresult.objects.filter(lastscantime__range=(timefrom,timeto)):
		last24num+=1
	return render_to_response('index.html',{'sumnum':sumnum,'last24num':last24num})

#function for get url scan result (ajax) now
@csrf_exempt
def scanurlnow(request):
	surl = request.POST.get('url','')
	phish = isphish(surl)
	download = isIncDangerDownload(surl)
	result = getscorefrom360(surl)
	staticdetection=StaticDetection(surl,'html')

	#if the url is unsafe
	if result[0]!=0:
		try:
			obj=Scanresult.objects.get(host=surl)
		except:
			#not have data in database yet,insert data into table
			try:
				obj=Safescanresult.objects.get(host=surl)
				obj.delete()
			except:
				pass
			obj = Scanresult(host=surl, staticdetection=staticdetection,phish=phish,download=download,fake=result[1],distort=result[2],trojan=result[3],totalscore=result[0])
			obj.save()
		else:
			#have data in database,update data into table
			obj.staticdetection = staticdetection
			obj.phish=phish
			obj.download=download
			obj.fake=result[1]
			obj.distort=result[2]
			obj.trojan=result[3]
			obj.totalscore=result[0]
			obj.save()
			#Scanresult.objects.filter(host=surl).update(staticdetection=staticdetection,phish=phish,download=download,fake=result[1],distort=result[2],trojan=result[3],totalscore=result[0])
	else:
		try:
			obj=Safescanresult.objects.get(host=surl)
		except:
			#not have data in database yet,insert data into table
			try:
				obj=Scanresult.objects.get(host=surl)
				obj.delete()
			except:
				pass
			obj = Safescanresult(host=surl)
			obj.save()
		else:
			#have data in database,update data into table
			obj.save()
	return HttpResponse(json.dumps({'phish':phish,'download':download,'dangerlevel':result[0],'isfake':result[1],'isdistort':result[2],'istrojan':result[3],'staticdetection':staticdetection,'lastscantime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))}))

#function for get url scan result (ajax) fromdatabase
@csrf_exempt
def scanurlfromdatabase(request):
	surl = request.POST.get('url','')
	phish=-1
	download=-1
	dangerlevel=-1
	isfake=-1
	isdistort=-1
	istrojan=-1
	staticdetection=-1
	lastscantime="Not scaned before.Try scan it now"
	try:
		result=Scanresult.objects.get(host=surl)
		state="unsafe"
		phish=result.phish
		download=result.download
		dangerlevel=result.totalscore
		isfake=result.fake
		isdistort=result.distort
		istrojan=result.trojan
		staticdetection=result.staticdetection
		lastscantime=str(result.lastscantime)[:19]
	except:
		try:
			result=Safescanresult.objects.get(host=surl)
			state="safe"
			lastscantime=str(result.lastscantime)[:19]
		except:
			state="unsafe"
	
	return HttpResponse(json.dumps({'state':state,'phish':phish,'download':download,'dangerlevel':dangerlevel,'isfake':isfake,'isdistort':isdistort,'istrojan':istrojan,'staticdetection':staticdetection,'lastscantime':lastscantime}))

#function for get Derived Data file
@csrf_exempt
def deriveddata(request):
	score = request.POST.get('scoreofurls','')
	keyword = request.POST.get('keywordofurls','')
	scores=score.split(',')
	keywords=keyword.split(',')
	#print scores
	#print keywords

	#get data from database
	result=''
	if scores==['']:
		if keywords==['']:
			for i in Scanresult.objects.filter():
				result+=str(i.host)+" "+str(i.totalscore)+"\r\n"
			for i in Safescanresult.objects.filter():
				result+=str(i.host)+" 0\r\n"
		else:
			for keyword in keywords:
				for i in Scanresult.objects.filter(host__contains=keyword):
					result+=str(i.host)+" "+str(i.totalscore)+"\r\n"
				for i in Safescanresult.objects.filter(host__contains=keyword):
					result+=str(i.host)+" 0\r\n"
	else:
		if keywords==[]:
			for score in scores:
				if score=='0':
					for i in Safescanresult.objects.filter():
						result+=str(i.host)+" 0\r\n"
				else:
					for i in Scanresult.objects.filter(totalscore=int(score)):
						result+=str(i.host)+" "+str(i.totalscore)+"\r\n"
		else:
			for score in scores:
				for keyword in keywords:
					if score=='0':
						for i in Safescanresult.objects.filter(host__contains=keyword):
							result+=str(i.host)+" 0\r\n"
					else:
						for i in Scanresult.objects.filter(totalscore=int(score),host__contains=keyword):
							result+=str(i.host)+" "+str(i.totalscore)+"\r\n"
	#print result

	#export the file
	file_name = "deriveddata.txt"
	response = HttpResponse(result)
	response['Content-Type'] = 'application/octet-stream'
	response['Content-Disposition'] = 'attachment;file_name='+file_name
 
	return response

#function for transfer deriveddata file
def readFile(fn, buf_size=262144):
	f = open(fn, "rb")
	while True:
		c = f.read(buf_size)
		if c:
			yield c
		else:
			break
	f.close()