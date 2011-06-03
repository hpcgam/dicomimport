#
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtCore import QUrl
u = QUrl("file:///home/user/work/doc-dcm/htm/nt.htm")
app = QApplication([])
w = QWebView()
w.setHtml(open("/home/user/work/doc-dcm/htm/nt.htm").read(), u)
w.show() 
app.exec_()