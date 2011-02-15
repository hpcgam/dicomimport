mkdir dicomimport
mv dicomimport.tar.gz dicomimport/dicomimport.tar.gz 
cd dicomimport
tar zxvf dicomimport.tar.gz 
rm dicomimport.tar.gz 

#Exec=python "/home/user/dicomimport/dicomimport.py"
#Path=/home/user/dicomimport

echo "Exec=python $HOME/dicomimport/dicomimport.py" >> dicomimport.desktop
echo "Path=$HOME/dicomimport" >> dicomimport.desktop

###copy desctop shortcut
test -f ${XDG_CONFIG_HOME:-~/.config}/user-dirs.dirs && source ${XDG_CONFIG_HOME:-~/.config}/user-dirs.dirs
dest=${XDG_DESKTOP_DIR:-$HOME/Desktop}
cp -v "dicomimport.desktop" "$dest"


echo Done