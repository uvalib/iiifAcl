# iiifAcl
a combination of Apache RewriteMap and config changes that will intercept requests for images bound for iiif server, query a web service running on Tracksys server to discover desired viewing rights for a given image, and then use soft linked copies of the iiif server executable to enforce those rights.

Here's the basic flow:

A user requests http://fedora02.lib.virginia.edu/iiif/uva-lib:2295196/full/!1200,1500/0/default.jpg

These apache config lines:

RewriteMap IIIFACL prg:/usr/local/bin/iiifAcl.py
RewriteRule ^/iiif/ "${IIIFACL:%{REQUEST_URI}}"

cause the python script /usr/local/bin/iiifAcl.py to be invoked, passing in the URI from the request.  The script contacts the service configured into that script, which should be the corresponding Tracksys service to accept a PID (example: uva-lib:2137386) and return a level of viewing rights, one of "public", "uva", or "private".

RewriteMaps return a rewritten URI - the script will return the original URI but with the beginning "iiif" rewritten to "iiifpub", "iiifuva", or "iiifpri" correesponding to the permissions indicated.

These new URIs will then be pass through the folling RewriteRules:

RewriteRule ^/iiifpub/([^:]{1,}):([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9])?/(.*)$ /iipsrvpub?IIIF=/var/www/html/$1/$2/$3/$4/$5$6/$2$3$4$5$6.jp2/$7  [PT]
RewriteRule ^/iiifuva/([^:]{1,}):([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9])?/(.*)$ /iipsrvuva?IIIF=/var/www/html/$1/$2/$3/$4/$5/$6/$2$3$4$5$6.jp2/$7  [PT]
RewriteRule ^/iiifpri/([^:]{1,}):([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9][0-9])?([0-9])?/(.*)$ /iipsrvpri?IIIF=/var/www/html/$1/$2/$3/$4/$5$6/$2$3$4$5$6.jp2/$7  [PT]

Each causes the iiif server to be invoked from one of three hard-linked paths.  The Apache config can then use Directory directives to apply appropriate access restrictions to each level.

Note that for now, private permissions are not defined.

For this to work, the hard links to the iipsrv executable must exist, the RewriteMap executable must reside in /usr/local/lib with the proper URL for a Tracksys permission server in the code, and the proper iipsrv.conf file included in Apache's extra config directory.

