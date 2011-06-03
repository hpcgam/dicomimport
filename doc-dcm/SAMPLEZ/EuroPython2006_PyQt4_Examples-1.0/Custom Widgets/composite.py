#!/usr/bin/env python

"""
composite.py

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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QGridLayout, QLabel, QLineEdit, \
     QTextEdit, QWidget

class AddressWidget(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        nameLabel = QLabel(self.tr("&Name:"))
        nameEdit = QLineEdit()
        nameLabel.setBuddy(nameEdit)
        addressLabel = QLabel(self.tr("&Address:"))
        addressEdit = QTextEdit()
        addressLabel.setBuddy(addressEdit)
        
        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(nameEdit, 0, 1)
        layout.addWidget(addressLabel, 1, 0, Qt.AlignTop)
        layout.addWidget(addressEdit, 1, 1)
        
        self.setLayout(layout)
        self.setWindowTitle(self.tr("Enter Name and Address"))

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = AddressWidget()
    window.show()
    sys.exit(app.exec_())
