#!/usr/bin/python

from mendeley_oapi import fetch
from mendeley_oapi import mendeley_client
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
    verification = str(verification)
    oapi.setVerificationCode(verification)
    
    tokens_store = mendeley_client.MendeleyTokensStore('/tmp/keys_api.mendeley.com.pkl')
    tokens_store.add_account('test_account',oapi.mendeley.get_access_token())
    tokens_store = 0
    print "Here"


documents = oapi.get_mendeley_documents()
pprint(documents)
