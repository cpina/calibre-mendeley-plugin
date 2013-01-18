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

    def add_document(self,document):
	from calibre.ebooks.metadata import MetaInformation

	mi = MetaInformation('', [_('Unknown')])
	mi.title = document['title']
	mi.authors = document['authors']
	mi.series_index = 1 # needed?

        self.db.add_books([document['path']], ['pdf'], [mi])

    def startImport(self):
        import sys
	from mendeley_oapi import fetch
	# sys.path.append('/home/carles/hackday_calibre/mendeley_oapi')

	documents = fetch.get_mendeley_documents()

        for document in documents:
	    self.add_document(document)

	self.close()

    def about(self):
        QMessageBox.about(self, 'About', 'Some text here')
      
