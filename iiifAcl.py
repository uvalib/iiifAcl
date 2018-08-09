#!/usr/bin/python -u
import sys
import fileinput
import re
import socket
from urllib2 import urlopen, URLError

# DNS lookups intermittently hang for ~5 seconds, affecting urlopen().
# To mitigate, we look up the IP address at invocation, and use it forever.
# Since Apache invokes this script at startup and keeps it open indefinitely,
# if the IP address for this server changes, Apache will need to be restarted.

TSServer = 'rightsws.lib.virginia.edu'
TSIPAddr = socket.gethostbyname(TSServer)
TSServiceURL = 'http://' + TSIPAddr + ':8089/'

reobjthumb = re.compile("^/iiif/([^/]*):([0-9]*)/full/(\!?)([0-9]*),([0-9]*)/(.*)")
reobjother = re.compile("^/iiif/([^/]*):([0-9]*)/(.*)")

while 1:
    
    line = sys.stdin.readline()

    m = reobjthumb.match(line)

    if m:
        try:
            wid = int(m.group(4))
        except ValueError, e:
            wid = 0
        try:
            ht = int(m.group(5))
        except ValueError, e:
            ht = 0

    if m and wid < 201 and ht < 201 :
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
            
    print '/iiif%s/%s/%s' %(perm[:3],pid,urlend) 
