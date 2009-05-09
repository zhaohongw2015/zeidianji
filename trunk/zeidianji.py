# coding=gbk
####configuration begin####
import ConfigParser
import sys, os
import time         
pathname = os.path.dirname(sys.argv[0])        
full_path= os.path.abspath(pathname)
full_path_name=os.path.join(full_path,'config.ini')

config = ConfigParser.RawConfigParser()
config.read(full_path_name)

if(not config.has_section('ACCOUNT')):
    account_name=raw_input("�������û���:")
    account_password=raw_input("����������:")
    config.add_section('ACCOUNT')
    config.set('ACCOUNT', 'account_name', account_name)
    config.set('ACCOUNT', 'account_password', account_password)
    with open(full_path_name, 'wb') as configfile:
        config.write(configfile)
else:
    account_name = config.get('ACCOUNT', 'account_name')
    account_password = config.get('ACCOUNT', 'account_password')


if(config.has_section('GARDEN')):
    seedid_blacklist = config.get('GARDEN', 'seedid_blacklist')
    seedid_blacklist = seedid_blacklist.split(',')
else:
    seedid_blacklist=[]

    
####configuration end####
import urllib2
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)
host='http://www.kaixin001.com/'
param=''
pdict={}
global stat_all,stat_succ
stat_all=0
stat_succ=0

#01 login
def login():
    data='url=/home/&email=%s&password=%s' % (account_name,account_password)
    req = urllib2.Request(url='http://www.kaixin001.com/login/login.php', \
                            data=data)
    f = urllib2.urlopen(req)
    print "login..."
    assert 200==f.code

    req = urllib2.Request(url='http://www.kaixin001.com/!house/index.php')
    f = urllib2.urlopen(req)
    print "GET /!house/index.php"
    print f.msg
    assert 200==f.code
    
    #03.1 get parameter
    for line in f:
        #print line
        if(line.find(r'FlashVars')>=0):
            break


    #û�ҵ�����,˵����½ʧ��
    if(line.find(r'FlashVars')<0):
        #��ķ����ٶȹ��죬��������࣬���Ժ�F5��ˢ����ҳ
        print "��½ʧ��,����config.ini�е��û���������"
        sys.exit(-1)

    #��������
    l=line.split(',')
    l1=l[1]
    param=l1[2:-1]  #remove ' at two ends
    print param
    #param='verify=13814301_1062_13814301_1241615280_1f83fcd2117fd3aca6bbe7da595cf4c0&wwwhost=www.kaixin001.com&roomid=8710&roomsnum=2&fuid=0'

    #ȡ������id
    hostid=param[param.find('='):param.find('_')]

    #03.2 split parameter
    plist=param.split('&')
    pdict={}
    for p in plist:
            pair=p.split('=')
            pdict[pair[0]]=pair[1]
    return pdict

pdict=login()

#getconf function
#http://www.kaixin001.com/!house/!garden/getconf.php?verify=13814301_1062_13814301_1241613391_54fc24f1c895e2e23fd07e9ad4a4c734&fuid=1230242&r=0.06616138247773051
def getConf(uid):
    #print param
    url="/!house/!garden/getconf.php?"
    url+=("verify=%s" % pdict['verify'])
    url+=("&fuid=%s" % uid)
    import random
    r=random.random()
    url+=("&r=%s" % r)
    req = urllib2.Request(url=host+url)
    f = urllib2.urlopen(req)
    #print "GET "+url
    print f.msg
    document=f.read()
    #print f.read()
    return document


#04 get host's conf
#GET /!house/!garden/getconf.php?verify=13814301_1062_13814301_1241617242_a02655ab7ab200ed717c3c307b22c30a&fuid=0&r=0.034257106482982635 HTTP/1.1
url="/!house/!garden/getconf.php?"+param
req = urllib2.Request(url=host+url)
f = urllib2.urlopen(req)
print "GET "+url
print f.msg
document=f.read()
#print f.read().decode('utf-8').encode('gbk')



#parse host's conf
import xml.dom.minidom
def getTagText(root, tag):
    node = root.getElementsByTagName(tag)
    if(len(node)<=0):
        return ' '
    else:
        node=node[0]
    rc = ""
    for node in node.childNodes:
        if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
            rc = rc + node.data
    return rc.encode('gbk')



hostname=""
def isMature(info,farm_info,seedid):
    if seedid in seedid_blacklist: #�������ϵĲ�͵
        return False 
    if(info.find("��͵")>0):  #��͵��,��͵��
        return False
    if(info.find("��͵")>0):  #�ٹ�XСʱ��͵
        return False
    if(farm_info.find("���ĵ�")>0): #���ĵ�
        if(farm_info.find(hostname)>0):
            return True
        else:
            return False
    if(info.find("ʣ��")>0):
        return True
    else:
        return False

import re
def removeTag(xmlstr):
    regex = "<(.|\n)*?>"
    result = re.sub(regex,'',xmlstr)
    return result

def havest1farm(uid,farmnum):
    global stat_all,stat_succ
    url="/!house/!garden/havest.php?"
    url+=("verify=%s" % pdict['verify'])
    url+=("&fuid=%s" % uid)
    import random
    r=random.random()
    url+="&seedid=0"
    url+=("&farmnum=%s" % farmnum)
    print "����..."           
    req = urllib2.Request(url=host+url)
    f = urllib2.urlopen(req)
    stat_all+=1
    #print "GET "+url
    #print f.msg
    #����Ƿ�ɹ�
    info=f.read()
    dom = xml.dom.minidom.parseString(info)
    data=dom.getElementsByTagName('data')[0]
    ret=getTagText(data,'ret')
    if(ret.find('succ')>=0):
        stat_succ+=1
    print info.decode('utf-8').encode('gbk')

def getName(document):
    dom = xml.dom.minidom.parseString(document)
    ac=dom.getElementsByTagName('account')[0]
    name=getTagText(ac,'name')
    return name
    
    
                
def havest(uid,document):
    dom = xml.dom.minidom.parseString(document)
    ac=dom.getElementsByTagName('account')[0]
    name=getTagText(ac,'name')
    print "����%s�Ļ�԰..." % name
    farms=dom.getElementsByTagName('item')   
    for farm in farms:
        status = getTagText(farm,'status')
        cropsid = getTagText(farm,'cropsid')
        farmnum=getTagText(farm,'farmnum')
        #print farmnum
        if(1==int(status) and int(cropsid)>0):
            fname=getTagText(farm,'name')
            crops=getTagText(farm,'crops')
            farm_info=getTagText(farm,'farm')
            seedid=getTagText(farm,'seedid')
            print fname,removeTag(crops)
            #havest
            if (isMature(crops,farm_info,seedid)):
                havest1farm(uid,farmnum)
            
    return fname



#[�ղ�ƪ]

#���Լ�԰�ӵĲ�
hostname=havest(0,document)


#�鿴˭�ҵĲ�����
#GET /!house/!garden/getfriendmature.php?verify=13814301_1062_13814301_1241613391_54fc24f1c895e2e23fd07e9ad4a4c734&r=0.5315156443975866 HTTP/1.1
url="/!house/!garden/getfriendmature.php?"+param
import random
r=random.random()
url+=("&r=%s" % r)
req = urllib2.Request(url=host+url)
f = urllib2.urlopen(req)
#print f.read().decode('utf-8').encode('gbk')
#print f.read()

import json
m=f.read()
j=json.loads(m)
shares=j['share']
friends=j['friend']
global stat_all,stat_succ
stat_all=0
stat_succ=0
for friend in (shares+friends):
    uid=friend['uid']
    realname=friend['realname']
    print uid,realname
    document=getConf(uid)
    havest(uid,document)
stat_fail=stat_all-stat_succ
if 0==stat_all:
    print '����û������'
else:
    print '������%d��,����%d��,ʧ��%d�Ρ������ʣ�%d%%' % (stat_all,stat_succ,stat_fail,(stat_succ*100/stat_all))



#���ƪ
#POST http://www.kaixin001.com/house/garden/friend_ajax.php
#verify	13814301_1062_13814301_1241712870_736ebb3ad5a6f64f8f1564cad3887b63
#fuid	0
#r	99589709
def getNeighbour(uid):
    #print param
    url="/house/garden/friend_ajax.php"
    c=("verify=%s" % pdict['verify'])
    c+=("&fuid=%s" % uid)
    #Math.round((Math.random()) * 100000000)
    import random
    r=random.random()
    r=int(r*100000000)
    c+=("&r=%s" % r)
    req = urllib2.Request((host+url),c)
    f = urllib2.urlopen(req)
    #print "GET "+url
    print f.msg
    document=f.read()
    #print document
    return document


#�����ֲ˵���
n=getNeighbour(0)
import json
j=json.loads(n)
nbs={}
counter=0
while(not nbs.has_key(j['fuid'])):
    print j['fuid']
    nbs[j['fuid']]=j
    n=getNeighbour(j['nextuid'])
    counter=counter+1
    if(0== counter % 1):
        time.sleep(2)   #��Ϣһ��,����"��ķ����ٶȹ��죬��������࣬���Ժ�F5��ˢ����ҳ"
    try:
        j=json.loads(n)
    except:
        time.sleep(10) 
        login()

#��������˵Ĳˣ�Ψ����Ϸ������    
nbs.pop('0')

#��ӡ�����ֲ˵���
for k in nbs:
    print k,nbs[k]['frealname']
    

from datetime import timedelta
from datetime import datetime
def str2num(v):
    if( v is None):
        return 0
    else:
        return int(v)
  
import re
def getCroplist(document):
    dom = xml.dom.minidom.parseString(document)
    farms=dom.getElementsByTagName('item')
    croplist=[]
    for farm in farms:
        status = getTagText(farm,'status')
        cropsid = getTagText(farm,'cropsid')
        farmnum=getTagText(farm,'farmnum')
        if(1==int(status) and int(cropsid)>0):
            cname=getTagText(farm,'name') #������
            crops=getTagText(farm,'crops')#����ʱ��
            itime_begin=crops.find('�����ջ�')
            if(itime_begin<0):
                continue
            itime_end=crops.find('<',itime_begin)
            t=crops[itime_begin+10:itime_end]
            #print t
            m = re.match(r"((?P<day>\d+)��)?((?P<hour>\d+)Сʱ)?((?P<minu>\d+)��)?", t)
            dtdict=m.groupdict()
            day,hour,minu=dtdict['day'],dtdict['hour'],dtdict['minu']
            #print day,hour,minu
            (day,hour,minu)=[str2num(x) for x in (day,hour,minu)]
            td=timedelta(days=day,hours=hour,minutes=minu)
            nw=datetime.now()
            th=nw+td # time of havest
            #print nw,td,th
            croplist.append((th,cname,farmnum))
    return croplist


wl=[]   #watch farm list


for k in nbs:
    document=getConf(k)
    croplist=getCroplist(document)
    for crop in croplist:
        wl.append((crop[0],crop[1],crop[2],nbs[k]['frealname'],nbs[k]['fuid']))

wl.sort()
for item in wl:
    print item[0],item[1],item[2],item[3],item[4]

import shelve    
d = shelve.open(r'c:\helloworld\vars')
d['wl']=wl
d.close()



import shelve
d = shelve.open(r'c:\helloworld\vars')
wl=d['wl']
d.close()


dol=[]#doing list
wd={}#watch dictionary
for k in wl:
    th,cname,farmnum,frealname,fuid=k
    wd[(fuid,farmnum)]=(th,cname,frealname)
    #wd[(�û�ID,����)]=(�ջ�ʱ��,������,�û���)

def getCheckingList(wd,deltaSec):
    cl=[]
    wlsorted=sorted(wd.items(),key=lambda d:d[1][0])
    for k in wlsorted:
        th,cname,farmnum,frealname,fuid=k[1][0],k[1][1],k[0][1],k[1][2],k[0][0]
        tnow=datetime.now()
        d = timedelta(seconds=deltaSec)#test ,should be 60
        if(th-tnow<d):
            print th,cname,farmnum,frealname,fuid
            cl.append((th,cname,farmnum,frealname,fuid))
        else:
            break
    print 'getChecklingList:%d' % len(cl)
    return cl

def checking(cl):
    cs=set()#checking set
    for k in cl:
        th,cname,farmnum,frealname,fuid=k
        cs.add(fuid)
    for fuid in cs:
        document=getConf(fuid)
        croplist=getCroplist(document)
        frealname=getName(document)
        print frealname
        for crop in croplist:
            th,cname,farmnum,frealname,fuid=crop[0],crop[1],crop[2],frealname,fuid
            wd[(fuid,farmnum)]=(th,cname,frealname)
            #print th,cname,farmnum,frealname,fuid


import threading
from datetime import timedelta
from datetime import datetime

def dodoing():
    print 'dodoing()'
    global dol
    print 'dodoing'
    print 'len of dol=%d' % len(dol)
    login()
    for k in dol:
        th,cname,farmnum,frealname,fuid=k
        print 'next target:',
        print th,frealname,cname
        havest1farm(fuid,farmnum)
        wd.pop((fuid,farmnum))
        
def doing():
    print 'doing()'
    global dol
    if(len(dol)>0):
        dodoing()
    td.run()
        
    
 
def docheck():
    print 'docheck()'
    global dol
    print 'docheck'
    cl=getCheckingList(wd,60)
    if len(cl)>0:
        th,cname,farmnum,frealname,fuid=cl[0]
        print r'��һ��Ŀ��:',
        print th,frealname,cname
        checking(cl)
        dol=getCheckingList(wd,5)
        print 'docheck:len(dol)=%d' % len(dol)


      

def check():
    print 'check()'
    docheck() 
    tc.run()

    
td = threading.Timer(5, doing)
tc = threading.Timer(10, check)
print 'tc.start'
tc.start()
print 'td.start'
td.start()
