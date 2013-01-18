#!/usr/bin/env python

from pprint import pprint
from mendeley_client import *
import os
import sys

# edit config.json first
mendeley = create_client('/home/carles/config.json')

########################################
######## Public Resources Tests ########
########################################

def getFolderId(folders, name):
    for folder in folders:
        if folder['name'] == name:
	    return folder['id']

    return None

def authorsToString(authors):
    a = ''

    for author in authors:
        a += author['surname'] + ',' + author['forename']

    return a

def downloadFile(document):
    if document.has_key('files'):
        file_hash = document['files'][0]['file_hash']
	document_id = document['id']

        path = '/tmp/' + file_hash + '.pdf'
        file_content = mendeley.download_file(document_id, file_hash)
	f=open(path, 'w')
	f.write(str(file_content))
	f.close()

	return path

    return ''

def getDocumentMetaInformation(document_id):
    document = mendeley.document_details(document_id)
    d = {}
    d['title'] = document['title']
    d['authors'] = authorsToString(document['authors'])
    d['path'] = downloadFile(document)
    return d

def getDocumentsMetaInformation(documents):
    documents_information = []
    for document in documents['documents']:
	documents_information.append(getDocumentMetaInformation(document['id']))

    return documents_information

def get_mendeley_documents():
    folders = mendeley.folders()

    folderId = getFolderId(folders, 'calibre')

    documents = mendeley.folder_documents(folderId)
    documents_information = getDocumentsMetaInformation(documents)

    return documents_information
