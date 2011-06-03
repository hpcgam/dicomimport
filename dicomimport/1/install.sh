#!/bin/sh
# Install script for local computer

# run:
# sudo sh install.sh

#######################################

echo Запускать под рутом: sh install.sh

zypper in  python-qt4
zypper in  ImageMagick

INSTDIR=/opt/dicomimport
INSTFN=dicomimport.tar.gz

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
chmod 777 {gdcmimg,storescu}
cp dicomimport.desktop /usr/share/applications
cp dic_icon.png  /usr/share/pixmaps

#run test page
firefox ./test.html
sh ./runsrv.sh

echo Done.
