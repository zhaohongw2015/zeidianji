# coding=gbk
####configuration begin####
account_name="fangjiansoft@gmail.com"
account_password="1234567"
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

l=line.split(',')
l1=l[1]
param=l1[2:-1]  #remove ' at two ends
print param

#04 GET /!house/!garden/getconf.php?
url="/!house/!garden/getconf.php?"+param
req = urllib2.Request(url=host+url)
f = urllib2.urlopen(req)
print "GET "+url
print f.msg
#print f.read().decode('utf-8').encode('gbk')

#parse host's conf
document=f.read()
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


dom = xml.dom.minidom.parseString(document)
ac=dom.getElementsByTagName('account')[0]
name=getTagText(ac,'name')
print "进入主人%s的花园..." % name

def isMature(info):
    if(info.find("剩余")>0):
        return True
    else:
        return False
    

farms=dom.getElementsByTagName('item')
for farm in farms:
    status = getTagText(farm,'status')
    cropsid = getTagText(farm,'cropsid')
    farmnum=getTagText(farm,'farmnum')
    #print farmnum
    if(1==int(status) and int(cropsid)>0):
        fname=getTagText(farm,'name')
        crops=getTagText(farm,'crops')
        print fname,crops
        #havest
        url="/!house/!garden/havest.php?"+param
        import random
        r=random.random()
        url+=("&r=%s" % r)
        url+="&seedid=0"
        url+=("&farmnum=%s" % farmnum)
        if (isMature(crops)):
            print "试图收一下..."
            req = urllib2.Request(url=host+url)
            f = urllib2.urlopen(req)
            #print "GET "+url
            #print f.msg
            print f.read().decode('utf-8').encode('gbk')

