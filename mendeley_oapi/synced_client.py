from mendeley_client import *

class SyncStatus:
    Deleted = 0
    Modified = 1
    New = 2
    Synced = 3   

    @staticmethod
    def to_str(status):
        return ["DEL","MOD","NEW","SYN"][status]

class Object:
    pass

class SyncedObject:

    def __init__(self, obj, status=SyncStatus.New):
        self.reset(obj, status)
        
    def reset(self, obj, status):
        self.changes = {}
        self.status = status

        if isinstance(obj, dict):
            self.object = Object()
            for key in obj.keys():
                setattr(self.object, key, obj[key])
        elif isinstance(obj, SyncedObject):
            self.object = obj.object
        else:
            assert False

    def version(self):
        if not hasattr(self.object, "version"):
            return None
        return self.object.version

    def id(self):
        if not hasattr(self.object, "id"):
            return None
        return self.object.id

    def update(self, change):
        if len(change.keys()) == 0:
            return
        # TODO add some checking of the keys etc
        for key, value in change.items():
            self.changes[key] = value
        
        self.status = SyncStatus.Modified

    def apply_changes(self):
        if len(self.changes) == 0:
            return

        for key, value in self.changes.items():
            setattr(self.object, key, value)

    def to_json(self):
        obj = {}
        for key in vars(self.object):
            obj[key] = getattr(self.object,key)
        return obj

    def is_deleted(self):
        return self.status == SyncStatus.Deleted

    def is_modified(self):
        return self.status == SyncStatus.Modified

    def is_new(self):
        return self.status == SyncStatus.New

    def is_synced(self):
        return self.status == SyncStatus.Synced

    def delete(self):
        self.status = SyncStatus.Deleted
        
class SyncedFolder(SyncedObject):
    pass

class SyncedDocument(SyncedObject):

    document_fields = [
        "abstract", "advisor", "applicationNumber", "articleColumn", "arxiv", 
        "authors", "cast", "chapter", "citation_key", "city", "code", "codeNumber", 
        "codeSection", "codeVolume", "committee", "counsel", "country", "date", 
        "dateAccessed", "day", "department", "doi", "edition", "editors", "genre", 
        "institution", "internationalAuthor", "internationalNumber", "internationalTitle", 
        "internationalUserType", "isbn", "issn", "issue", "isRead", "isStarred", "keywords", 
        "language", "lastUpdate", "legalStatus", "length", "medium", "month", "notes", 
        "original_publication", "owner", "pages", "pmid", "producers", "publicLawNumber", 
        "published_in", "publisher", "reprint_edition", "reviewedArticle", "revision", 
        "sections", "series", "seriesEditor", "seriesNumber", "session", "short_title", 
        "source_type", "tags", "time", "title", "translators", "type","userType", "volume", 
        "website", "year"
        ]

    def __str__(self):
        return self.object.id

    def to_json(self):
        obj = {}

        for key in vars(self.object):
            if key in SyncedDocument.document_fields:
                obj[key] = getattr(self.object,key)
        return obj

class ConflictResolver:

    def resolve_both_updated(self, local_document, remote_document):
        """Update local_document from remote_document as needed. 
           If the local_document status is modified after the resolution
           the changes will be applied to the remote_document in sync()

           no return value
           """
        raise Exception("Reimplement me")

    def resolve_local_delete_remote_update(self, local_document, remote_document):
        """Return a boolean to decide if the remote version should be kept"""
        raise Exception("Reimplement me")

    def resolve_local_update_remote_delete(self, local_document):
        """Return a boolean to decide if the local version should be recreated"""
        raise Exception("Reimplement me")

class SimpleConflictResolver(ConflictResolver):
    """Example implementation of ConflictResolver with conservative settings
       It keeps modified documents vs deleted ones and keeps remote data in case
       of both documents modifying the same field"""

    def resolve_local_delete_remote_update(self, local_document, remote_document):
        keep_remote_document = True
        return keep_remote_document

    def resolve_local_update_remote_delete(self, local_document):
        recreate_local_document = True
        return recreate_local_document

    def resolve_both_updated(self, local_document, remote_document):
        assert isinstance(remote_document, SyncedDocument)
        assert isinstance(local_document, SyncedDocument)

        local_changes = local_document.changes

        for key in vars(remote_document.object):
            remote_value = getattr(remote_document.object, key)
            if hasattr(local_document.object, key):
                local_value = getattr(local_document.object, key)
                if local_value == remote_value:
                    # nothing changed
                    continue

                # apply the remote change
                setattr(local_document.object, key, remote_value)

                if key not in local_changes:
                    # no conflict, no need to resolve anything
                    continue
                
                # the local and remote documents have modified the same field
                keep_remote_version = self.resolve_conflict(key, local_changes[key], remote_value)

                if keep_remote_version:
                    # get rid of the local changes
                    del local_changes[key]
                else:
                    # the document status will stay modified and will send its
                    # change to the remote in sync_documents
                    pass

        # the local_document data now is in sync with the remote_document
        assert local_document.version() == remote_document.version()

        # if no local changes are left, the document isn't modified anymore
        if len(local_changes) == 0:
            local_document.status = SyncStatus.Synced
        else:
            # local changes will be applied in sync_documents
            pass

    def resolve_conflict(self, key, local_version, remote_version):
        # dumb "resolution", 
        return False

class DummySyncedClient:

    def __init__(self, config_file="config.json", conflict_resolver=SimpleConflictResolver()):
        self.client = create_client(config_file)
        self.folders = {}
        self.documents = {}
        self.new_documents = []
        assert isinstance(conflict_resolver, ConflictResolver)
        self.conflict_resolver = conflict_resolver

    def sync(self):
        success = False
        
        while True:
            # if not self.sync_folders():
            #     continue
            if not self.sync_documents():
                continue
            break

    def fetch_document(self, remote_id):
        details = self.client.document_details(remote_id)
        assert "error" not in details
        assert details["id"] == remote_id  
        return SyncedDocument(details, SyncStatus.Synced)

    def push_new_local_document(self, local_document):
        # create the local document on the remote
        existing_id = local_document.id()

        # it's a new document, or the conflict resolver decided 
        # to keep the local version so needs to be reset
        response = self.client.create_document(document=local_document.to_json())
        assert "error" not in response

        local_document.object.version = response["version"]
        local_document.object.id = response["document_id"]
        local_document.status = SyncStatus.Synced

        if existing_id is not None:
            del self.documents[existing_id]
        self.documents[local_document.id()] = local_document
        return local_document.id()

    def add_new_local_document(self, document_details):
        document = SyncedDocument(document_details)
        self.new_documents.append(document)
        return document

    def sync_documents(self):
        # TODO fetch the whole library with paging
        # validate folders before storing, restart sync if unknown folder

        remote_documents = self.client.library()
        assert "error" not in remote_documents
        remote_ids = []

        def sync_remote_changes():

            for remote_document_dict in remote_documents["documents"]:
                remote_id = remote_document_dict["id"]
                remote_document = SyncedDocument(remote_document_dict, SyncStatus.Synced)
                remote_ids.append(remote_id)
                if remote_id not in self.documents:
                    # new document
                    self.documents[remote_id] = self.fetch_document(remote_id)
                    assert self.documents[remote_id].object.id == remote_id
                    continue

                local_document = self.documents[remote_id]

                # server can't know about new documents
                assert not local_document.is_new()

                # if remote version is more recent
                if local_document.version() != remote_document.version():
                    remote_document = self.fetch_document(remote_id)
                    if local_document.is_deleted():
                        keep_remote = self.conflict_resolver.resolve_local_delete_remote_update(local_document, remote_document)
                        if keep_remote:
                            self.documents[remote_id].reset(remote_document, SyncStatus.Synced)
                        else:
                            # will be deleted later
                            pass
                        continue

                    if local_document.is_synced():
                        # update from remote
                        local_document.reset(remote_document, SyncStatus.Synced)
                        continue

                    if local_document.is_modified():
                        # both documents are modified, resolve the conflict
                        # by handling the remote changes required and leave the local 
                        # changes to be synced later
                        self.conflict_resolver.resolve_both_updated(local_document, remote_document)
                        assert isinstance(local_document, SyncedDocument)
                        assert isinstance(remote_document, SyncedDocument)
                        assert local_document.version() == remote_document.version()
                        continue

                    # all cases should have been handled
                    assert False

                # both have the same version, so only local changes possible
                else:
                    if local_document.is_synced():
                        # nothing to do
                        # assert remote_document == local_document
                        continue

                    if local_document.is_deleted():
                        # nothing to do, will be deleted
                        continue

                    if local_document.is_modified():
                        # nothing to do, changes will be sent in the update loop
                        continue

                    # all cases should have been handled
                    assert False
    
        def sync_local_changes():
            # deal with local changes or remote deletion
            for doc_id in self.documents.keys():
                local_document = self.documents[doc_id]
                assert local_document.id() == doc_id

                # new documents are handled later
                assert not local_document.is_new()

                if doc_id not in remote_ids:
                    # was deleted on the server         
                    if local_document.is_modified():
                        recreate_local = self.conflict_resolver.resolve_local_update_remote_delete(local_document)
                        if recreate_local:
                            remote_ids.append(self.push_new_local_document(local_document))
                            continue
                    del self.documents[doc_id]
                    continue   

                if local_document.is_synced():
                    continue                 

                if local_document.is_deleted():
                    assert self.client.delete_library_document(doc_id)
                    del self.documents[doc_id]
                    continue

                if local_document.is_modified():
                    response = self.client.update_document(doc_id, document=local_document.changes)
                    assert "error" not in response
                    local_document.status = SyncStatus.Synced
                    local_document.object.version = response["version"]
                    local_document.apply_changes()
                    continue

                assert False

        def send_new_documents():
            # create new local documents on the server
            for new_document in self.new_documents:
                assert new_document.is_new()
                doc_id = self.push_new_local_document(new_document)
                assert doc_id > 0
            self.new_documents = []

            
        sync_remote_changes()
        sync_local_changes()
        send_new_documents()

        return True

    def reset(self):
        self.documents = {}
        self.folders = {}

    def dump_status(self,outf):
        outf.write( "\n")
        outf.write( "#Documents (%d)\n"%len(self.documents))
        outf.write( "@sort 0,-2\n")
        outf.write( "@group 0\n")
        outf.write( "--\n")
        outf.write( "status, id, version, title\n")
        if len(self.documents)+len(self.new_documents):

            for doc_id, document in self.documents.items():
                if document.is_modified():
                    outf.write("# changes: %s\n"%document.changes)
                outf.write( "%s,  %s ,  %s , %s\n"%(SyncStatus.to_str(document.status), document.id(), document.version(), document.object.title))
            for document in self.new_documents:
                outf.write( "%s,  %s ,  %s , %s\n"%(SyncStatus.to_str(document.status), document.id(), document.version(), document.object.title))
