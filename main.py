#!/usr/bin/python

from PyQt4.Qt import (QDialog, QGridLayout, QPushButton, QMessageBox, QLabel,
    QWidget, QVBoxLayout, QLineEdit, QIcon, QDialogButtonBox, QTimer, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from calibre_plugins.bbcgf_ebook.config import plugin_prefs
from calibre.utils.config import prefs as cprefs
from calibre.ebooks.conversion.config import load_defaults
from calibre.customize.conversion import OptionRecommendation
from calibre.ptempfile import PersistentTemporaryFile
from calibre.gui2 import Dispatcher, info_dialog

class MendeleyDialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
	self.gui = gui
	self.do_user_config = do_user_config

	self.db = gui.current_db

	self.l = QVBoxLayout()
	self.setLayout(self.l)

	self.setWindowTitle('Mendeley Plugin')
	self.setWindowIcon(icon)

	self.helpl = QLabel('Enter the URL of a bbcgoodfood.com recipe below.')
	self.l.addWidget(self.helpl)

       self.setMinimumWidth(500)
       self.resize(self.sizeHint())

    def about(self):
        QMessageBox.about(self, 'About', 'Some text here')
      
