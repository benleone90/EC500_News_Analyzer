# ======================================================
# File Uploader API - Public API Functions
# See documentation for required input format
# ======================================================
import logging
import json

if __name__ == '__main__':
    import sys
    import os

    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
    import _fileuploader_events as ev
    import _fileuploader_helpers as funcs
    from docDB import db

else:
    from . import _fileuploader_events as ev
    from . import _fileuploader_helpers as funcs
    from docDB import db

# Init logger
logger = logging.getLogger(__name__)  # set module level logger
# configure logging -- note: set to std:out for debug
logging.basicConfig(filename='fileuploader.log', format='%(asctime)s %(levelname)s %(message)s')


# Uploads a file, parses it into JSON, and creates an entry in the Database
# @param<username> The username of the user creating an entry
# @param<path> A path to a file to insert into the DB
# Remove Test and fn params before production -- for unit tests only
# @return If successful, returns the JSON version of the file and a success response code. Otherwise, returns an empty
#         JSON and an error message
def create(username, path, test=False, fn=None):

    logging.info(f"{{Event: {ev.Event.CREATE_Initiated}, Target: {path, username}}}")

    fileObj, name = funcs.generateObject(path, username)

    if fileObj is None:
        logging.error(f"{{Event: {ev.Event.CREATE_Error}, Target: {path, username}}}")
        return {}, "File could not be converted"

    # Calls non-DB test function for tests. Remove this block and test params (test=False, fn=None) before deployment
    # Test block begin
    if test:
        result = _mockDBCreate(fn, fileObj)
    else:
        result = db.addDocument(fileObj)
    # End test block

    # Un-comment out below line for production
    # result = db.addDocument(fileObj)

    if result:
        logging.info(f"{{Event: {ev.Event.CREATE_Success}, Target: {path, username}}}")
        return fileObj, "Document Successfully Uploaded"
    else:
        logging.error(f"{{Event: {ev.Event.CREATE_Error}, Target: {path, username}}}")
        return {}, "This Document could not be added to the database. Please make sure that you have not already " \
                     "added this document "


# Accessor for a single file in the DB
# @param<username> A string containing the username of the user associated with the files
# @param<fileobj> A (stringified) JSON object containing fields from which the file can be referenced (eg, Title or _id)
# @return If the read is successful returns the file as a JSON object and a success message. Otherwise, returns an empty
#        JSON, and an error code
def read_one(username, fileobj, test=False, fn=None):

    logging.info(f"{{Event: {ev.Event.READ_Initiated}, Target: {fileobj, username}}}")

    # Ensure JSON compatible input
    try:
        db_fileobj = json.loads(fileobj)
    except ValueError as E:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {fileobj, username}}}")
        return {}, "Invalid object (Non-JSON) for File Read Request"
    except TypeError as E:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {fileobj, username}}}")
        return {}, "Invalid object (Non-JSON) for File Read Request"

    # Calls non-DB test function for tests. Remove this block and test params (test=False, fn=None) before deployment
    # Test block begin
    if test:
        result = _mockDBReadOne(fn, username, db_fileobj)
    else:
        result = db.getDocument(username, db_fileobj)  # Extract requested document from database
    # End test block

    # Un-comment out below line for production
    # result = db.getDocument(username, db_fileobj)  # Extract requested document from database
    # If database returns none, file is not in database
    if result is None or result == []:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {fileobj, username}}}")
        return {}, "File Not Found"
    # Otherwise return result
    else:
        result = json.loads(result)
        logging.info(f"{{Event: {ev.Event.READ_Success}, Target: {fileobj, username}}}")
        return result, "Success"


# Accessor for all files in the DB belonging to a single user
# @param<username> A string containing the username of the user associated with the files
# @return If the read is successful returns the file as a JSON object containing the files found along with a Success
#         code. Otherwise, returns an empty list and an error code
def read_many(username, test=False, fn=None):
    logging.info(f"{{Event: {ev.Event.READ_Initiated}, Target: {username}}}")

    # Calls non-DB test function for tests. Remove this block and test params (test=False, fn=None) before deployment
    # Test block begin
    if test:
        result = _mockDBReadMany(fn, username)
    else:
        # Extract requested document from database
        result = db.getDocuments(username)  # Extract requested documents from database
    # End test block

    # Un-comment out below line for production
    # result = db.getDocuments(username)  # Extract requested documents from database

    # If database returns none, there are no files in the database belonging to this user
    if result is None or result == []:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {username}}}")
        return [], "Files Not Found"
    # Otherwise return result
    else:
        result = json.loads(result)
        logging.info(f"{{Event: {ev.Event.READ_Success}, Target: {username}}}")
        return result, "Success"


# Modifies a file in the DB
# @param<username> A string containing the username of the user associated with the files
# @param<identifier> A JSON object containing fields from which the file can be referenced (eg, Title or _id)
# @param<update> A JSON string object containing the specific parameters to update
# @return If the update is successful returns updated file as a JSON object along with a Success code
#         Otherwise, otherwise returns an empty JSON and an error code
def update(username, identifier, updateObj, test=False, fn=None):
    logging.info(f"{{Event: {ev.Event.UPDATE_Initiated}, Target: {username, identifier, updateObj}}}")

    # Ensure JSON compatible inputs
    try:
        db_identifier = json.loads(identifier)
        db_update = json.loads(updateObj)
    except ValueError as E:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {username, identifier, updateObj}}}")
        return {}, "Invalid Request parameters"
    except TypeError as E:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {username, identifier, updateObj}}}")
        return {}, "Invalid Request parameters"

    # Calls non-DB test function for tests. Remove this block and test params (test=False, fn=None) before deployment
    # Test block begin
    if test:
        result = _mockDBUpdate(fn, username, db_identifier, db_update)
    else:
        # Extract requested document from database
        result = db.updateDocument(username, db_identifier, db_update)
    # End test block

    # Un-comment out below line for production
    # result = db.updateDocument(username, db_identifier, db_update)    # Request to update file in database

    # A none result means that the file could not be updated, return an error
    if result is None or result == []:
        logging.error(f"{{Event: {ev.Event.READ_Error}, Target: {identifier, updateObj}}}")
        return {}, "Could not complete your update"
    # Otherwise, return the updated files
    else:
        result = json.loads(result)
        logging.info(f"{{Event: {ev.Event.UPDATE_Success}, Target: {identifier, updateObj}}}")
        return result, "Update Successful"


# Delete a file in the DB
# @param<username> A string containing the username of the user associated with the files
# @param<fileObj> A JSON object containing a unique identifier (eg file name or _id) associated with the file to delete.
# @return If the delete is successful, returns a success message and the number of files deleted.
#         Otherwise, an error message and an error code
def delete(username, fileObj, test=False, fn=None):
    logging.info(f"{{Event: {ev.Event.DELETE_Initiated}, Target: {username, fileObj}}}")

    # Ensure JSON compatible inputs
    try:
        db_fileObj = json.loads(fileObj)
    except ValueError as E:
        logging.error(f"{{Event: {ev.Event.DELETE_Error}, Target: {username, fileObj}}}")
        return "Invalid request Parameters", 400
    except TypeError as E:
        logging.error(f"{{Event: {ev.Event.DELETE_Error}, Target: {username, fileObj}}}")
        return "Invalid request Parameters", 400

    # Calls non-DB test function for tests. Remove this block and test params (test=False, fn=None) before deployment
    # Test block begin
    if test:
        result = _mockDBDelete(fn, username, db_fileObj)
    else:
        # Extract requested document from database
        result = db.deleteDocument(username, db_fileObj)
    # End test block

    # # Un-comment out below line for production
    # result = db.deleteDocument(username, db_fileObj)     # Attempt to delete from DB
    if result is None or result <= 0:
        logging.error(f"{{Event: {ev.Event.DELETE_Error}, Target: {username, fileObj}}}")
        return "Unable to delete file", 404

    # Log success and return number of documents deleted
    logging.info(f"{{Event: {ev.Event.DELETE_Success}, Target: {username, fileObj}}}")
    return f"Deleted {result} documents", 200


# ******************************************************************************************************
# Functions for Github Action Tests
#
# Mimic the real functions but use a local file store instead of DB which cannot be accesses from GitHub actions since
# IP of actions machine is indeterminate (and must be whitelisted to access DB)
# ******************************************************************************************************

# Mock DB function for document create
def _mockDBCreate(fn, fileObj):
    with open(fn, 'a+') as infile:
        try:
            data = json.load(infile)
        except:
            data = None
        result = True
        if data:
            for item in data:
                item = json.loads(item)
                if item["UID"] == fileObj["UID"] and item["Name"] == fileObj["Name"]:
                    result = False
                    break
        if result:
            json.dump(fileObj, infile)
            infile.write('\n')

        return result


# Mock DB function for read one
def _mockDBReadOne(fn, username, db_fileobj):
    with open(fn, 'r+') as infile:
        data = []
        result = None
        try:
            for jsonObj in infile:
                obj = json.loads(jsonObj)
                data.append(obj)
        except:
            data = []
        if data:
            for item in data:
                # item = json.loads(item)
                if item["UID"] == username and item["Name"] == db_fileobj["Name"]:
                    result = json.dumps(item)
                    break
    return result


# Mock DB function for read many
def _mockDBReadMany(fn, username):
    with open(fn, 'r+') as infile:
        data = []
        result = []
        try:
            for jsonObj in infile:
                obj = json.loads(jsonObj)
                data.append(obj)
        except:
            data = []
        if data:
            for item in data:
                # item = json.loads(item)
                if item["UID"] == username:
                    result.append(item)
        if result:
            result = json.dumps(result)

    return result

def _mockDBUpdate(fn, username, db_identifier, db_update):
    data = []
    result = None
    with open(fn, 'r+') as infile:
    # with open("./test/fakedb.txt", 'r+') as infile:
        try:
            for jsonObj in infile:
                obj = json.loads(jsonObj)
                data.append(obj)
        except:
            data = []
        if data:
            for item in data:
                if item["UID"] == username and item["Name"] == db_identifier["Name"]:
                    # db_update = dict(db_update)
                    for key in db_update.keys():
                        item[key] = db_update[key]
                    result = json.dumps(item)
        if result:
            infile.seek(0)
            infile.truncate()
            for item in data:
                json.dump(item, infile)
                infile.write('\n')

    return result

def _mockDBDelete(fn, username, db_fileObj):
    data = []
    result = None
    with open(fn, 'r+') as infile:
    # with open("./test/fakedb.txt", 'r+') as infile:
        try:
            for jsonObj in infile:
                obj = json.loads(jsonObj)
                data.append(obj)
        except:
            data = []
        if data:
            for item in data:
                if item["UID"] == username and item["Name"] == db_fileObj["Name"]:
                    data.remove(item)
                    result = 1
                    break
        if result:
            infile.seek(0)
            infile.truncate()
            for item in data:
                json.dump(item, infile)
                infile.write('\n')

    return result






