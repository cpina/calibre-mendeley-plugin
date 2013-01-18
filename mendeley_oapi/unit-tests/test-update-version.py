import os
import sys
import time
import unittest

from utils import *
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
os.sys.path.insert(0, parent_dir) 
from mendeley_client import *

class TestEnv:
    client = None
    sleep_time = 1 

class TestDocumentUpdate(unittest.TestCase):

    # Tests
    def setUp(self):
        self.test_document = TestEnv.client.create_document(document={'type' : 'Book',
                                                                      'title': 'Document creation test', 
                                                                      'year': 2008})
    def tearDown(self):
        TestEnv.client.delete_library_document(self.test_document["document_id"])  

    def update_doc(self, obj):
        document_id = self.test_document["document_id"]
        response = TestEnv.client.update_document(document_id, document=obj)  
        if isinstance(response, requests.Response) and "error" in response.json:
            return False, response.json
        updated_details = TestEnv.client.document_details(document_id)
        return self.compare_documents(updated_details, obj), response

    def update_and_check(self, obj, expected_match):
        match, response = self.update_doc(obj)
        self.assertEqual("error" in response, not expected_match)
        self.assertEqual(match, expected_match)        
    
    def compare_documents(self, docA, docB):
        """Return True if docA[key] == docB[key] for keys in docB
        if docA has extra keys, they are ignored"""

        for key in docB.keys():
            if not key in docA or docA[key] != docB[key]:
                return False
        return True
    
    @timed
    @delay(TestEnv.sleep_time)
    def test_valid_update(self):
        info = {"type":"Book Section",
                "title":"How to kick asses when out of bubble gum",
                "authors":[ {"forename":"Steven", "surname":"Seagal"}, 
                            {"forename":"Dolph","surname":"Lundgren"}],
                "year":"1998"
                }
        self.update_and_check(info, True)

    @timed
    @delay(TestEnv.sleep_time)
    def test_valid_update_no_delay(self):
        info = {"type":"Book Section"}
        self.update_and_check(info, True)
        #Do a request without delay - the request should fail if done in less than a second from the previous create/update due to the rate limiting (one update per second per document)
        #Please note this test might fail if the previous update_and_check takes longer than a second to run.
        info = {"year":"1998"}
        self.update_and_check(info, False)
        #Sleeping again and doing the update should work then
        time.sleep(1)
        self.update_and_check(info, True)


    @timed
    @delay(TestEnv.sleep_time)
    @skip('skipping until format is fixed.')
    def test_authors_format(self):
        self.update_and_check({"authors":[ ["Steven", "Seagal"], ["Dolph","Lundgren"]]}, False)
        self.update_and_check({"authors":[ ["Steven Seagal"], ["Dolph Lundgren"]]}, False)
        self.update_and_check({"authors":"bleh"}, False)
        self.update_and_check({"authors":-1}, False)
        self.update_and_check({"authors":[ {"forename":"Steven", "surname":"Seagal"}, 
                                           {"forename":"Dolph","surname":"Lundgren"}]}, True)

    @timed
    @delay(TestEnv.sleep_time)
    @skip('skipping until value type is fixed.')
    def test_invalid_field_type(self):
        # year is a string not a number
        self.update_and_check({"year":1998}, False)

    @timed
    @delay(TestEnv.sleep_time)
    def test_invalid_document_type(self):
        self.update_and_check({"type":"Cat Portrait"}, False)
        
    @timed
    @delay(TestEnv.sleep_time)
    def test_invalid_field(self):
        self.update_and_check({"shoesize":1}, False)

    @timed
    @delay(TestEnv.sleep_time)
    def test_readonly_field(self):
        self.update_and_check({"uuid": "0xdeadbeef"}, False)
        
class TestDocumentVersion(unittest.TestCase):

    # Utils
    def verify_version(self, obj, expected):
        delta = abs(obj["version"]-expected)
        self.assertTrue(delta < 300)        
    
    # Tests
    def setUp(self):
        self.test_document = TestEnv.client.create_document(document={'type' : 'Book',
                                                                        'title': 'Document creation test', 
                                                                        'year': 2008})
    def tearDown(self):
        TestEnv.client.delete_library_document(self.test_document["document_id"])

    @timed
    def test_version_returned(self):
        """Verify that the version is returned on creation, details and listing"""
        now = timestamp()

        # verify that we get a version number when creating a document
        # at the moment it is the timestamp of creation, so check that it's around
        # the current UTC timestamp (see verify_version)
        created_version = self.test_document["version"]
        self.verify_version(self.test_document, now)

        # verify that the list of documents returns a version and that
        # it matches the version returned earlier
        document_id = self.test_document['document_id']
        documents = TestEnv.client.library()
        self.assertTrue(document_id in documents['document_ids'])

        found_document = None
        for document in documents['documents']:
            if document["id"] == document_id:
                found_document = document
                break
        self.assertTrue(found_document)
        self.assertEqual(found_document["version"], created_version)

        # verify that the document details have the same version
        details = TestEnv.client.document_details(document_id)
        self.assertEqual(details["version"], created_version)

    @timed
    @delay(TestEnv.sleep_time)
    def test_version_on_document_update(self):
        """Verify that an update increases the version number"""
        # sleep a bit to avoid receiving the same timestamp between create and update
        current_version = self.test_document["version"]
        response = TestEnv.client.update_document(self.test_document["document_id"], document={"title":"updated title"})
        self.assertTrue("version" in response)
        self.assertTrue(response["version"] > current_version)

    @timed
    @delay(TestEnv.sleep_time)
    def test_version_on_document_folder_update(self):
        # sleep a bit to avoid receiving the same timestamp between create and update

        folder = TestEnv.client.create_folder(folder={"name":"test"})
        self.assertTrue("version" in folder)
        current_version = self.test_document["version"]
        response = TestEnv.client.add_document_to_folder(folder["folder_id"], self.test_document["document_id"])

        # verify that the document version changed
        created_version = self.test_document["version"]
        details = TestEnv.client.document_details(self.test_document["document_id"])
        self.assertTrue(details["version"] > created_version)        

        TestEnv.client.delete_folder(folder["folder_id"])

def main(config_file):
    client = create_client(config_file)

    # verify that the version number is available on this server before running all the tests
    document = TemporaryDocument(client).document()
    if not "version" in document:
        print "The server doesn't support functionalities required by this test yet"
        sys.exit(1)

    TestEnv.client = client
    unittest.main()

if __name__ == '__main__':
    main(get_config_file())

