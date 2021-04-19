from pymongo import MongoClient
from bson.json_util import dumps, loads
import os
import copy

# Valid identifiers for a document (in combination with UID)
docIds = ["_id", "Name"]


# Initialize DB connection
def _connect():
    key = os.getenv('MONGOKEY')
    client = MongoClient(key, connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True, connect=False,
                         maxPoolsize=1)
    return client


# ==========================================
# Methods for accessing Documents Collection
# ==========================================

# Get reference to Documents Collection
def _getDocCollection():
    client = _connect()
    db = client["NEWS_ANALYZER"]  # Name of Database
    documents = db["Documents"]  # Name of Collection
    return documents


# Add a document to the DB
# @param<document> A JSON document object to store in the database. Note: To prevent duplicates, the document's "Name"
#                  and "UID" fields must not match an existing (non-deleted) document in the database (ie, it must not
#                  have both the same UID and Name as another document already stored and not marked as deleted)
# @return          1 if the document is successfully added and None otherwise
def addDocument(document_input):
    documents = _getDocCollection()

    # Ensure we have a valid user in the DB to associate with this document
    UID = document_input["UID"]
    if UID is None:
        return None

    # Create a copy so don't update fields of original document
    document = copy.copy(document_input)

    # Query to determine if this document already exists in the DB
    query = {"Name": document["Name"], "UID": UID, "Deleted": "False"}

    # Check if this document exists in the DB and if not, insert it
    if documents.count_documents(query) == 0:
        document["Deleted"] = "False"
        documents.insert_one(document)  # Insert document
        return 1
    else:
        return None  # Otherwise, don't insert


# Retrieve a single document from the DB
# @param<username>   A string containing the username of a user whose documents we wish to access
# @param<docobj>   A JSON object containing a valid identifier (id or Name) associated with the document
# @return          The document (as a JSON) if one is found and None otherwise
def getDocument(username, docobj):
    # Validate that this json object has the correct identifiers for a query
    ids = _validateDocObj(docobj)

    # If no valid identifiers or username is passed, return None
    if not ids:
        return None

    # Add valid identifiers to query
    query = dict()
    query["UID"] = username  # Add internal UID to doc
    query["Deleted"] = "False"  # Ensure we do not fetch deleted documents
    for identifier in ids:
        query[identifier] = docobj[identifier]

    query["Deleted"] = "False"  # Ensure we do not fetch deleted documents

    documents = _getDocCollection()

    if documents.count_documents(query) == 0:  # Check if this document exists
        return None

    doc = documents.find_one(query)  # find document(s)
    ret = dumps(doc, indent=2)  # convert to JSON
    return ret


# Retrieve multiple documents belonging to a single user from the DB
# @param<UID>   A string containing the username of a user whose documents we wish to access
# @return       The documents (as a JSON) if atleast one is found and None otherwise
def getDocuments(uid):
    documents = _getDocCollection()  # Get collection

    query = {"UID": uid, "Deleted": "False"}  # Set query parameters

    # Ensure there are documents in the DB
    if documents.count_documents(query) == 0:
        return None

    doc = documents.find(query)  # find document(s)
    ret = dumps(doc, indent=2)  # convert to JSON
    return ret


# Update a document in DB
# @param<username>   A string containing the username of a user whose documents we wish to update
# @param<idObj>  A JSON object containing a valid identifier (id or Name) associated with the document
# @param<update> A JSON object containing the update to apply to the document
# @return        The updated document (as a JSON) or None if the query is invalid
def updateDocument(username, idObj, update):
    # Validate that this json object has the correct identifiers for a query
    ids = _validateDocObj(idObj)

    # If no valid identifiers are passed, return None
    if not ids:
        return None

    # Add valid identifiers to query
    query = dict()
    query["Deleted"] = "False"  # Ensure we do not fetch deleted documents
    query["UID"] = username  # Add UID for user
    for identifier in ids:
        query[identifier] = idObj[identifier]

    documents = _getDocCollection()  # Fetch collection
    newvalues = {"$set": update}  # Set update params
    result = documents.update_one(query, newvalues)  # Update document

    if result.modified_count > 0:  # If we have successfully updated the document, return the document by calling get
        # Create a shallow copy to avoid mutating original object
        objcopy = copy.copy(idObj)
        if "Name" in update:
            objcopy["Name"] = update["Name"]
        obj = getDocument(username, objcopy)
        return obj


# Mark a document in the DB as deleted
# @param<username>  A string containing the username of a user whose documents we wish to delete
# @param<idObj>  A JSON object containing a valid identifier (id or Name) associated with the document
# @return        The number of documents marked as deleted
def deleteDocument(username, idObj):
    # Validate that this json object has the correct identifiers for a query
    ids = _validateDocObj(idObj)

    # If no valid identifiers are passed, return None
    if not ids:
        return None

    # Add valid identifiers to query
    query = dict()
    query["UID"] = username
    query["Deleted"] = "False"  # Ensure we do not fetch deleted documents
    for identifier in ids:
        query[identifier] = idObj[identifier]

    # Set deleted flag on "deleted" document
    newvalues = {"$set": {"Deleted": "True"}}

    documents = _getDocCollection()
    # Update document with deleted flag
    result = documents.update_one(query, newvalues)
    return result.modified_count  # Return # docs updated with deleted flag


# Mark all documents associated with a username as deleted
# @param<UID>   A string containing the username of a user who's documents we wish to mark as deleted
# @return       The number of documents marked with a deleted flag or None if no m matching users are found
def deleteAllUserDocs(username):
    documents = _getDocCollection()

    query = {"UID": username, "Deleted": "False"}
    # Set deleted flag on "deleted" document
    deletedflag = {"$set": {"Deleted": "True"}}
    result = documents.update_many(query, deletedflag)
    return result.modified_count


# Private helper method to ensure that a JSON has the correct fields to validate a document object
def _validateDocObj(docobj):
    ret = []
    for identifier in docIds:
        if identifier in docobj:
            ret.append(identifier)
    return ret
