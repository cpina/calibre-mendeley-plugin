#!/usr/bin/python

from PyQt4.Qt import (QDialog, QGridLayout, QPushButton, QMessageBox, QLabel,
    QWidget, QVBoxLayout, QLineEdit, QIcon, QDialogButtonBox, QTimer, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from calibre_plugins.mendeley_to_calibre.config import plugin_prefs
from calibre.utils.config import prefs as cprefs
from calibre.ebooks.conversion.config import load_defaults
from calibre.customize.conversion import OptionRecommendation
from calibre.ptempfile import PersistentTemporaryFile
from calibre.gui2 import Dispatcher, info_dialog
from calibre.gui2.threaded_jobs import ThreadedJob

import os

def do_work(abort, log, notifications):
    from calibre_plugins.mendeley_to_calibre.mendeley_oapi import fetch
    oapiConfig = fetch.OapiConfig()
    oapi = fetch.calibreMendeleyOapi(oapiConfig, abort, log, notifications)
    documents = oapi.get_mendeley_documents()
    return documents

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

        self.helpl = QLabel('Documents inside "calibre" subfolder will be imported now:')
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
        mi.tags = ["Mendeley"]

        mendeley_id = {}
        mendeley_id['mendeley'] = document['mendeley_id']

        mi.identifiers = mendeley_id
        mi.series_index = 1 # needed?

        self.db.add_books([document['path']], ['pdf'], [mi], False, True)

        os.remove(document['path'])

    def startImport(self):
        from calibre.utils.config import JSONConfig
        from pprint import pprint

        # plugin_prefs = JSONConfig('plugins/Mendeley')
        # pprint(plugin_prefs)

        job = ThreadedJob('Mendeley_importer',
                    'Importing Mendeley Documents',
                    func=do_work,
                    args=(),
                    kwargs={},
                    callback=self.importer_finished)

        self.gui.job_manager.run_threaded_job(job)

    def importer_finished(self,job):
        if job.failed:
            return self.gui.job_exception(job, dialog_title='Failed to download Mendeley documents')

        else:
            documents = job.result
            for document in documents:
                self.add_document(document)
        self.close()

    def about(self):
        QMessageBox.about(self, 'About', 'Some text here')
