# -*- coding: utf-8 -*-
# needs pack:
# python-imaging 
# python-imaging-sane

import locale
locale.setlocale(locale.LC_ALL, '')
"""
5. как получать статус сканера "готов"?

1. возможно надо деактивировать кнопку "скан" на время сканирования?
2. проверить инсталляшку. 
3. Руководство!!!
4. SOLVED? какое качество выдает save у джепга? ~75

"""
import os, sys, glob
import subprocess
import logging
import time, datetime
import BaseHTTPServer
import cgi
import string
import time
import shutil

sys.path.append('./') #may be not need (for dicom lib)
sys.path.append('./lib')

import read_cfg
import procimp
import snd
from urlparse import parse_qs
from UserDict import UserDict
import TmpFile

B_SOUND=u"error.wav"
HOME_DIR = os.getenv('HOME') or os.getenv('USERPROFILE')

cfg=read_cfg.Configs('dicomimport.ini')  #настройки программы
logging.basicConfig
#logging.basicConfig(filename=cfg.logfn,format='%(asctime)s %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S',level=logging.DEBUG)

logfile=HOME_DIR+'/doc-dicom.log'
if os.path.exists(logfile) and os.path.getsize(logfile) >512000L: #delete without log rotation
    try: os.remove(logfile)
    except: pass
        
logging.basicConfig(filename = logfile, format='%(asctime)s %(levelname)s %(message)s', \
                    datefmt='%a, %d %b %Y %H:%M:%S',level=logging.DEBUG)
logging.getLogger('PyQt4.uic').setLevel(logging.INFO)   #фильтруем дебаг сообщения от кьютэ ;)

def ERR(mess):
    print mess
    logging.error(mess)
    snd.psound(B_SOUND)
    raw_input("\n Нажмите Enter")

# single instance{
import fcntl
pid_file = HOME_DIR+ '/doc-dicom.pid'
fp = open(pid_file, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    ERR("Программа уже запущена. ")
    sys.exit(0)
# single instance{

try:
    from PyQt4 import QtCore,QtGui,uic
    #from PyQt4.QtWebKit import *
    import dicom
except ImportError:
    ERR('ERROR: PyQt not installed. (or dicom not found)')
    raise

try:
    import sane
except ImportError:
    ERR('ERROR: sane not installed.')
    raise

_RED = QtGui.QColor( 255, 0, 0 )
_GREEN = QtGui.QColor( 0, 190, 0 )
_WHITE = QtGui.QColor( 255, 255, 255 )

app = QtGui.QApplication(sys.argv)
logging.info('\nDoc-Dicom started')

class MainWnd(QtGui.QDialog):
    """ класс главной формы  """
   
    def __init__(self, pat_rec):
        QtGui.QWidget.__init__(self)
        #super(MainWindow, self).__init__()
        uic.loadUi("mainfrm.ui", self)
        
        QtCore.QObject.connect(self.B_export, QtCore.SIGNAL('clicked()'), self.onB_export)
        QtCore.QObject.connect(self.B_help, QtCore.SIGNAL('clicked()'), self.onB_help)
        QtCore.QObject.connect(self.B_scan, QtCore.SIGNAL('clicked()'), self.onB_scan)
        QtCore.QObject.connect(self.B_exit, QtCore.SIGNAL('clicked()'), self.onB_exit)

        self.pat_rec = pat_rec
        self.setWindowTitle(u'Пациент: '+self.pat_rec["pat_fio"])
        #self.l_pat_name.setText(u"...")        #self.l_pat_name.setText(self.pat_rec["pat_fio"]+u"\nА/К:"+self.pat_rec["pat_reg"])
        self.DrawCurrStatus()
        
        #self.imageLabel = QtGui.QLabel(self)        #self.imageLabel.resize(370, 120)
        self.imageLabel.move(10, 220)
        self.imageLabel.setText(u"...")
        
        #self.labelHelp.setText(u"<b>Справка </b>")        QtCore.QObject.connect(self.labelHelp,QtCore.SIGNAL("click()"), self.changeEdit)
        
        self.comboBox.addItem(u'Направление');
        self.comboBox.addItem(u'Другое...');
        self.lineEdit.setDisabled(True)
        QtCore.QObject.connect(self.comboBox,QtCore.SIGNAL("currentIndexChanged(int)"), self.changeEdit)
        
        self.DrawPreview("./logo.jpg")
        self.listWidget.itemSelectionChanged.connect(self.RepaintPreview)
        self.progressBar.reset()
        self.progressBar.hide()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        self.scanthread = scannerThread()
        self.connect(self.scanthread, QtCore.SIGNAL('errScan'), self.errScan )
        self.connect(self.scanthread, QtCore.SIGNAL('scanFinished'), self.scanOk )
        self.connect(self.scanthread, QtCore.SIGNAL('scanCancelled'), self.scanCancelled )

        self.activateWindow()
        self.show()
          
        tv=os.getenv('TMP') or os.getenv('TEMP') or os.getenv('TMPDIR')
        if not tv: tv= os.getenv('HOME') or os.getenv('USERPROFILE') #tmp variable not found =:(  )
        if tv[-1:] != '/': tv=tv+'/' 
        self.dirpath=tv+str( time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) )

        if not os.path.exists(self.dirpath):
            try:
                os.makedirs(self.dirpath)
            except:
                #err=True
                self.dirpath=os.getenv("HOME")
                
        self.scanthread.threadInitialize(self.dirpath)
        
        # есть ли сканеры?
        sane_version = sane.init()
        scanners=sane.get_devices()        #        print "scanners", scanners
        if not scanners:
            self.errScan(u"Сканер не обнаружен, проверьте подключение сканера.")
            logging.error("MainWnd _init_: сканер не найден")
            sane.exit()
            return

    def DisableButtons(self,ar):
        self.B_export.setDisabled(ar)
        self.B_help.setDisabled(ar)
        #self.B_scan.setDisabled(ar)

    def changeEdit(self):
        if self.comboBox.currentIndex()==self.comboBox.count()-1:
            self.lineEdit.setDisabled(False)
        else:
            self.lineEdit.setDisabled(True)
        
    def DrawCurrStatus(self,text=''):
        if not text:
            self.l_pat_name.setText(self.pat_rec["pat_fio"]+u"\nА/К: "+self.pat_rec["pat_reg"])
        else:
            self.l_pat_name.setText(text)
            
        for i in xrange(10): #dirty hack for thread =)
            QtCore.QThread.msleep(20)            #time.sleep(0.05)
            QtGui.QApplication.processEvents()

    #def closeEvent(self,QMainWindow):
    def closeEvent(self,event):
        #проверяем список. если есть незагруженные файлы
        if self.listWidget.count() ==0:
            return
        
        lcou=0
        list=[]
        while lcou < self.listWidget.count():
            self.listWidget.setCurrentRow(lcou)
            item=self.listWidget.currentItem()

            if item.backgroundColor()!=_GREEN: #если чекбокс отмечен
                jpgfilename=unicode(self.listWidget.currentItem().text() ).encode( "utf-8" )
                list.append(jpgfilename)
            lcou+=1
                 
        if list:
            reply = QtGui.QMessageBox.question(self, u'Внимание',
                 u"Файлы не были сохранены на сервере. Выити из программы?",
                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                event.ignore()
                return
        try: 
            shutil.rmtree(self.dirpath)
        except:            pass
#        logging.info("window closed")
        event.accept()

    def RepaintPreview(self):
        #print self.listWidget.currentItem().text()
        self.DrawPreview(self.listWidget.currentItem().text())
        
    def DrawPreview(self,fn ):
        img=QtGui.QImage(fn)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(img) )
        self.scaleFactor = 1.0
        self.imageLabel.setScaledContents(True)
        
    def AddFileInList(self, arg):
        #self.listFiles+=(True,arg,True,0)
        item = QtGui.QListWidgetItem(arg)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable| QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        item.setBackgroundColor(_WHITE)
        self.listWidget.addItem(item)
        #self.B_export.setDisabled(False)
        self.DrawPreview(arg)

        #refresh main form and list
    def DoPaint(self, arg):
        #print "from thread:", str(arg )         #print "curr mode:",gMode
        self.l_curr_state.setText(str(arg ))
        self.listWidget.Clear() #?
 
    def errScan(self,errorMess):
        snd.psound(B_SOUND)
        QtGui.QMessageBox.critical(self, u'Проблема со сканером:', errorMess)
        self.B_scan.setText(u"Сканировать")
        self.DrawCurrStatus()
        self.DisableButtons(False)
        #print "ya error"

    def scanCancelled(self):
        self.B_scan.setText(u"Сканировать")
        self.DisableButtons(False)
        self.DrawCurrStatus()
        print "scanCancelled done"#, scannedFile

    def scanOk(self,scannedFile):
        self.B_scan.setText(u"Сканировать")
        
        self.AddFileInList(scannedFile) #перенести в ок
        self.DisableButtons(False)
        self.DrawCurrStatus()
        print "scanOk done" #, scannedFile
        
    def onB_help(self):
        flags=self.windowFlags()  &~QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        import webbrowser
        webbrowser.open(os.path.abspath('')+"/htm/hlp.html" )
        return
  
    def onB_scan(self):
#    http://webcache.googleusercontent.com/search?q=cache:cL3CiijTODIJ:python.su/forum/viewtopic.php%3Fid%3D10177+%22auto-crop%22+PIL&cd=10&hl=ru&ct=clnk&gl=ru&source=www.google.ru
        #http://nullege.com/codes/show/src@n@a@NanScan-HEAD@NanScan@Backends@SaneBackend.py/38/sane.get_devices
        #http://energyplus-frontend.googlecode.com/svn-history/r147/trunk/organizer/initwindow.py

        if self.scanthread.imWorking:
            self.DrawCurrStatus(u"Прерывание операции...")
            #print "canc"
            self.scanthread.cancelScan()
        else:
            #print "bscabbb"
            self.B_scan.setText(u"Прервать")
            self.DrawCurrStatus(u"Идет сканирование...")
            self.DisableButtons(True)
            if self.checkBox.isChecked(): dpi=150
            else: dpi=72
            self.scanthread.beginScan(dpi)
            
        print "done - onB_scan(self):",self.scanthread.imWorking

        
    def onB_export(self):
        
        if not self.listWidget.count(): # нет сканированных файлов
            return
        
        logging.info('export begin...')
        self.DrawCurrStatus(u"Сохранение...")
        #self.DisableCurrButt(self.B_export)#!!! ??после экспорта дизаблить кнопку
        
        self.progressBar.setMaximum(self.listWidget.count())
        self.progressBar.show()
        lcou=0; WeGetErrorProcessing=False
        loadstat={'lsucc':0,'lfail':0,'all':0}
        #print "self.listWidget.count()",self.listWidget.count()
        
        while lcou < self.listWidget.count():
            self.listWidget.setCurrentRow(lcou)
            item=self.listWidget.currentItem()
            # пробуем сконвертировать и разместить дайком - файл
            if item.checkState() and item.backgroundColor()!=_GREEN: #если чекбокс отмечен
                loadstat['all']+=1
                #print "sadasdkaskfk=",loadstat['all']
                jpgfilename=unicode(self.listWidget.currentItem().text() ).encode( "utf-8" )
                
                sel=unicode(self.comboBox.currentText() ) # 
                bSuceed, StudyUID, SeriesUID, ObjectUID = procimp.ConvertAndUpload(jpgfilename , self.pat_rec, cfg, sel)
               
                if bSuceed:
                #if procimp.ConvertAndUpload(jpgfilename , self.pat_rec, cfg, sel) : #конвертация и загрузка прошли успешно
                    loadstat['lsucc']+=1
                    item.setBackgroundColor(_GREEN)
                    
                    #http://python.su/forum/viewtopic.php?pid=7863
                    # autocrop: http://bytes.com/topic/python/answers/24415-auto-crop-pil
                    # теперь передаем в апи ссылку?
                    str4mis='dcm4chee://wado?requestType=WADO&studyUID=' + \
                                    StudyUID+'&seriesUID='+SeriesUID+'&objectUID='+ObjectUID
                    logging.info('wado url:'+str4mis)
                    
                else:			#возникла ошибка при конвертации или загрузке
                    item.setBackgroundColor(_RED); loadstat['lfail']+=1
                    WeGetErrorProcessing=True
                    
            lcou+=1
            self.progressBar.setValue(lcou)
            self.progressBar.repaint() #

        #print "Уcпешно загружено", loadstat['lsucc'], "из", loadstat['all']
        self.progressBar.color = QtGui.QColor(0, 250, 0) 
        self.progressBar.setFormat(u"Успешно загружено: "+str(loadstat['lsucc'])+u" из "+str(loadstat['all']))
        self.progressBar.repaint()
        self.DrawCurrStatus()
        
    def onB_exit(self):
        devs=sane.get_devices()
        if not devs:
#            print "no dev!"
            try:
                sane.exit()
            except: pass
 #           return
        else:
            try:
                s=sane.cancel()
            except: pass
            #print "dev found:",s
            
        self.close()
        #try:
        #    s = sane.open(devs[0][0])
        #except:
        #    print "ошибка открытия сканера"
        #    s.close()
        #    sane.exit()

    
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
            logging.error(errmess)
            print errmess
            return False

        #for key, values in params.iteritems():
            #for value in values:
                #get[key] = value
                #print 'key:',key, 'values:',values, 'val',value

        #tmpt = string.split(params.get("bdate")[0],'.')
        #bdate = tmpt[2]+tmpt[1]+tmpt[0]	#reverse date to yyyymmdd
        #if( len(bdate)!=8 ):
        #    errmess='ERROR parse date string'
        #    logging.debug(errmess)
        #    print errmess
        #    return False
        #    #self.pat_rec={'pat_birtd': 'bdate'}

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
        #self.pat_rec['DateCreationStudy']=''             # дата создания файлов исследования 
        self.pat_rec['Modality']='OT' 
        #self.pat_rec['DateImportStudy']=datetime.datetime.now().date().strftime("%d.%m.%y")    # дата импорта файлов в дайком сервер(берется текущая)
        self.pat_rec['DateCreationStudy']=self.pat_rec['DateImportStudy']=datetime.datetime.now().date().strftime("%Y%m%d")    # дата импорта файлов в дайком сервер(берется текущая)
        self.pat_rec['SeriesStudy']=''           #серия исследования (используется для всей серии загр. файлов)
            
        tmpt = string.split(self.pat_rec['pat_bdate'],'.')
        self.pat_rec['pat_bdate'] = tmpt[2]+tmpt[1]+tmpt[0]	#reverse date to yyyymmdd
        
        widget = MainWnd(self.pat_rec)
        #widget.setWindowTitle(u'Пациент: '+self.pat_rec["pat_fio"])
        #widget.l_kard_num.setText(self.pat_rec["pat_reg"]); widget.l_FIO.setText(self.pat_rec["pat_fio"])
        #widget.dateEdit.setDisplayFormat("dd.MM.yyyy"); widget.show()
        app.exec_()
            
        #посылаем но дата броузеру.
        self.send_response(200)
        self.send_header("Content-type", "text/javascript") #??
        #print '4 browser:', '_cb_blabla({"ok":1});'         #or 	print '4 browser:', '_cb_blabla({"err":"reason"});' #got err
        self.end_headers()
        #self.wfile.write(outmessage) #выскакивает popup
        print outmessage
        print 'done'
        
###########################################
# self.scannerthread = scannerThread()
class scannerThread(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        #print 'scannerThread init'
        self.imWorking = False
        self.dpi=72

    def threadInitialize(self,dirpath):
        self.dirpath=dirpath
        #print 'threadInitialize'
        
    def autocrop2(self,im):
        import Image, ImageChops, ImageFilter
        bg=im
        bg=bg.filter(ImageFilter.BLUR)
        bg=bg.convert('P').convert('1').convert("RGB") #????
        bg2=Image.new(bg.mode, bg.size, bg.getpixel((im.size[0]-1,  im.size[1]-1, )) )
        # problem line ^^^^^????
        diff = ImageChops.difference(bg, bg2)
        bbox = diff.getbbox()
        #print "bbox", bbox
        if bbox: return im.crop(bbox) # cropped
        else: return im # no contents
        
    def run(self):
        #print "rnning, wait"
        #import time
        #time.sleep(12)
        
        sane_version = sane.init()
        devs=sane.get_devices()
        
        if not devs:
            #self.ScanNotFoundMess()            #self.DrawCurrStatus()
            self.emit( QtCore.SIGNAL('errScan'), u"Сканер не обнаружен, проверьте подключение." )
            logging.error("scannerThread: Сканер не обнаружен")
            sane.exit()
            return
        
        try:
            self.s = sane.open(devs[0][0])
        except:
            print "ошибка открытия сканера"
            #self.DrawCurrStatus()            #self.ScanNotFoundMess()
            self.emit( QtCore.SIGNAL('errScan'), u"Ошибка открытия сканера" )
            try:
                self.s.close()
                sane.exit()
            except: pass
            self.imWorking = False
            return 
            
        #print 'Device parameters:', s.get_parameters()
        #for opt in s.get_options():
        #    print opt
        
        self.s.mode = 'color'
        #self.s.resolution=130#150
        self.s.resolution=self.dpi
        #s.depth = 32
        #print 'Device parameters:', s.get_parameters()        #print 'Device options:', s.get_options()        #print 'Device options:', s.optlist

        self.imWorking = True
        try:
            #self.s.start()
            im=self.s.scan()
        except:  # _sane.Error, se:            #print se
            self.emit( QtCore.SIGNAL('errScan'), u"Ошибка сканирования" )
            self.imWorking = False
            return #?
        
        #im=self.s.snap() #заюзать кутэ
        #import ImageQt
        #image = ImageQt.ImageQt(im)
        
        self.s.close()
        sane.exit()

        #im.show()
        filename=self.dirpath+'/'+str( time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) )+'.jpg'
        im = self.autocrop2(im)
        im.save(filename)
        self.emit( QtCore.SIGNAL('scanFinished'), QtCore.QString(filename ))
        #
        #image.save(QtCore.QString(filename+'111'),"jpg",70)
        #
        
         #тестовая секция
        #filename =u"это имя файла.жпег"
        #self.emit( QtCore.SIGNAL('scanFinished'),QtCore.QString(filename) )
        #тестовая секция
        
        self.imWorking = False
        #print "done"
        
    def beginScan(self, dpi):
        #self.emit( QtCore.SIGNAL('error(int)'), 1 )
        #self.emit( QtCore.SIGNAL('scanFinished'),u"блаблабла" )
        #return
        self.dpi = dpi
        #print 'begin beginScan(self)'
        self.imWorking = True
        self.start()
        #print 'scan done?- beginScan(self)'
        self.imWorking = False

    def cancelScan(self):
        print 'cancel Scan'
        #import time
        #time.sleep(5)
        #print 'canceled'
        
        try:
            zzz=self.s.cancel()
            #zz1=sane.cancel()
            self.emit( QtCore.SIGNAL('scanCancelled'))
        except:
            print "error cancel!"
            pass
            #Вывести сообщение об ошибке отмены?
        print 'canceled???  z= '
        print zzz

        
    def __del__(self):
        self.wait()
        #print "im deleted"
###########################################

def main():
    server_class = BaseHTTPServer.HTTPServer
#    httpd = server_class(("127.0.0.1", 9966), MyHandler)
    httpd = server_class((cfg.httpdhost, int(cfg.httpdport)), MyHandler)
#    print  "serv started"
    
 
    print time.asctime(), "Server Started - %s:%s" % (cfg.httpdhost, cfg.httpdport)
    print "Destination server: "+cfg.dcmhost+", AE title: "+cfg.dcmaetitle+"\nAll ok, waiting..."
    try:
        httpd.serve_forever()
        print "httpd stopped.."
    except KeyboardInterrupt:
        pass
    except Exception:
        print 'unknown err'
        httpd.server_close()
        print time.asctime(), "Server Stopped - %s:%s" % (cfg.httpdhost, cfg.httpdport)
        #print  "Server Stopped - "

if __name__ == '__main__':
    main()
