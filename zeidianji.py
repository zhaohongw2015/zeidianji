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
    account_name=raw_input("开心网用户名:")
    account_password=raw_input("开心网密码:")
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


    #没找到参数,说明登陆失败
    if(line.find(r'FlashVars')<0):
        #你的访问速度过快，或次数过多，请稍候按F5键刷新网页
        print "登陆失败,请检查config.ini中的用户名和密码"
        sys.exit(-1)

    #解析参数
    l=line.split(',')
    l1=l[1]
    param=l1[2:-1]  #remove ' at two ends
    print param
    #param='verify=13814301_1062_13814301_1241615280_1f83fcd2117fd3aca6bbe7da595cf4c0&wwwhost=www.kaixin001.com&roomid=8710&roomsnum=2&fuid=0'

    #取得主人id
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
    if seedid in seedid_blacklist: #黑名单上的不偷
        return False 
    if(info.find("已偷")>0):  #已偷完,已偷光
        return False
    if(info.find("可偷")>0):  #再过X小时可偷
        return False
    if(farm_info.find("爱心地")>0): #爱心地
        if(farm_info.find(hostname)>0):
            return True
        else:
            return False
    if(info.find("剩余")>0):
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
    print "下手..."           
    req = urllib2.Request(url=host+url)
    f = urllib2.urlopen(req)
    stat_all+=1
    #print "GET "+url
    #print f.msg
    #检查是否成功
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
    print "进入%s的花园..." % name
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



#[收菜篇]

#收自家园子的菜
hostname=havest(0,document)


#查看谁家的菜熟了
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
    print '今天没生意做'
else:
    print '共下手%d次,得手%d次,失手%d次。得手率：%d%%' % (stat_all,stat_succ,stat_fail,(stat_succ*100/stat_all))



#惦记篇
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


#所有种菜的人
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
        time.sleep(2)   #休息一下,避免"你的访问速度过快，或次数过多，请稍候按F5键刷新网页"
    try:
        j=json.loads(n)
    except:
        time.sleep(10) 
        login()

#不惦记主人的菜，唯护游戏可玩性    
nbs.pop('0')

#打印所有种菜的人
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
            cname=getTagText(farm,'name') #作物名
            crops=getTagText(farm,'crops')#成熟时间
            itime_begin=crops.find('距离收获：')
            if(itime_begin<0):
                continue
            itime_end=crops.find('<',itime_begin)
            t=crops[itime_begin+10:itime_end]
            #print t
            m = re.match(r"((?P<day>\d+)天)?((?P<hour>\d+)小时)?((?P<minu>\d+)分)?", t)
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
    #wd[(用户ID,田块号)]=(收获时间,作物名,用户名)

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
        print r'下一个目标:',
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
