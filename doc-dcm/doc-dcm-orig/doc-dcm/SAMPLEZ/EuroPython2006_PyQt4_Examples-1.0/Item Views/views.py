#!/usr/bin/env python

"""
views.py

Copyright (C) 2006 David Boddie

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
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QApplication, QFont, QStandardItemModel, QTableView, \
     QTreeView

if __name__ == "__main__":

    app = QApplication(sys.argv)

    phonebook = {"Arthur": "Camelot",
                 "Monty": "The Circus",
                 "David": "Oslo"}
    
    model = QStandardItemModel(3, 2)
    row = 0
    
    for name, address in phonebook.items():
    
        model.setData(model.index(row, 0), QVariant(name))
        model.setData(model.index(row, 1), QVariant(address))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        model.setData(model.index(row, 0), QVariant(font), Qt.FontRole)
        model.setData(model.index(row, 1), QVariant(font), Qt.FontRole)
        row += 1
    
    model.setHeaderData(0, Qt.Horizontal, QVariant("Name"))
    model.setHeaderData(1, Qt.Horizontal, QVariant("Address"))
    
    tree = QTreeView()
    tree.setModel(model)
    tree.show()
    
    table = QTableView()
    table.setModel(model)
    table.show()
    
    sys.exit(app.exec_())
