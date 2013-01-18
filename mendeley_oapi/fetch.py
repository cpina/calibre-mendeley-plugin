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

def getDocumentMetaInformation(document_id):
    document = mendeley.document_details(document_id)
    d = {}
    d['title'] = document['title']
    d['authors'] = authorsToString(document['authors'])
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
