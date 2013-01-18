#!/usr/bin/env python

from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = 'GPL v3'
__copyright__ = '2012, 2013, Carles Pina'

from PyQt4.Qt import (Qt, QWidget, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QLabel, QFormLayout)

from calibre.gui2 import dynamic, info_dialog
from calibre.utils.config import JSONConfig

from mendeley_oapi import fetch
from mendeley_oapi import mendeley_client

# from calibre_plugins.mendeley_to_calibre.common_utils import (get_library_uuid, KeyboardConfigDialog, PrefsViewerDialog)

plugin_prefs = JSONConfig('plugins/Mendeley')

class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
        QWidget.__init__(self)
	self.plugin_action = plugin_action

	self.layout = QFormLayout()
	self.label = QLabel()
	self.label.setOpenExternalLinks(True)
	
	oapiConfig = OapiConfig()
        oapi = fetch.MendeleyOapi(oapiConfig)
	url = oapi.getVerificationUrl()

	self.label.setText('<a href="http://%s">Press Here</a>' % url)
	self.setLayout(self.layout)

	self.api_key = QLineEdit(self)

	self.layout.addWidget(self.label)
	self.layout.addRow('Verification Code',self.api_key)
	self.api_key.setText(plugin_prefs['api_key'])

    def save_settings(self):
        plugin_prefs['api_key'] = str(self.api_key.text())
