# run as root
cd /usr/libexec

mkdir iipsrvpri
mkdir iipsrvpub
mkdir iipsrvuva

cd iipsrvpri
/bin/ln ../iipsrv/iipsrv.fcgi ./iipsrv.fcgi
cd ../iipsrvpub
/bin/ln ../iipsrv/iipsrv.fcgi ./iipsrv.fcgi
cd ../iipsrvuva
/bin/ln ../iipsrv/iipsrv.fcgi ./iipsrv.fcgi

