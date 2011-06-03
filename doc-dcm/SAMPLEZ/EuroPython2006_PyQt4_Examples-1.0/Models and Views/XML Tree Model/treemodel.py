#!/usr/bin/env python

"""
treemodel.py

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

import os, sys

from optparse import OptionParser

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL
from PyQt4.uic import loadUi

from elementtree.ElementTree import parse, Element

class XPathElementTreeModel(QtCore.QAbstractItemModel):
    def buildMaps(self, parent, parentid):
        for rowidx, child in enumerate(parent):
            childid = self.makeEntry(child, parentid, rowidx)
            self.buildMaps(child, childid)
            
    def makeEntry(self, child, parentid, rowidx):
        childid = hash((parentid, id(child)))
        self._ne[childid] = child
        self._np[childid] = (parentid, rowidx)
        return childid
    

    def __init__(self, root, showRoot = True):
        QtCore.QAbstractItemModel.__init__(self)
        if showRoot:
            fakeroot = Element("fakeroot")
            fakeroot.append(root.getroot())
            self._root = fakeroot
        else:
            self._root = root.getroot()

        self._xpathroot = root
        self._realroot = self._root
        
        self._columns = ["Tag", "Attributes"]
        
        self._ne = {}
        self._np = {}
        self._ne[0] = self._root
        self.buildMaps(self._root, 0)
        self._neo = self._ne.copy()
        self._npo = self._np.copy()

        
    def setXPathExpr(self, expr):
        if expr == "":
            self._root = self._realroot
            self._ne = self._neo.copy()
            self._np = self._npo.copy()
        else: 
            try:
                #elems = self._xpathroot.xpath(unicode(expr))
                elems = list(self._xpathroot.findall(unicode(expr)))
                
                
                self._root = elems
                print self._root
                for rowidx, e in enumerate(elems):
                    if e == self._realroot:
                        continue
                    eid = self.makeEntry(e, 0, rowidx)
                    self.buildMaps(e, eid)
                    
            except (NotImplementedError, SyntaxError), e:
                return

        self.reset()
        
    
    def data(self, index, role):
        if not (index.isValid() and role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant()

        elem = self._ne[index.internalId()]
        if index.column() == 0:
            return QtCore.QVariant(elem.tag)
        else:
            return QtCore.QVariant(";".join("%s=\"%s\"" % (k, elem.attrib[k]) for k in elem.attrib))

    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._columns[section])
        
        return QtCore.QVariant()


    def index(self, row, column, parent):
        if parent.isValid():
            pitem = self._ne[parent.internalId()]
            pid = parent.internalId()
        else:
            pitem = self._root
            pid = 0

        return self.createIndex(row, column, hash((pid, id(pitem[row]))))

        
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        pitem, rowidx = self._np[index.internalId()]

        if pitem == 0:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(self._np[pitem][1], 0, pitem)

    
    def rowCount(self, parent):
        if parent.isValid():
            item = self._ne[parent.internalId()]
        else:
            item = self._root

        return len(item)


    def columnCount(self, parent):
        return len(self._columns)

class ElementTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root, showRoot = True):
        QtCore.QAbstractItemModel.__init__(self)
        if showRoot:
            fakeroot = Element("fakeroot")
            fakeroot.append(root)
            self._root = fakeroot
        else:
            self._root = root

        self._realroot = self._root
        
        self._columns = ["Tag", "Attributes"]
        
        self._np = dict((child, (parent, rowidx)) for parent in self._root.getiterator()
                        for rowidx, child in enumerate(parent))


    def data(self, index, role):
        if not (index.isValid() and role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant()

        elem = index.internalPointer()

        if index.column() == 0:
            return QtCore.QVariant(elem.tag)
        else:
            return QtCore.QVariant(";".join("%s=\"%s\"" % (k, elem.attrib[k]) for k in elem.attrib))

    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._columns[section])
        
        return QtCore.QVariant()


    def index(self, row, column, parent):
        if parent.isValid():
            pitem = parent.internalPointer()
        else:
            pitem = self._root

        return self.createIndex(row, column, pitem[row])

        
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        pitem, rowidx = self._np[index.internalPointer()]
        
        if id(pitem) == id(self._root):
            return QtCore.QModelIndex()
        else:
            return self.createIndex(self._np[pitem][1], 0, pitem)

    
    def rowCount(self, parent):
        if parent.isValid():
            item = parent.internalPointer()
        else:
            item = self._root

        return len(item)


    def columnCount(self, parent):
        return len(self._columns)


class OPMLModel(ElementTreeModel):
    def __init__(self, root):
        ElementTreeModel.__init__(self, root[1], False)
        self._columns = ["Text"]

        
    def data(self, index, role):
        if not (index.isValid() and role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant()
        
        return QtCore.QVariant(self._elems[index.internalId()].attrib["text"])


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <XML file>\n" % sys.argv[0])
        sys.exit(1)
    
    app = QtGui.QApplication(sys.argv)
    
    path = sys.argv[1]
    
    ui = loadUi(os.path.join(os.path.split(__file__)[0], "xmltreemodel.ui"))
    
    if True:
    
        def submit():
            model.setXPathExpr(ui.xpathline.text())
        
        model = XPathElementTreeModel(parse(path))
        QtCore.QObject.connect(ui.xpathline, SIGNAL("returnPressed()"), submit)
    else:
        model = ElementTreeModel(parse(path).getroot())
        
    ui.xmlview.setModel(model)
    ui.show()
    app.exec_()
