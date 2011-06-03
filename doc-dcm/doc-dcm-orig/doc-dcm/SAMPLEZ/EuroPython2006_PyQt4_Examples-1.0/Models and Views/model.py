#!/usr/bin/env python

"""
model.py

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
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, QRectF, QSize, Qt, \
     QVariant, SIGNAL, SLOT
from PyQt4.QtGui import QAbstractItemDelegate, QApplication, QBrush, \
     QCheckBox, QComboBox, QGridLayout, QImage, QLabel, QPainter, QSpinBox, \
     QStyle, QTableView, QWidget, qGray

import image_resources

ItemSize = 256


class PixelDelegate(QAbstractItemDelegate):
    def __init__(self, parent=None):
        QAbstractItemDelegate.__init__(self,parent)

        self.pixelSize = 7
    
    def paint(self, painter, option, index):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if option.state & QStyle.State_Selected:
            painter.setBrush(option.palette.highlight())
        else:
            painter.setBrush(QBrush(Qt.white))
        
        painter.drawRect(option.rect)
        
        if option.state & QStyle.State_Selected:
            painter.setBrush(option.palette.highlightedText())
        else:
            painter.setBrush(QBrush(Qt.black))

        size = min(option.rect.width(), option.rect.height())
        brightness, ok = index.model().data(index, Qt.DisplayRole).toInt()
        radius = (size/2.0) - (brightness/255.0 * size/2.0)
        painter.drawEllipse(QRectF(
                            option.rect.x() + option.rect.width()/2 - radius,
                            option.rect.y() + option.rect.height()/2 - radius,
                            2*radius, 2*radius))
    
    def sizeHint(self, option, index):
        return QSize(self.pixelSize, self.pixelSize)
    
    def setPixelSize(self, size):
        self.pixelSize = size


class ImageModel(QAbstractTableModel):
    def __init__(self, image, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.modelImage = QImage(image)

    def rowCount(self, parent):
        return self.modelImage.height()

    def columnCount(self, parent):
        return self.modelImage.width()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        
        return QVariant(qGray(self.modelImage.pixel(index.column(), index.row())))


class Window(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self.table = QTableView()
        self.imageTable = QTableView()
        delegate = PixelDelegate(self)
        self.imageTable.setItemDelegate(delegate)
        self.imageTable.horizontalHeader().hide()
        self.imageTable.verticalHeader().hide()
        self.imageTable.setShowGrid(False)
        
        self.imageCombo = QComboBox()
        self.imageCombo.addItem("Dream", QVariant(":/Pictures/dream.png"))
        self.imageCombo.addItem("Teapot", QVariant(":/Pictures/teapot.png"))
        
        gridCheckBox = QCheckBox(self.tr("Show grid:"))
        gridCheckBox.setCheckState(Qt.Unchecked)
        
        self.connect(self.imageCombo, SIGNAL("currentIndexChanged(int)"),
                     self.setModel)
        self.connect(gridCheckBox, SIGNAL("toggled(bool)"),
                     self.imageTable, SLOT("setShowGrid(bool)"))
        
        self.imageCombo.setCurrentIndex(1)
        
        layout = QGridLayout()
        layout.addWidget(self.imageTable, 0, 0, 1, 2)
        layout.addWidget(self.table, 0, 2, 1, 2)
        layout.addWidget(gridCheckBox, 1, 0)
        layout.addWidget(self.imageCombo, 1, 1)
        self.setLayout(layout)
    
    def setModel(self, row):
    
        image = QImage(self.imageCombo.itemData(row).toString())
        model = ImageModel(image, self)
        self.table.setModel(model)
        self.imageTable.setModel(model)
        
        for row in range(model.rowCount(QModelIndex())):
            self.imageTable.resizeRowToContents(row)
        for column in range(model.columnCount(QModelIndex())):
            self.imageTable.resizeColumnToContents(column)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
