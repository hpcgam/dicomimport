# -*- coding: utf-8 -*-
import os, sys, glob
import subprocess
import logging
import time, datetime
import BaseHTTPServer
import cgi
import string
import read_cfg
import procimp
from urlparse import parse_qs
from UserDict import UserDict

sys.path.append('./') #may be not need (for dicom lib)

cfg=read_cfg.Configs('dicomimport.ini')  #настройки программы
logging.basicConfig
logging.basicConfig(filename=cfg.logfn,format='%(asctime)s %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S',level=logging.DEBUG)
logging.getLogger('PyQt4.uic').setLevel(logging.INFO)   #фильтруем дебаг сообщения от кьютэ ;)
logging.debug('\nApp started')

try:
  from PyQt4 import QtCore,QtGui,uic
  import dicom
except ImportError:
  errmess='ERROR-QtCore,QtGui,uic or dicom not found'
  print errmess
  logging.debug(errmess)
  raw_input("Press Enter") 
  raise ImportError,errmess
	
app = QtGui.QApplication(sys.argv)


class MainWnd(QtGui.QDialog):
    """ класс главной формы, производит загрузку ресурсов  """
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        #super(MainWindow, self).__init__()
        uic.loadUi("mainfrm.ui", self)

"""
получаемые данные:\
из метода гет:\
1. ид пациента (номер карты)\
2. автор съемки - оператор, вводящий джпег файлы в дайком сервер.\
еще...\
дата съемки считается по умолчанию датой создания граф. файла.\
в форме поле присутствует для коррекции\
"""
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler ):
    pat_rec={}
    def do_HEAD(self):
        pass

    def do_GET(self):   # """Respond to a GET request."""
        try:
            params = parse_qs(self.path[2:]) #deprecated call use urlparse.parse_qs()
        except:
            errmess='ERROR parse incoming string'
            logging.debug(errmess)
            print errmess
            return False

        #for key, values in params.iteritems():
            #for value in values:
                #get[key] = value
                #print 'key:',key, 'values:',values, 'val',value

        #tmpt = string.split(params.get("bdate")[0],'.')
        #bdate = tmpt[2]+tmpt[1]+tmpt[0]	#reverse date to yyyymmdd
        #if( len(bdate)!=8 ):
            #errmess='ERROR parse date string'
            #logging.debug(errmess)
            #print errmess
            ##return False
            #self.pat_rec={'pat_birtd': 'bdate'}

        try:
            self._cb=params.get("_cb")[0]#if not exist -raise except
            outmessage=message = self._cb+'({"ok":1});'
        except:
            outmessage=message = '({"ok":1});'

        lis=['reg','fio','login','bdate'] 
        try:
            for par in lis:
                self.pat_rec['pat_'+par]=unicode(params.get(par)[0],'utf-8')
        except:
            errmess='ERROR parse date string'
            logging.debug(errmess)
            print errmess
            return False

        self.pat_rec['usr_comp'] = os.getenv('HOSTNAME','unknown')   #? компьютер, с которого произв. загрузка
        self.pat_rec['DateCreationStudy']=''             # дата создания файлов исследования 
        self.pat_rec['Modality']=''      
        #self.pat_rec['DateImportStudy']=datetime.datetime.now().date().strftime("%d.%m.%y")    # дата импорта файлов в дайком сервер(берется текущая)
        self.pat_rec['DateImportStudy']=datetime.datetime.now().date().strftime("%Y%m%d")    # дата импорта файлов в дайком сервер(берется текущая)
        self.pat_rec['SeriesStudy']=''           #серия исследования (используется для всей серии загр. файлов)
            
        tmpt = string.split(self.pat_rec['pat_bdate'],'.')
        self.pat_rec['pat_bdate'] = tmpt[2]+tmpt[1]+tmpt[0]	#reverse date to yyyymmdd
        
        dialog = QtGui.QFileDialog()
#        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        dialog.setWindowTitle(u"Выберите файлы для загрузки на дайком сервер")
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
#        dialog.setNameFilters(["Jpeg files (*.jpeg *.jpg)", "Bitmap (*.bmp)", "All (*)"])
        dialog.setNameFilters(["Jpeg files (*.jpeg *.jpg)", "Bitmap (*.bmp)"])
        
        dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) #топмост винд.
        dialog.activateWindow()
        UserSelectedFiles=dialog.exec_()

        if UserSelectedFiles:  #пользователь выбрал некоторые файл(ы)
            fileslist=dialog.selectedFiles()
            #fileslist.sort() #?

            #добавляем выделенные файлы в листвью и check gets filenames
            sfiles=[]
            for a in fileslist:
                sfiles.append(a)

            def DrawStateLoadingInList(item, loadstat, v=True):
                if v:
                    item.setBackgroundColor( QtGui.QColor( 0, 190, 0 ) ); item.setText( item.text()+u'\tЗагружено без ошибок' )
                    loadstat['lsucc']+=1
                else:
                    item.setBackgroundColor( QtGui.QColor( 255, 0, 0 ) ); item.setCheckState(QtCore.Qt.Unchecked)
                    item.setText( item.text()+u'\tОШИБКА ЗАГРУЗКИ' ); loadstat['lfail']+=1
                    
            # действия, производимые по нажатию кнопки Ок - попытка сконвертировать и загрузить дайком файлы на сервер
            def onOkButt():
                widget.label_4.setText(u"Отчет о загрузке:")
                widget.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
                #self.pat_rec['Modality']=string.split( str( widget.comboBox.currentText().toUtf8() ))[0]
                self.pat_rec['Modality']=string.split( unicode( widget.comboBox.currentText() ))[0]

                #получаем дату создания файла (возможно скорректированую) в виде дд.мм.гггг.
                #self.pat_rec['DateCreationStudy']=str(widget.dateEdit.date().toString("dd.MM.yyyy"))
                self.pat_rec['DateCreationStudy']=str(widget.dateEdit.date().toString("yyyyMMdd"))
                
                maxv=lcou=0;
                while lcou < widget.listWidget.count():
                    widget.listWidget.setCurrentRow(lcou)
                    if widget.listWidget.currentItem().checkState(): maxv+=1
                    lcou+=1
                    
                widget.progressBar.setRange(0,maxv)
                widget.progressBar.setFormat(u"Загружается %v из: %m ...")

                widget.progressBar.show()

                lcou=0; WeGetErrorProcessing=False
                loadstat={'lsucc':0,'lfail':0,'all':0}
                while lcou < widget.listWidget.count():
                    widget.listWidget.setCurrentRow(lcou)
                    item=widget.listWidget.currentItem()
                    # пробуем сконвертировать и разместить дайком - файл
                    if item.checkState(): #если чекбокс отмечен
                        loadstat['all']+=1
                        #jpgfilename=str(widget.listWidget.currentItem().text() )
                        jpgfilename=unicode(widget.listWidget.currentItem().text() ).encode( "utf-8" )
                        if procimp.ConvertAndUpload(jpgfilename , self.pat_rec,logging,cfg,lcou+1) : #конвертация и загрузка прошли успешно
                            DrawStateLoadingInList(item,loadstat,True)
                        else:			#возникла ошибка при конвертации или загрузке
                            DrawStateLoadingInList(item,loadstat,False)
                            WeGetErrorProcessing=True
                            
                    lcou+=1
                    widget.progressBar.setValue(lcou)
                    widget.repaint()
                #-
                #print "Ушпешно загружено", loadstat['lsucc'], "из", loadstat['all']
                
                widget.progressBar.color = QtGui.QColor(0, 250, 0) 
                
                widget.progressBar.setFormat(u"Успешно загружено: "+str(loadstat['lsucc'])+u" из "+str(loadstat['all']))
                widget.repaint()
            
                self.pat_rec['SeriesStudy']=''
                if WeGetErrorProcessing:
                    myapp = QtGui.QMessageBox()
                    myapp.setText(u'При импорте файлов возникли ошибки.\
                    \nВозможно входные файлы повреждены, или DICOM-сервер не отвечает.\
                    \nСписок файлов с ошибками помечен красным цветом');myapp.setWindowTitle(u'Сообщение об ошибке импорта файлов')
                    myapp.exec_()
            #-- 
            
            def onCancelButt():
                print 'cancel pressed'
                widget.close()

            widget = MainWnd()
            widget.setWindowTitle(u'Загрузка файлов для: '+self.pat_rec["pat_fio"])
            widget.l_kard_num.setText(self.pat_rec["pat_reg"])
            widget.l_FIO.setText(self.pat_rec["pat_fio"])
            widget.dateEdit.setDisplayFormat("dd.MM.yyyy")

            #получаем дату создания файла.
            DateCreationStudy=os.stat ( unicode(fileslist[0]) ) [8]
            sd = datetime.datetime.fromtimestamp(DateCreationStudy)
            val=sd.strftime('%d%m%Y')
            widget.dateEdit.setDate(QtCore.QDate.fromString(val, "ddMMyyyy"))      
            widget.comboBox.addItem(u'US - УЗС'); widget.comboBox.addItem(u'XC - фотографии'); widget.comboBox.addItem(u'ES - эндоскопия'); widget.comboBox.addItem(u'CT - комп.томогр.'); widget.comboBox.addItem(u'OT - другие')
            qlist = QtCore.QStringList(map(QtCore.QString, sfiles))

            widget.progressBar.reset()
            widget.progressBar.hide()
            
            #установка значений и чекбоксов для листвью (по умолчанию все файлы включены)
            for a in qlist:
                item = QtGui.QListWidgetItem(a)
                item.setFlags(QtCore.Qt.ItemIsUserCheckable| QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                widget.listWidget.addItem(item)

            QtCore.QObject.connect(widget.buttonBox, QtCore.SIGNAL('accepted()'), onOkButt)
            QtCore.QObject.connect(widget.buttonBox, QtCore.SIGNAL('rejected()'), onCancelButt)

            widget.show()
            app.exec_()
        #-
        else:
            print 'no files selected'
            
        #посылаем но дата броузеру.
        self.send_response(200)
        self.send_header("Content-type", "text/javascript") #??
        #print '4 browser:', '_cb_blabla({"ok":1});'         #or 	print '4 browser:', '_cb_blabla({"err":"reason"});' #got err
        self.end_headers()
        #self.wfile.write(outmessage) #выскакивает popup
        print outmessage

        print 'done'
###########################################

def main():
    #russificaton for resources 
    #translator = QTranslator(app)
    #translator.load("qt_ru.qm")
    #app.installTranslator(translator)

    #app = QtGui.QApplication(sys.argv)
    #app.setStyle("Windows") #Plastique , Motif, CDE, Plastique, Cleanlooks

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((cfg.httpdhost, int(cfg.httpdport)), MyHandler)
    print time.asctime(), "Server Started - %s:%s" % (cfg.httpdhost, cfg.httpdport)
    print "Destination server: "+cfg.dcmhost+", AE title: "+cfg.dcmaetitle+"\nAll ok, waiting..."
    try:
      httpd.serve_forever()
      print 'httpd stopped..'
    except KeyboardInterrupt:
      pass
    except Exception:
      print 'unknown err'
      httpd.server_close()
    print time.asctime(), "Server Stopped - %s:%s" % (cfg.httpdhost, cfg.httpdport)


if __name__ == '__main__':
    main()

