#!/usr/bin/env python

"""
painting.py

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

import math, sys
from PyQt4.QtCore import QPointF, QRectF, QSize
from PyQt4.QtGui import QApplication, QBrush, QColor, QLinearGradient, \
     QPainter, QPainterPath, QWidget, qApp

class CustomWidget(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self.path = QPainterPath()
        angle = 2*math.pi/5
        self.path.moveTo(50, 0)
        for step in range(1, 6):
            self.path.lineTo(20 * math.cos((step - 0.5) * angle), 20 * math.sin((step - 0.5) * angle))
            self.path.lineTo(50 * math.cos(step * angle), 50 * math.sin(step * angle))
        self.path.closeSubpath()

        start = QPointF(0, 100)
        stop = QPointF(100, 0)
        self.gradient = QLinearGradient(start, stop)
        self.gradient.setColorAt(0.15, QColor(255, 0, 128))
        self.gradient.setColorAt(0.4, QColor(255, 255, 128))
        self.gradient.setColorAt(0.5, QColor(255, 255, 255))
        self.gradient.setColorAt(0.6, QColor(255, 255, 128))
        self.gradient.setColorAt(0.85, QColor(255, 0, 128))
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(192, 192, 255)))
        painter.drawRect(event.rect())
        
        painter.translate(self.width()/2.0, self.height()/2.0)
        painter.scale(self.width()*0.75/100.0, self.height()*0.75/100.0)
        painter.setBrush(QBrush(self.gradient))
        painter.drawPath(self.path)
        painter.end()
    
    def sizeHint(self):
    
        return QSize(200, 200)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = CustomWidget()
    window.show()
    sys.exit(app.exec_())
