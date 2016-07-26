#!/usr/bin/python -u
import sys
import fileinput
import re
from urllib2 import urlopen, URLError

TSServiceURL = 'http://tracksysdev.lib.virginia.edu:8082/'

reobjthumb = re.compile("^/iiif/([^/]*):([0-9]*)/full/(\!?)([0-9]*),([0-9]*)/(.*)")
reobjother = re.compile("^/iiif/([^/]*):([0-9]*)/(.*)")

while 1:
    
    line = sys.stdin.readline()

    m = reobjthumb.match(line)
    if m and int(m.group(4)) < 201 and int(m.group(5)) < 201 :
        pid = m.group(1) + ':' + m.group(2)
        urlend = 'full' '/' + m.group(3) + m.group(4) + ',' + m.group(5) + '/' + m.group(6)
        perm = 'public'
    else:
        m = reobjother.match(line)
        if m:
            pid = m.group(1) + ':' + m.group(2)
            urlend = m.group(3)
            req = TSServiceURL + pid
            try:
                resp = urlopen(req,None,2)
                perm = resp.read().decode('ascii')
            except URLError, e:
                perm = 'public'
            except socket.timeout:
                perm = 'public'
        else:
            pid = 'unknown'
            urlend = ''
            perm = 'private'
            
    print('/iiif%s/%s/%s' %(perm[:3],pid,urlend) )
