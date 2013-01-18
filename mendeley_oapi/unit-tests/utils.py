import calendar
import os
import sys
import time

def timed(fn):
    def wrapped(*args, **kwargs):
        now = time.time()
        res = fn(*args, **kwargs)
        delta = time.time()-now
        print "\n%s took\t%5.3fs"%(fn.__name__,delta)
        return res
    return wrapped

def skip(reason):
    def wrappedskip(fn):
        def wrapped(*args, **kwargs):
            print "Skipping %(function)s:  %(reason)s" % {"function" : fn.__name__, "reason": reason}
            return
        wrapped.__name__=fn.__name__
        return wrapped
    return wrappedskip

def timestamp():
    n = time.gmtime()
    return calendar.timegm(n)

def delay(period):
    def wrappedperiod(fn):
        def wrapped(*args, **kwargs):
            time.sleep(period)
            res = fn(*args, **kwargs)
            return res
        wrapped.__name__=fn.__name__
        return wrapped
    return wrappedperiod

def get_config_file():
    config_file = "../config.json"
    if len(sys.argv) > 1:
        _, file_ext = os.path.splitext(sys.argv[1])
        if file_ext == ".json":
            config_file = sys.argv[1]
            del sys.argv[1]    
    return config_file

class TemporaryDocument:

    def __init__(self, client):
        self.__client = client
        self.__document = client.create_document(document={'type' : 'Book', 
                                                           'title': 'Document creation test'})
        assert "document_id" in self.__document

    def document(self):
        return self.__document

    def __del__(self):
        assert self.__client.delete_library_document(self.__document["document_id"])
        
def test_prompt():
    print "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!! This test will reset the library of the account used for testing !!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
    inp = raw_input("If you are okay with this, please type 'yes' to continue: ")
    return inp == "yes"
