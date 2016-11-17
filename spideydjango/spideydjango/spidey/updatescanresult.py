# encoding: UTF-8
from spideydjango.spidey.models import  Scanresult
from spideydjango.spidey.models import  Safescanresult
from spideydjango.spidey.jinshan import isphish,isIncDangerDownload
from spideydjango.spidey.get360 import getscorefrom360
from spideydjango.spidey.StaticDetection import StaticDetection
import threading
import time

def scanurlnow(surl,model):
	if model=="add":
		try:
			obj=Safescanresult.objects.get(host=surl)
		except:
			try:
				obj=Scanresult.objects.get(host=surl)
			except:
				pass
			else:
				return
		else:
			return


	try:
		result = getscorefrom360(surl)
	except:
		return

	#if the url is unsafe
	if result[0]!=0:
		phish = isphish(surl)
		download = isIncDangerDownload(surl)
		staticdetection=StaticDetection(surl,'html')
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

class Updatescanresult(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while True:
			time.sleep(604800)
			allurls=Scanresult.objects.all()
			for i in allurls:
				print i.host
				scanurlnow(i.host,"update")