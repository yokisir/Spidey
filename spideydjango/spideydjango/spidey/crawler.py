#coding=utf-8  

'''
catch data from anquan & Bing & 360
'''
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
from spideydjango.spidey.models import  Scanresult
from spideydjango.spidey.updatescanresult import scanurlnow
from urlparse import *
import threading
import urllib2
import urllib
import re
import os
import time
import sys

TIMEOUT=20
#change the default encode model
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


#class for parse html from anquan.org
class AnquanParser(HTMLParser):
    flag=False

    def __init__(self):
        HTMLParser.__init__(self)
        self.urls=[]
 
    def handle_starttag(self,tag,attrs):
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    #print variable+" "+value
                    if variable == "href" and value[:19] == "//www.anquan.org/s/":
                        self.flag=True

    def handle_data(self,data):
        if self.flag==True:
            self.urls.append("http://"+data)
            self.flag=False

#class for parse html from baidu.com
class BaiduParser(HTMLParser):
    flag=False

    def __init__(self):
        HTMLParser.__init__(self)
        self.keywords=[]
 
    def handle_starttag(self,tag,attrs):
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    #print variable+" "+value
                    if variable == "class" and value == "list-title":
                        self.flag=True

    def handle_data(self,data):
        if self.flag==True:
            self.keywords.append(data)
            self.flag=False

#class for parse html from baidu find result
class BingParser(HTMLParser):
    flag=False

    def __init__(self):
        HTMLParser.__init__(self)
        self.urls=[]
 
    def handle_starttag(self,tag,attrs):
        if tag == "li":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    #print variable+" "+value
                    if variable == "class" and value == "b_algo":
                        self.flag=True
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    if variable == "href" and self.flag == True:
                        self.flag=False
                        self.urls.append(value)

#class for parse html from 360.cn
class A360Parser(HTMLParser):
    flag=0

    def __init__(self):
        HTMLParser.__init__(self)
        self.urls=[]
 
    def handle_starttag(self,tag,attrs):
        if tag == "div":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    #print variable+" "+value
                    if variable == "class" and value == "ld-list-g":
                        self.flag=1
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                if self.flag==1:
                    self.flag=2
        if tag == "h3":
            self.flag=0

    def handle_data(self,data):
        if self.flag==2:
            self.urls.append("http://"+data)
            self.flag=1

#class for parse html from baidu jump link
class JumpParser(HTMLParser):
    flag=False

    def __init__(self):
        HTMLParser.__init__(self)
        self.url=[]
 
    def handle_starttag(self,tag,attrs):
        if tag == "meta":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value)  in attrs:
                    #print variable+" "+value
                    if variable == "http-equiv" and value == "refresh":
                        self.flag=True
                    if variable == "content" and self.flag == True:
                        self.url=value[7:-1]
                        self.flag=False

#function for analysis domain name from urls
def analysisdomain(urls):
    topHostPostfix = (
    '.com','.cn','.la','.io','.co','.info','.net','.org','.me','.mobi',
    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn','edu.cn','gov.cn'
    '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
    '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
    '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co',
    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
    '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
    '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
    '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
    '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk")

    regx = r'[^\.]+('+'|'.join([h.replace('.',r'\.') for h in topHostPostfix])+')$'
    pattern = re.compile(regx,re.IGNORECASE)
    hosts=[]
    for url in urls:
        #print url
        parts = urlparse(url)
        host = parts.netloc
        m = pattern.search(host)
        res =  m.group() if m else host
        if res:
            hosts.append(res)
    return hosts

#function for get the host from the baidu jump web
def getFindurls(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    request = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(request)
    page = response.read().decode("utf8")

    hp = FindParser()
    hp.feed(page)
    hp.close()

    urls=hp.urls
    #print urls
    return hp.urls

#function for get the host from the baidu jump web
def getJumpurls(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    request = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(request)
    page = response.read()

    '''
    f=open('test.html','w')
    f.write(page)
    f.close()
    '''

    hp = JumpParser()
    try:
        hp.feed(page)
        hp.close()
    except:
        pass

    #print hp.url
    return hp.url

#function for get url from anquan.org
def catchanquan():
    anquan = 'https://jubao.anquan.org/exposure'
    hosts=[]
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    try:
        request = urllib2.Request(anquan,headers=headers)
        response = urllib2.urlopen(request,timeout=TIMEOUT)
        page = response.read()
    except:
        print "* crawler.py:catchanquan():TIMEOUT"
        return hosts
    #print page

    hp = AnquanParser()
    try:
        hp.feed(page)
        hp.close()
    except:
        pass

    #print hp.urls
    hosts=analysisdomain(hp.urls)

    #print hosts
    return hosts

#function for get hot keywords from baidu.com
def catchbaidu():
    keywords=[]
    baidus = ['http://top.baidu.com/buzz?b=342&c=513&fr=topbuzz_b42_c513','http://top.baidu.com/buzz?b=344&c=513&fr=topbuzz_b342_c513','http://top.baidu.com/buzz?b=11&c=513&fr=topbuzz_b344_c513']
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    for baidu in baidus:
        try:
            request = urllib2.Request(baidu,headers=headers)
            response = urllib2.urlopen(request,timeout=TIMEOUT)
            page = response.read().decode("gbk")
        except:
            print "* crawler.py:catchbaidu():TIMEOUT"
            continue
        #print page

        hp = BaiduParser()
        try:
            hp.feed(page)
            hp.close()
        except:
            pass

        keywords+=hp.keywords
        #for keyword in hp.keywords:
        #    print keyword
    return keywords

    '''
    urls=[]
    hosts=[]
    for keywordurl in hp.keywordurls:
        urls+=getFindurls(keywordurl)
    #print urls
    tmpurls=[]
    for url in urls:
        print url
        tmpurls.append(getJumpurls(url))
    print tmpurls
    #print hosts
    #hosts=analysisdomain(hp.urls)
    '''

#function for get urls from bing.com
def catchbing(keyword):
    #keywords=["长征五号首发成功"]
    urls=[]
    print keyword
    p=""
    for pagenum in range(0,64):
        bing="http://cn.bing.com/search?q="+urllib.quote(str(keyword))+"&go=%e6%8f%90%e4%ba%a4&first="+p+"1&FORM=PERE"
        p=str(pagenum+1)
        #print bing
        headers = {
           'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
        }
        request = urllib2.Request(bing,headers=headers)
        try:
            response = urllib2.urlopen(request,timeout=TIMEOUT)
            page = response.read()
        except:
            print "* crawler.py:catchbing():TIMEOUT"
            continue
        '''
        f=open('test.html','w')
        f.write(page)
        f.close()
        '''

        hp = BingParser()
        try:
            hp.feed(page)
            hp.close()
        except:
            pass

         #print hp.urls
        urls+=hp.urls

    hosts=[]
    hosts=analysisdomain(urls)
    #print hosts
    return hosts

#function for get urls from webscan.360.cn
def catch360():
    url360="http://webscan.360.cn/url"
    urls=[]
    headers = {
       'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0',
    }
    try:
        request = urllib2.Request(url360,headers=headers)
        response = urllib2.urlopen(request,timeout=TIMEOUT)
        page = response.read()
    except:
        print "* crawler.py:catch360():TIMEOUT"
        return urls
    '''
    f=open('test.html','w')
    f.write(page)
    f.close()
    '''

    hp = A360Parser()
    try:
        hp.feed(page)
        hp.close()
    except:
        pass

    #print hp.urls
    urls=hp.urls

    hosts=[]
    hosts=analysisdomain(urls)
    #print hosts
    return hosts

#class for create a thread to add scan result
class Addscanresult(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            hosts=catchanquan()+catch360()
            for host in hosts:
                print host
                scanurlnow(host,"add")
            keywords=catchbaidu()
            for keyword in keywords:
                hosts=catchbing(keyword)
                hosts = list(set(hosts))
                for host in hosts:
                    print host
                    scanurlnow(host,"add")
            time.sleep(60)