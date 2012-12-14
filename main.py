#!/usr/bin/python

from PyQt4.Qt import (QDialog, QGridLayout, QPushButton, QMessageBox, QLabel,
    QWidget, QVBoxLayout, QLineEdit, QIcon, QDialogButtonBox, QTimer, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from calibre_plugins.mendeley_to_calibre.config import plugin_prefs
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

	self.helpl = QLabel('You will import the library:')
	self.l.addWidget(self.helpl)

        self.setMinimumWidth(500)
        self.resize(self.sizeHint())

	self.startImportButton = QPushButton('Start Import')
	self.startImportButton.clicked.connect(self.startImport)
	self.l.addWidget(self.startImportButton)

    def startImport(self):
        file_name = '/home/carles/turing.pdf'
        self.gui.iactions['Add Books']._add_books([file_name], False)
	self.db = self.gui.current_db
	from calibre.ebooks.metadata import MetaInformation
	mi = MetaInformation('', [_('Unknown')])
	mi.title='here it is!'
	mi.authors = ['this is the author']
	mi.series_index = 1
	print mi
	self.db.add_books([file_name], ['pdf'], [mi])
	print "=============",self.db


    def about(self):
        QMessageBox.about(self, 'About', 'Some text here')
      
