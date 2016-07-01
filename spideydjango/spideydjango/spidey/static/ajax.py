from django.shortcuts import render_to_response

def scanurl(request):
	surl = request.POST.getlist()
	print surl
	return render_to_response('index.html',{'sumnum':'40000','last24num':'24'})

print 'aaa'