#!/usr/bin/env python

"""
sqlcursorview.py

Copyright (C) 2006 Torsten Marek

This file is part of the examples for the Introducing PyQt4 for GUI Application
Development talk given at EuroPython 2006 at CERN, Geneva, Switzerland.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import sys

from PyQt4 import QtCore, QtGui

from pysqlite2 import dbapi2


class DbAPICursorModel(QtCore.QAbstractItemModel):
    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)
        self._resultRows = []
        self._columnTitles = []


    def columnCount(self, parent):
        return len(self._columnTitles)

    def rowCount(self, parent):
        return len(self._resultRows)

    def setResultset(self, cursor):
        self._resultRows = cursor.fetchall()
        self._columnTitles = [desc[0] for desc in cursor.description]
        self.reset()

    def index(self, row, column, parent):
        return self.createIndex(row, column, 0)
    

    def data(self, index, role):
        if not (index.isValid() and role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant()

        value = self._resultRows[index.row()][index.column()]
        if value is None:
            value = ""
        if isinstance(value, str):
            try:
                value = unicode(value, "UTF-8")
            except UnicodeError:
                value = unicode(value, "ISO-8859-15")

        else:
            value = unicode(value)
        return QtCore.QVariant(value)

        
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._columnTitles[section])
        
        return QtCore.QVariant()


app = QtGui.QApplication(sys.argv)
model = DbAPICursorModel()
view = QtGui.QTableView()
sort = QtGui.QSortFilterProxyModel()
sort.setSourceModel(model)
view.setModel(sort)

view.horizontalHeader().setSortIndicatorShown(True)
view.horizontalHeader().setClickable(True)

QtCore.QObject.disconnect(view.horizontalHeader(), QtCore.SIGNAL("sectionPressed(int)"),
                          view, QtCore.SLOT("selectColumn(int)"))
QtCore.QObject.connect(view.horizontalHeader(), QtCore.SIGNAL("sectionClicked(int)"),
                       view, QtCore.SLOT("sortByColumn(int)"))
                       
view.setAlternatingRowColors(True)

conn = dbapi2.connect(":memory:")
query = conn.cursor()
query.execute("create table person(id int primary key, "
            "firstname varchar(20), lastname varchar(20))")
query.execute("insert into person values(101, 'Danny', 'Young')")
query.execute("insert into person values(102, 'Christine', 'Holand')")
query.execute("insert into person values(103, 'Lars', 'Gordon')")
query.execute("insert into person values(104, 'Roberto', 'Robitaille')")
query.execute("insert into person values(105, 'Maria', 'Papadopoulos')")

#QtCore.disconnect(view, "columnClicked(
query.execute("SELECT * FROM person")
model.setResultset(query)
view.show()
app.exec_()
