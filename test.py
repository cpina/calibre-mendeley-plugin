#!/usr/bin/python

from mendeley_oapi import fetch
import sys
from pprint import pprint

sys.path.append('/home/carles/hackday_calibre/mendeley_oapi')

class OapiConfig:
    def __init__(self):
        setattr(self,'api_key', 'c168ce62964a4900e66d9361bda9cb3a04cf98732')
	setattr(self,'api_secret', '7d4294168e43807651faf051510c707b')
	setattr(self,'host', 'api.mendeley.com')

oapiConfig = OapiConfig()

oapi = fetch.MendeleyOapi(oapiConfig)

if oapi.isValid():
    metaInformation = oapi.get_mendeley_documents()
    pprint(metaInformation)
else:
    print "URL:",oapi.getVerificationUrl()
    verification = raw_input('write verification')
    oapi.setVerificationCode(verification)

documents = oapi.get_mendeley_documents()
pprint(documents)
