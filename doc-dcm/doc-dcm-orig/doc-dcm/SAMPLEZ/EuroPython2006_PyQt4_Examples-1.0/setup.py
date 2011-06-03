#! /usr/bin/env python

"""
setup.py

Copyright (C) 2006 David Boddie

This file is part of the package containing the examples for the "Introducing
PyQt4 for GUI Application Development" talk given at EuroPython 2006 at CERN,
Geneva, Switzerland.

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

from distutils.core import setup

__version__ = "1.0"

setup(
    name="EuroPython2006_PyQt4_Examples",
    version=__version__,
    author="David Boddie",
    author_email="david@boddie.org.uk",
    url="http://indico.cern.ch/contributionDisplay.py?contribId=33&sessionId=41&confId=44",
    description="PyQt4 examples from a talk at EuroPython 2006.",
    long_description='This package contains the examples for the "Introducing '
                     'PyQt4 for GUI Application Development" talk given at '
                     'EuroPython 2006 at CERN, Geneva, Switzerland.',
    download_url="http://cheeseshop.python.org/packages/source/E/EuroPython2006_PyQt4_Examples/EuroPython2006_PyQt4_Examples-%s.zip" % __version__
    )
