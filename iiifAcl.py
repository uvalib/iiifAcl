#!/usr/bin/python -u
import sys
import fileinput
import re
import socket
import logging
from urllib2 import Request, urlopen, URLError

# controls whether to use cached IP address workaround
TSUseIPKludge = True
# controls whether to use prod values
TSUseProdVals = True

# Tracksys definitions

if TSUseProdVals:
	TSProtocol = 'http://'
	TSHostName = 'tracksys.lib.virginia.edu'
	TSAPIPath = '/api/pid/%s/rights'
else:
	TSProtocol = 'http://'
#	TSHostName = 'tracksysdev.lib.virginia.edu'
#	TSAPIPath = ':8082/%s'
	TSHostName = 'rightsws.lib.virginia.edu'
	TSAPIPath = ':8089/%s'

TSDestination = TSHostName
TSHeaders = {}
TSTimeout = 2

if TSUseIPKludge:
	# DNS lookups intermittently hang for ~5 seconds, affecting urlopen().
	# To mitigate, we look up the IP address at invocation, and use it forever.
	# Since Apache invokes this script at startup and keeps it open indefinitely,
	# if the IP address for this server changes, Apache will need to be restarted.
	TSIPAddress = socket.gethostbyname(TSHostName)
	TSDestination = TSIPAddress
	TSHeaders = { "Host" : TSHostName }

	# Accessing the server by IP address can cause an SSL hostname mismatch error.
	# To mitigate, we override this check:
	#import ssl
	#ssl.match_hostname = lambda cert, hostname: True

# IIIF path matching regexes
reobjthumb = re.compile("^/iiif/([^/]*):([0-9]*)/full/(\!?)([0-9]*),([0-9]*)/(.*)")
reobjother = re.compile("^/iiif/([^/]*):([0-9]*)/(.*)")

# initialize logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')

def warn(msg):
	logging.warning('[%s] %s' % (line.strip(), msg))

# apache communication loop
while 1:

	line = sys.stdin.readline()

	if not line:
		exit(0);

	# set default permission
	perm = 'private'

	# if this is a path for a scaled IIIF image, extract any width/height
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

	# if this is a scaled image whose largest specified dimension does not exceed 200 pixels, allow public access
	if m and wid < 201 and ht < 201:
		pid = '%s:%s' % (m.group(1), m.group(2))
		urlend = '%s/%s%s,%s/%s' % ('full', m.group(3), m.group(4), m.group(5), m.group(6))
		perm = 'public'
	else:
		# check if this is a valid IIIF path
		m = reobjother.match(line)

		if m:
			# valid IIIF path: extract the PID and lookup access restrictions
			pid = '%s:%s' % (m.group(1), m.group(2))
			urlend = m.group(3)
			TSServiceURL = TSProtocol + TSDestination + TSAPIPath % (pid)
			req = Request(TSServiceURL, headers=TSHeaders)
			try:
				# call the API
				resp = urlopen(req,None,TSTimeout)
				perm = resp.read().decode('ascii')
			except URLError, e:
				# API error
				warn('API request failed for url [%s]: %s' % (TSServiceURL, str(e)))
				perm = 'public'
		else:
			# not a valid IIIF path
			warn('invalid path')
			pid = 'unknown'
			urlend = ''
			perm = 'private'

	print '/iiif%s/%s/%s' %(perm[:3],pid,urlend)
