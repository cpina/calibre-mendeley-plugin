#!/usr/bin/python

# "THE CHOCOLATE-WARE LICENSE" (Revision 1):
# <carles@pina.cat> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some
# day, and you think this stuff is worth it, you can buy me a chocolate in
# return. - Carles Pina Estany
# (license based in Beer-ware, see
#           https://fedoraproject.org/wiki/Licensing/Beerware )

from PyQt4.Qt import (QDialog, QGridLayout, QPushButton, QMessageBox, QLabel,
    QWidget, QVBoxLayout, QLineEdit, QIcon, QDialogButtonBox, QTimer, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator)

from calibre_plugins.mendeley_to_calibre.config import plugin_prefs
from calibre.utils.config import prefs as cprefs
from calibre.ebooks.conversion.config import load_defaults
from calibre.customize.conversion import OptionRecommendation
from calibre.ptempfile import PersistentTemporaryFile
from calibre.gui2 import Dispatcher, info_dialog
from calibre.gui2.threaded_jobs import ThreadedJob
from mendeley_oapi import mendeley_client

import os

def do_work(abort, log, notifications):
    from calibre_plugins.mendeley_to_calibre.mendeley_oapi import fetch
    oapiConfig = fetch.OapiConfig()

    tokens_store = mendeley_client.MendeleyTokensStore()

    # TODO: Check if account exists
    tokens_store.loads(plugin_prefs['account'])

    oapi = fetch.calibreMendeleyOapi(oapiConfig, tokens_store, abort, log, notifications)
    documents = oapi.get_mendeley_documents()
    return documents

class MendeleyDialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.db = gui.current_db

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('Mendeley Plugin')
        self.setWindowIcon(icon)

        self.setMinimumWidth(500)
        self.resize(self.sizeHint())

        self.startImportButton = QPushButton('Import documents from \'calibre\' Mendeley folder.')
        self.startImportButton.clicked.connect(self.startImport)
        self.layout.addWidget(self.startImportButton)
        
        self.helpl = QLabel('\n')
        self.helpl.setWordWrap(True)
        self.layout.addWidget(self.helpl)
        
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

        plugin_prefs = JSONConfig('plugins/Mendeley')

        job = ThreadedJob('Mendeley_importer',
                    'Importing Mendeley Documents',
                    func=do_work,
                    args=(),
                    kwargs={},
                    callback=self.importer_finished)

        self.gui.job_manager.run_threaded_job(job)

        self.startImportButton.setEnabled(False)
        self.helpl.setText('Importing documents. You can close the dialog. See the progress in the Calibre jobs (see the Status Bar).')

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
