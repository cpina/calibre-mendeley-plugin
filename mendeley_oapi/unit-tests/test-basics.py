import sys
import unittest
import os

parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
os.sys.path.insert(0, parent_dir) 

from mendeley_client import *
from utils import test_prompt

class TestMendeleyClient(unittest.TestCase):

    client = create_client("../config.json")

    def clear_groups(self):
        for group in self.client.groups():
            self.client.delete_group(group["id"])
    
    def clear_folders(self):
        folders = self.client.folders()
        self.assertTrue("error" not in folders)
        for folder in self.client.folders():
            self.client.delete_folder(folder["id"])

    def clear_library(self):
        for doc in self.client.library()["document_ids"]:
            self.client.delete_library_document(doc)

    def is_folder(self, folder_id):
        ret = [f for f in self.client.folders() if f["id"] == folder_id]
        return len(ret) == 1

    @classmethod
    def setUpClass(self):
        self.client = create_client("../config.json")

    def tearDown(self):
        self.clear_folders()
        self.clear_groups()
        self.clear_library()
        
    ## Test Groups ##

    def test_create_open_groups(self):
        # Check that the user can create more than 2 open groups
        for i in range(5):
            self.assertTrue("error" not in self.client.create_group(group={"name":"test_open_group_%d"%i, "type":"open"}))

    def test_create_restricted_groups(self):

        # check that the user can't create more than 2 restricted groups
        types = ["private", "invite"]
        
        for group_type1 in types:
            first_group = self.client.create_group(group={"name":"test", "type":group_type1})
            self.assertTrue("group_id" in first_group)

            for group_type2 in types:
                response = self.client.create_group(group={"name":"test", "type":group_type2})
                self.assertEquals(response.status_code, 403)
            self.client.delete_group(first_group["group_id"])
   
    def test_create_group(self):
        # check that the user can create several open groups and one restricted group
        types = ["private", "invite"]
        for i in range(3):
            self.client.create_group(group={"name":"public_group_%d"%i, "type":"open"})
        for group_type in types:
            response = self.client.create_group(group={"name":"test_%s"%group_type, "type":group_type})
            self.assertTrue("error" not in response)
            self.client.delete_group(response["group_id"])


    ## Test Folder ##

    def test_create_folder_name_already_used(self):
        # check that the user can create two folders with the same name
        self.clear_folders()
        self.client.create_folder(folder={"name": "test"})
        rep = self.client.create_folder(folder={"name": "test"})
        self.assertFalse("error" in rep)

    def test_create_folder_valid(self):
        # check that the user can create folder 
        folder_name = "test"
        rep = self.client.create_folder(folder={"name": folder_name})
        folder_id = rep["folder_id"]
        folder_ = [folder for folder in self.client.folders() if folder["id"] == folder_id]
        self.assertEquals(folder_name, folder_[0]["name"])
        
    def test_delete_folder_valid(self):
        # check that the user can delete folder
        folder_name = "test"
        rep = self.client.create_folder(folder={"name": folder_name})
        folder_id = rep["folder_id"]
        resp = self.client.delete_folder(folder_id)
        self.assertTrue("error" not in rep)

    def test_delete_folder_invalid(self):
        # check that the user can't delete a folder owned by an other user (or non-existent)
        invalid_ids = ["1234567890123", "-1234567890123", "-1", "","some string"]
        for invalid_id in invalid_ids:
            self.assertFalse(self.client.delete_folder(invalid_id))

    def test_parent_folder(self):
        parent_id = None
        folder_ids = []
        
        # create top level folder and 3 children 
        for i in range(4):
            data={"name": "folder_%d"%i}
            if parent_id:
                data["parent"] = parent_id
            folder = self.client.create_folder(folder=data)
            self.assertTrue("folder_id" in folder)
            if parent_id:
                self.assertTrue("parent" in folder and str(folder["parent"]) == parent_id)

            # update the list of folder_ids
            folder_ids.append(folder["folder_id"])
            parent_id = folder_ids[-1]
        
        # delete last folder and check it"s gone and that its parent still exists
        response = self.client.delete_folder(folder_ids[-1]) 
        self.is_folder(folder_ids[-1])
        del folder_ids[-1]
        self.assertTrue(response)

        # add another folder on the bottom and delete its parent
        # check both are deleted and grandparent still ok
        parent_id = folder_ids[-1]
        grandparent_id = folder_ids[-2]

        #  Create the new folder
        folder = self.client.create_folder(folder={"name":"folder_4", "parent":parent_id})
        new_folder_id = folder["folder_id"]
        folder_ids.append(new_folder_id)
        self.assertTrue("parent" in folder and str(folder["parent"]) == parent_id)
        
        #  Delete the parent and check the parent and new folder are deleted
        deleted = self.client.delete_folder(parent_id)
        self.assertTrue(deleted)
        self.assertFalse(self.is_folder(new_folder_id))
        del folder_ids[-1] # new_folder_id
        self.assertFalse(self.is_folder(parent_id))
        del folder_ids[-1] # parent_id
        self.assertTrue(self.is_folder(grandparent_id))
        
        # delete top level folder and check all children are deleted
        top_folder = self.client.delete_folder(folder_ids[0])
        for folder_id in folder_ids:
            self.assertFalse(self.is_folder(folder_id))
        
        self.assertEqual(len(self.client.folders()), 0)

    ## Test Other ##
    
    def test_get_starred_documents(self):
        document = self.client.create_document(document={"type" : "Book","title": "starred_doc_test", "year": 2025, "isStarred": 1})
        self.assertTrue("document_id" in document)
        self.assertTrue("version" in document)

        response = self.client.documents_starred()
        self.assertEquals(response["documents"][0]["id"], document["document_id"])
        self.assertEquals(response["documents"][0]["version"], document["version"])

    def test_create_doc_from_canonical(self):
        canonical_id = "26a21bf0-6d00-11df-a2b2-0026b95e3eb7"
        document = self.client.create_document_from_canonical(canonical_id=canonical_id)
        self.assertTrue("document_id" in document)
        self.assertTrue("version" in document)

        canonical_metadata = self.client.details(canonical_id)
        library_metadata = self.client.document_details(document["document_id"])
        
        self.assertEquals(canonical_metadata["title"], library_metadata["title"])

    def test_add_doc_to_folder_valid(self):
        document = self.client.create_document(document={"type" : "Book","title": "doc_test", "year": 2025})
        doc_id = document["document_id"]
        folder = self.client.create_folder(folder={"name": "Test"})
        folder_id = folder["folder_id"]
        response = self.client.add_document_to_folder(folder_id, doc_id)
        self.assertTrue("error" not in response )

    def test_add_doc_to_folder_invalid(self):
        document = self.client.create_document(document={"type" : "Book","title": "doc_test", "year": 2025})
        document_id = document["document_id"]
        invalid_folder_ids = ["some string", "-1", "156484", "", "-2165465465"]
        for invalid_folder_id in invalid_folder_ids:
            response = self.client.add_document_to_folder(invalid_folder_id, document_id)
            self.assertTrue(response.status_code == 404 or response.status_code == 400)
        
        folder = self.client.create_folder(folder={"name": "Test"})
        self.assertTrue("error" not in folder)

        invalid_document_ids = ["some string", "-1", "156484", "", "-2165465465"]

        folder_id = folder["folder_id"]
        
        for invalid_document_id in invalid_document_ids:
            response = self.client.add_document_to_folder(folder_id, invalid_document_id)
            self.assertTrue(response.status_code == 404 or response.status_code == 400)
        
    def test_download_invalid(self):
        self.assertEquals(self.client.download_file("invalid", "invalid").status_code, 400)

    def test_upload_pdf(self):
        file_to_upload = "../example.pdf"

        hasher = hashlib.sha1()
        hasher.update(open(file_to_upload, "rb").read())
        expected_file_hash = hasher.hexdigest()
        expected_file_size = str(os.path.getsize(file_to_upload))

        response = self.client.create_document(document={"type":"Book", "title":"Ninja gonna be flyin"})
        self.assertTrue("error" not in response)
        document_id = response["document_id"]

        # upload the pdf
        upload_result = self.client.upload_pdf(document_id, file_to_upload)

        # get the details and check the document now has files
        details = self.client.document_details(document_id)
        self.assertEquals(len(details["files"]), 1)

        document_file = details["files"][0]
        self.assertEquals(document_file["file_extension"], "pdf")
        self.assertEquals(document_file["file_hash"], expected_file_hash)
        self.assertEquals(document_file["file_size"], expected_file_size)

        # delete the document
        self.assertTrue(self.client.delete_library_document(document_id))

    def test_download_pdf(self):
        file_to_upload = "../example.pdf"

        hasher = hashlib.sha1(open(file_to_upload, "rb").read())
        expected_file_hash = hasher.hexdigest()
        expected_file_size = os.path.getsize(file_to_upload)

        response = self.client.create_document(document={"type":"Book", "title":"Ninja gonna be flyin"})
        self.assertTrue("error" not in response)
        document_id = response["document_id"]

        # upload the pdf
        upload_result = self.client.upload_pdf(document_id, file_to_upload)
        
        def download_and_check(with_redirect):
            # download the file back
            response = self.client.download_file(document_id, expected_file_hash, with_redirect=with_redirect)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("data" in response and "filename" in response)

            # check that the downloaded file is the same as the uploaded one
            data = response['data']
            size = len(data)
            actual_file_hash = hashlib.sha1(data).hexdigest()
            self.assertEquals(size, expected_file_size)
            self.assertEquals(actual_file_hash, expected_file_hash)

        download_and_check(with_redirect="true")
        download_and_check(with_redirect="false")


if __name__ == "__main__":
    if not test_prompt():
        print "Aborting"
        sys.exit(1)
    print ""
    unittest.main()
