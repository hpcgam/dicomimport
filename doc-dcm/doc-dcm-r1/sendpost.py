# -*- coding: utf-8 -*-
import sys
import urllib,httplib

data = {"reg":"А\К пациента","doc_type":"Наименование док-та", \
        "url":"Собственно урл"}
params = urllib.urlencode(data)
#???headers = {"http-equiv": "Content-Type", " content": "text/html","charset":"utf8"}
headers = {"http-equiv": "Content-Type", "charset":"utf8"}
connection = httplib.HTTPConnection("mis.iood.ru/m0/pat/misc/attach")
try:
    connection.request("POST", "/", params)
    resp = connection.getresponse()
    if resp.status != 200:
        #print "Status %d %s : %s" % (resp.status, resp.reason, url)        # неверный ответ
        pass
    else:
        print "все Ок"
except Exception, e:
     print "Ошибка:", e.__class__,  e 
     #return False
     sys.exit(1)
    
print "response:",resp.status, "reas",resp.reason
dataa = resp.read()
print dataa
connection.close()
