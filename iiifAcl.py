#!/usr/bin/python -u
import sys
import fileinput
import re
import socket
import json
import logging
from urllib2 import Request, urlopen, URLError, HTTPError

# controls whether to use cached IP address workaround
TSUseIPKludge = True

# Tracksys definitions
TSProtocol = 'https://'
TSHostName = 'tracksys.lib.virginia.edu'
TSSuffix = '/api/aries/'
TSDestination = TSHostName
TSHeaders = {}
TSTimeout = 30

if TSUseIPKludge:
	# DNS lookups intermittently hang for ~5 seconds, affecting urlopen().
	# To mitigate, we look up the IP address at invocation, and use it forever.
	# Since Apache invokes this script at startup and keeps it open indefinitely,
	# if the IP address for this server changes, Apache will need to be restarted.
	TSIPAddress = socket.gethostbyname(TSHostName)
	TSDestination = TSIPAddress
	TSHeaders = { "Host" : TSHostName }

	# Tracksys redirects IP-based http requests to https, causing a hostname
	# mismatch error.  To mitigate, we override this check:
	import ssl
	ssl.match_hostname = lambda cert, hostname: True

# build final URL
TSServiceURL = TSProtocol + TSDestination + TSSuffix

# IIIF path matching regexes
reobjthumb = re.compile("^/iiif/([^/]*):([0-9]*)/full/(\!?)([0-9]*),([0-9]*)/(.*)")
reobjother = re.compile("^/iiif/([^/]*):([0-9]*)/(.*)")

# initialize logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')

def warn(msg):
	logging.warning('[' + line.strip() + '] ' + msg)

# apache communication loop
for line in sys.stdin:

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
	if m and wid < 201 and ht < 201 :
		pid = m.group(1) + ':' + m.group(2)
		urlend = 'full' '/' + m.group(3) + m.group(4) + ',' + m.group(5) + '/' + m.group(6)
		perm = 'public'
	else:
		# check if this is a valid IIIF path
		m = reobjother.match(line)

		if m:
			# valid IIIF path: extract the PID and lookup access restrictions
			pid = m.group(1) + ':' + m.group(2)
			urlend = m.group(3)
			req = Request(TSServiceURL + pid, headers=TSHeaders)
			try:
				# call the Aries API
				resp = urlopen(req,None,TSTimeout)
				jres = resp.read().decode('ascii')
				try:
					# parse the JSON response
					api = json.loads(jres)
					try:
						# check for access restriction field
						perm = api['access_restriction']
					except KeyError:
						# access_restriction field does not exist
						#warn('no access_restriction key in JSON: [' + jres + ']')
						perm = 'public'
				except ValueError, e:
					# JSON parsing error
					warn('could not parse JSON: [' + jres + ']')
					perm = 'public'
			except HTTPError, e:
				# Aries API HTTP error
				warn('API request failed: ' + str(e.code) + ' (' + str(e.reason) + ')')
				perm = 'public'
			except URLError, e:
				# Aries API other error
				warn('API request failed: ' + str(e.reason))
				perm = 'public'
		else:
			# not a valid IIIF path
			warn('invalid path')
			pid = 'unknown'
			urlend = ''
			perm = 'private'

	print '/iiif%s/%s/%s' %(perm[:3],pid,urlend)
