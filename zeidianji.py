# coding=gbk
####configuration begin####
import ConfigParser
import sys, os
         
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
####configuration end####
import urllib2
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)
host='http://www.kaixin001.com/'
#01 login
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
    if(line.find(r'FlashVars')>=0):
        break

#没找到参数,说明登陆失败
if(line.find(r'FlashVars')<0):
    print "登陆失败,请检查config.ini中的用户名和密码"
    sys.exit(-1)
    
#解析参数
l=line.split(',')
l1=l[1]
param=l1[2:-1]  #remove ' at two ends
print param
#param='verify=13814301_1062_13814301_1241615280_1f83fcd2117fd3aca6bbe7da595cf4c0&wwwhost=www.kaixin001.com&roomid=8710&roomsnum=2&fuid=0'

#03.2 split parameter
plist=param.split('&')
pdict={}
for p in plist:
	pair=p.split('=')
	pdict[pair[0]]=pair[1]

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




def isMature(info):
    if(info.find("已偷")>0):
        return False
    if(info.find("不能偷")>0):
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
            print fname,removeTag(crops)
            #havest
            url="/!house/!garden/havest.php?"
            url+=("verify=%s" % pdict['verify'])
            url+=("&fuid=%s" % uid)
            import random
            r=random.random()
            url+="&seedid=0"
            url+=("&farmnum=%s" % farmnum)
            if (isMature(crops)):
                print "试图收一下..."
                req = urllib2.Request(url=host+url)
                f = urllib2.urlopen(req)
                #print "GET "+url
                #print f.msg
                print f.read().decode('utf-8').encode('gbk')

#收自家园子的菜
havest(0,document)

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
friends=j['friend']
for friend in friends:
    uid=friend['uid']
    realname=friend['realname']
    print uid,realname
    document=getConf(uid)
    havest(uid,document)



