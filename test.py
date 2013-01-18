#!/usr/bin/python

from mendeley_oapi import fetch
import sys
from pprint import pprint

sys.path.append('/home/carles/hackday_calibre/mendeley_oapi')

metaInformation = fetch.get_mendeley_documents()
pprint(metaInformation)
