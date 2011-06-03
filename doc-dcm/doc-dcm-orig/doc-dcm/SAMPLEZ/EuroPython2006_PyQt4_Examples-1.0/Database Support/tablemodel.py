#!/usr/bin/env python

############################################################################
##
## Copyright (C) 2004-2006 Trolltech ASA. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *


def createConnection():

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(":memory:")
    if not db.open():
        QMessageBox.critical(0, qApp.tr("Cannot open database"),
                qApp.tr("Unable to establish a database connection.\n"
                              "This example needs SQLite support. Please read "
                              "the Qt SQL driver documentation for information "
                              "how to build it.\n\nClick Cancel to exit."),
                QMessageBox.Cancle, QMessageBox.NoButton)
        return False
    
    query = QSqlQuery()
    query.exec_("create table person(id int primary key, "
                "firstname varchar(20), lastname varchar(20))")
    query.exec_("insert into person values(101, 'Danny', 'Young')")
    query.exec_("insert into person values(102, 'Christine', 'Holand')")
    query.exec_("insert into person values(103, 'Lars', 'Gordon')")
    query.exec_("insert into person values(104, 'Roberto', 'Robitaille')")
    query.exec_("insert into person values(105, 'Maria', 'Papadopoulos')")
    return True


def createView( title, model ):
    return view


class Window(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        model = QSqlTableModel(self)
        model.setTable("person")
        model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        model.select()
        
        model.setHeaderData(0, Qt.Horizontal, 
                            QVariant(QObject.tr(model, "ID")))
        model.setHeaderData(1, Qt.Horizontal, 
                            QVariant(QObject.tr(model, "First name")))
        model.setHeaderData(2, Qt.Horizontal, 
                            QVariant(QObject.tr(model, "Last name")))
        
        view1 = QTableView(self)
        view1.setModel(model)
        view2 = QTableView(self)
        view2.setModel(model)
        
        layout = QHBoxLayout()
        layout.addWidget(view1)
        layout.addWidget(view2)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    
    window = Window()
    window.show()
    sys.exit(app.exec_())
