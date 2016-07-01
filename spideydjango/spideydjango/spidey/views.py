from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

class ScanNum(object):
	"""docstring for ScanNum"""
	def __init__(self, sumnum, last24num):
		super(ScanNum, self).__init__()
		self.sumnum = sumnum
		self.last24num = last24num

#function for view the index page
def index(request):
	return render_to_response('index.html',{'sumnum':'40000','last24num':'24'})

#function for get url scan result (ajax)
@csrf_exempt
def scanurl(request):
	surl = request.POST.get('url','')
	return HttpResponse(json.dumps({'dangerlevel':'2','lastscantime':'2016.06.27 16:54:12'}))

#function for get Derived Data file
@csrf_exempt
def deriveddata(request):
	level1 = request.POST.get('level1','')
	level2 = request.POST.get('level2','')
	keywordofurls = request.POST.get('keywordofurls','')

	print level1
	print level2
	print keywordofurls
 
	file_name = "deriveddata.txt"
	response = HttpResponse(readFile(file_name))
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