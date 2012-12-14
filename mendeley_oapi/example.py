#!/usr/bin/env python

"""
Mendeley Open API Example Client

Copyright (c) 2010, Mendeley Ltd. <copyright@mendeley.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

For details of the Mendeley Open API see http://dev.mendeley.com/

Example usage:

python example.py

"""

from pprint import pprint
from mendeley_client import *
import os
import sys

def authors_to_string(authors):
    all_authors = ""
    for author in authors:
        if all_authors != "":
	    all_authors += ", "

	all_authors += author['forename'] + ' ' + author['surname']

    return all_authors

def get_mendeley_documents():
    documents = []
    # edit config.json first
    mendeley = create_client()

    folders = mendeley.folders()

    calibre_folder_id = -1
    for folder in folders:
        if folder['name'] == 'calibre':
            calibre_folder_id = folder['id']
    
    folder_documents = mendeley.folder_documents(calibre_folder_id)
    
    for document_id in folder_documents['document_ids']:
        document_detail = mendeley.document_details(document_id)
        title = document_detail['title']
        authors = authors_to_string(document_detail['authors'])
        document_id = document_detail['id']
    
        try:
            file_hash = document_detail['files'][0]['file_hash']
        except:	# to fix
            file_hash = None
    
    
        document = {}

	document["title"] = title
	document["authors"] = authors
	document["document_id"] = document_id
	document["file_hash"] = file_hash

        if file_hash != None:
            downloaded_file = mendeley.download_file(document_id,file_hash)
	    path = "/tmp/"+file_hash+".pdf"
	    pdf = open(path,"w")
	    pdf.write(downloaded_file["data"])
	    pdf.close()

	    document["path"] = path


	documents.append(document)

    return documents

if __name__ == "__main__":
    pprint(get_mendeley_documents())
