#!/usr/bin/env python

"""
treewidget.py

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
from PyQt4.QtGui import QApplication, QTreeWidget, QTreeWidgetItem

if __name__ == "__main__":

    app = QApplication(sys.argv)

    phonebook = {"Arthur": "Camelot",
                 "Monty": "The Circus",
                 "David": "Oslo"}
    
    tree = QTreeWidget()
    tree.setColumnCount(2)
    tree.setHeaderLabels(["Name", "Address"])
    
    for name, address in phonebook.items():
        item = QTreeWidgetItem(tree)
        item.setText(0, name)
        item.setText(1, address)
    
    tree.show()
    
    sys.exit(app.exec_())
