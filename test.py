#!/usr/bin/python -u

# this test script does a few things:
# 1. ensures that the iiifAcl script works in an unbuffered fashion
#    (if this test script hangs, the iiifAcl script needs fixin')
# 2. ensures that a sampling of pids returns the correct permissions
# 3. tests both the normal and thumbnail codepaths in the iiifAcl script

import sys
import string
from subprocess import Popen, PIPE

# sample pids for uva/pub/pri
pids = { 'uva-lib:236153', 'uva-lib:453245', 'uva-lib:2807870' }
fmt = '/%s/%s/full/%s/0/default.jpg'

def msg(s):
	print '[TEST] %s' % (s)

script = './iiifAcl.py'
if len(sys.argv) > 1:
	script = sys.argv[1]

msg('script  : ' + script)
process = Popen([ script ], stdin=PIPE, stdout=PIPE)

msg('NOTE: if this script hangs here, fix input buffering in the above script!')

for pid in pids:
	# grab prefix from a sample request, to later populate expected responses
	process.stdin.write(fmt % ('iiif', pid, 'full') + '\n')
	process.stdin.flush()
	res = process.stdout.readline().strip()
	pieces = string.split(res,'/')
	prefix = pieces[1]
	msg('prefix  : %s' % (prefix))

	msg('pid     : %s' % (pid))

	testcases = dict()

	# should return /iiif{pri,uva,pub}/...
	testcases.update({fmt % ('iiif', pid, 'full'): fmt % (prefix, pid, 'full')})

	# should return same prefixes as above
	testcases.update({fmt % ('iiif', pid, '201,'): fmt % (prefix, pid, '201,')})
	testcases.update({fmt % ('iiif', pid, ',201'): fmt % (prefix, pid, ',201')})
	testcases.update({fmt % ('iiif', pid, '201,201'): fmt % (prefix, pid, '201,201')})

	# should return /iiifpub/...
	testcases.update({fmt % ('iiif', pid, '200,'): fmt % ('iiifpub', pid, '200,')})
	testcases.update({fmt % ('iiif', pid, ',200'): fmt % ('iiifpub', pid, ',200')})
	testcases.update({fmt % ('iiif', pid, '200,200'): fmt % ('iiifpub', pid, '200,200')})

	# ensure each request produces the expected response
	for req, exp in testcases.iteritems():
		msg('request : [%s]' % (req))
		msg('expect  : [%s]' % (exp))
		process.stdin.write(req + '\n')
		process.stdin.flush()
		res = process.stdout.readline().strip()
		msg('result  : [%s]' % (res))
		if res != exp:
			msg('FAILURE : [%s] != [%s]' % (res, exp))
			exit(1)

process.stdin.close()
process.wait()

msg('SUCCESS')

exit(0)
