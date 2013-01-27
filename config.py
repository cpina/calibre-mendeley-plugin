#!/usr/bin/env python

from __future__ import (division, absolute_import, print_function)

__license__   = 'GPL v3'
__copyright__ = '2012, 2013, Carles Pina'

from PyQt4.Qt import (Qt, QWidget, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QLabel, QFormLayout)

from calibre.gui2 import dynamic, info_dialog
from calibre.utils.config import JSONConfig

# from calibre_plugins.mendeley_to_calibre.common_utils import (get_library_uuid, KeyboardConfigDialog, PrefsViewerDialog)

plugin_prefs = JSONConfig('plugins/Mendeley')

class OapiConfig:
    def __init__(self):
        setattr(self,'api_key', 'c168ce62964a4900e66d9361bda9cb3a04cf98732')
        setattr(self,'api_secret', '7d4294168e43807651faf051510c707b')
        setattr(self,'host', 'api.mendeley.com')

class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
        from calibre_plugins.mendeley_to_calibre.mendeley_oapi import fetch
        from calibre_plugins.mendeley_to_calibre.mendeley_oapi import mendeley_client

        QWidget.__init__(self)
        self.plugin_action = plugin_action

        self.layout = QFormLayout()
        self.label = QLabel()
        self.label.setOpenExternalLinks(True)
        
        oapiConfig = OapiConfig()
        self.oapi = fetch.calibreMendeleyOapi(oapiConfig)
        self.oapi.isValid()
        url = self.oapi.getVerificationUrl()
        link = '<a href="%s">Press Here</a>' % (url)

        self.label.setText(link)
        self.setLayout(self.layout)

        self.api_key = QLineEdit(self)

        self.layout.addWidget(self.label)
        self.layout.addRow('Verification Code',self.api_key)
        self.api_key.setText(plugin_prefs['api_key'])

    def save_settings(self):
        from calibre_plugins.mendeley_to_calibre.mendeley_oapi import mendeley_client
        print("SAVE SETTINGS",str(self.api_key.text()))
        plugin_prefs['verification'] = str(self.api_key.text())
        self.oapi.setVerificationCode(str(self.api_key.text()))
        tokens_store = mendeley_client.MendeleyTokensStore('/tmp/keys_api.mendeley.com.pkl')
        tokens_store.add_account('test_account',self.oapi.mendeley.get_access_token())
        tokens_store = 0 # force delete
        print("Here")
