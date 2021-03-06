#!/usr/bin/python

#~ This file is part of NoStaples.

#~ NoStaples is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ NoStaples is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with NoStaples.  If not, see <http://www.gnu.org/licenses/>.

"""
This module holds the PreferencesModel, which manages user settings.
"""

import logging

from gtkmvc.model import Model

from nostaples import constants
from nostaples.utils import properties

class PreferencesModel(Model):
    """
    Manages user settings.
    """
    __properties__ = \
    {
        'preview_mode' : constants.DEFAULT_PREVIEW_MODE,
        'thumbnail_size' : constants.DEFAULT_THUMBNAIL_SIZE,
        'toolbar_style' : constants.DEFAULT_TOOLBAR_STYLE,
        
        'blacklisted_scanners' : [],    # List of scanner display names
        
        'saved_keywords' : '',
    }

    def __init__(self, application):
        """
        Constructs the PreferencesModel.
        """
        Model.__init__(self)
        self.application = application
        
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.log.debug('Created.')
        
    def load_state(self):
        """
        Load persisted state from the self.state_manager.
        """
        state_manager = self.application.get_state_manager()
        
        self.preview_mode = state_manager.init_state(
            'preview_mode', constants.DEFAULT_PREVIEW_MODE, 
            properties.GuardedPropertyStateCallback(
                self, 'preview_mode', constants.PREVIEW_MODES_LIST))
        
        self.thumbnail_size = state_manager.init_state(
            'thumbnail_size', constants.DEFAULT_THUMBNAIL_SIZE, 
            properties.GuardedPropertyStateCallback(
                self, 'thumbnail_size', constants.THUMBNAIL_SIZE_LIST))
        
        self.toolbar_style = state_manager.init_state(
            'toolbar_style', constants.DEFAULT_TOOLBAR_STYLE, 
            properties.GuardedPropertyStateCallback(
                self, 'toolbar_style', constants.TOOLBAR_STYLES_LIST))
        
        self.blacklisted_scanners = state_manager.init_state(
            'blacklisted_scanners', constants.DEFAULT_BLACKLISTED_SCANNERS, 
            properties.PropertyStateCallback(self, 'blacklisted_scanners'))
        
        self.saved_keywords = state_manager.init_state(
            'saved_keywords', constants.DEFAULT_SAVED_KEYWORDS, 
            properties.PropertyStateCallback(self, 'saved_keywords'))
        
    # PROPERTY SETTERS
        
    set_prop_preview_mode = properties.StatefulPropertySetter(
        'preview_mode')
    set_prop_thumbnail_size = properties.StatefulPropertySetter(
        'thumbnail_size')
    set_prop_toolbar_style = properties.StatefulPropertySetter(
        'toolbar_style')
    set_prop_blacklisted_scanners = properties.StatefulPropertySetter(
        'blacklisted_scanners')
    set_prop_saved_keywords = properties.StatefulPropertySetter(
        'saved_keywords')