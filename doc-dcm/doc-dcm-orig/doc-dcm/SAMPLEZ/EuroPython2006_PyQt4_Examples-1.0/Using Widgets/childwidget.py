#!/usr/bin/env python

"""
childwidget.py

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
from PyQt4.QtGui import QApplication, QPushButton, QWidget

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QWidget()
    window.resize(480, 360)
    window.show()
    
    button = QPushButton("Press me", window)
    button.move(200, 200)
    button.show()
    
    sys.exit(app.exec_())
