from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Scanresult(models.Model):
	host=models.CharField(max_length=255,primary_key=True)
	staticdetection=models.IntegerField(null=False,default=-1)
	phish=models.IntegerField(blank=False,default=-1)
	download=models.IntegerField(blank=False,default=-1)
	fake=models.IntegerField(blank=False,default=-1)
	distort=models.IntegerField(blank=False,default=-1)
	trojan=models.IntegerField(blank=False,default=-1)
	totalscore=models.IntegerField(blank=False,default=-1)
	lastscantime=models.DateTimeField(auto_now=True)

class Safescanresult(models.Model):
	host=models.CharField(max_length=255,primary_key=True)
	lastscantime=models.DateTimeField(auto_now=True)