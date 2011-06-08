#!/bin/sh
# Install script for local computer
#######################################

echo Запускать под рутом: sh install.sh

zypper in  python-qt4
zypper in  ImageMagick
#zypper in  python-xlib
zypper in python-imaging 
zypper in python-imaging-sane


INSTDIR=/opt/doc-dcm
INSTFN=doc-dcm.tar.gz

if [ ! -d $INSTDIR ]; then
	echo ''
	mkdir $INSTDIR
	chmod 755 $INSTDIR
	#chown nobody:nogroup $INSTDIR
fi

mv $INSTFN $INSTDIR
cd $INSTDIR
tar zxvf $INSTFN
#rm $INSTFN
##chmod 666 *
#chmod 777 {gdcmimg,storescu}

cp doc-dcm.desktop /usr/share/applications
cp doc-dcm_icon.png  /usr/share/pixmaps

#run test page
#firefox ./test.html
#sh ./runsrv.sh

echo Done.

