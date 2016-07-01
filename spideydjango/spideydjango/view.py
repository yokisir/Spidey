#from django.http import HttpResponse
from django.shortcuts import render_to_response

class ScanNum(object):
	"""docstring for ScanNum"""
	def __init__(self, sumnum, last24num):
		super(ScanNum, self).__init__()
		self.sumnum = sumnum
		self.last24num = last24num

def index(request):
	#return HttpResponse('Hello,Django!')
	return render_to_response('index.html',{'sumnum':'40000','last24num':'24'})