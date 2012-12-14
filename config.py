#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2012, Carles Pina'

from PyQt4.Qt import (Qt, QWidget, QVBoxLayout, QCheckBox, QPushButton)

from calibre.gui2 import dynamic, info_dialog
from calibre.utils.config import JSONConfig

from calibre_plugins.mendeley_to_calibre.common_utils import (get_library_uuid, KeyboardConfigDialog, PrefsViewerDialog)

plugin_prefs = JSONConfig('plugins/Mendeley')

class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
        QWidget.__init__(self)
	self.plugin_action = plugin_action

	self.l = QVBoxLayout()
	self.setLayout(self.l)

	self.cb_widget = QCheckBox('Test test.', self)
	self.l.addWidget(self.cb_widget)

    def save_settings(self):
        plugin_prefs['hidedldlg'] = self.cb_widget.isChecked()

    def edit
