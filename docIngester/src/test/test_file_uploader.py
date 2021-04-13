# Tests for file uploader module
from memory_profiler import profile

from docIngester.src import fileuploader as fup
import tracemalloc

import os

# ==================
# Start Tests
# ==================

file = "fakedb.txt"

rootdir = os.path.dirname(os.path.abspath(__file__))
pdf1 = os.path.join(rootdir, 'test.pdf')
pdf2 = os.path.join(rootdir, 'test2.pdf')

#Init tracemalloc
def test_init():
    printTitle()
    f = open(file, "w")
    f.write('\n')
    f.seek(0)
    f.truncate()
    f.close()
    f.close()
    assert 1 == 1

# Create Tests
def test_create():

    tracemalloc.start()  # Start trace malloc

    # Create a test user to associate with files
    user = {
        "username": "test_fileuploader",
        "email": "test_fileuploader@EC500.edu",
        "password": 123
    }

    # Correct Creates
    fileObj, msg = fup.create(user["username"], pdf1, test=True, fn=file)
    assert fileObj["path"] == pdf1
    assert fileObj["Name"] == "test.pdf"
    assert msg == "Document Successfully Uploaded"

    fileObj, code = fup.create(user["username"], pdf2, test=True, fn=file)
    assert fileObj["path"] == pdf2
    assert fileObj["Name"] == "test2.pdf"
    assert code == "Document Successfully Uploaded"


    # Invalid Create (bad file path)
    ret, msg = fup.create(user["username"], "./notafile.pdf", test=True, fn=file)
    assert ret == {}
    assert msg == "File could not be converted"

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 5 ]")
    for stat in top_stats[:5]:
        print(stat)


# Read Tests
def test_read():

    tracemalloc.start()  # Start trace malloc

    # Ref to test user to associate with files
    user = {
        "username": "test_fileuploader",
        "email": "test_fileuploader@EC500.edu",
        "password": 123
    }

    query1 = '{"Name": "test.pdf"}'
    query2 = '{"Name": "test2.pdf"}'

    # Valid read one op
    obj, code = fup.read_one(user["username"], query1, test=True, fn=file)
    assert obj["path"] == pdf1
    assert code == "Success"

    # Valid read one op
    obj, code = fup.read_one(user["username"], query2, test=True, fn=file)
    assert obj["path"] == pdf2
    assert code == "Success"

    # Invalid read one op (bad params)
    obj, code = fup.read_one(user["username"], 7, test=True, fn=file)
    assert obj == {}
    assert code == "Invalid object (Non-JSON) for File Read Request"

    # Invalid read one op (bad query)
    obj, msg  = fup.read_one(user["username"], '{"Name": "notafile.pdf"}', test=True, fn=file)
    assert obj == {}
    assert msg == "File Not Found"

    # valid read many - will not work without DB connection
    # w = json.loads(db.getUser(user["username"]))
    # result, code = fup.read_many(user["username"])
    # for item in result:
    #     assert item["UID"] == w["_id"]
    # assert code == 200

    # Valid read many for no DB connection
    w = user
    result, code = fup.read_many(user["username"], test=True, fn=file)
    for item in result:
        assert item["UID"] == w["username"]
    assert code == "Success"

    # invalid read many
    result, code = fup.read_many("notauser", test=True, fn=file)
    assert result == []
    assert code == "Files Not Found"

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 5 ]")
    for stat in top_stats[:5]:
        print(stat)


# Update tests
def test_update():

    tracemalloc.start()  # Start trace malloc

    # Ref to test user to associate with files
    user = {
        "username": "test_fileuploader",
        "email": "test_fileuploader@EC500.edu",
        "password": 123
    }

    # Valid Update Test 1
    identifier = '{"Name":"test.pdf"}'
    validupdate = '{"Upload_Date":"2020-12-17"}'
    obj, code = fup.update(user["username"], identifier, validupdate, test=True, fn=file)
    assert obj["Upload_Date"] == "2020-12-17"
    assert code == "Update Successful"

    # Valid Update Test 2
    identifier = '{"Name":"test2.pdf"}'
    validupdate = '{"File_Metadata": {"Authors": ["Jose"]}}'
    obj, code = fup.update(user["username"], identifier, validupdate, test=True, fn=file)
    assert obj["File_Metadata"]["Authors"][0] == "Jose"
    assert code == "Update Successful"

    # Invalid Update - bad params
    identifier = 7
    validupdate = '{"File_Metadata": {"Authors": ["Jose"]}]'
    obj, code = fup.update(user["username"], identifier, validupdate, test=True, fn=file)
    assert obj == {}
    assert code == "Invalid Request parameters"

    #Invlalid Update - bad user
    identifier = '{"Name":"test2.pdf"}'
    validupdate = '{"File_Metadata": {"Authors": ["Jose"]}}'
    obj, code = fup.update("badusername", identifier, validupdate, test=True, fn=file)
    assert obj == {}
    assert code == "Could not complete your update"

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 5 ]")
    for stat in top_stats[:5]:
        print(stat)


# Delete Tests
def test_delete():

    tracemalloc.start()  # Start trace malloc

    # Ref to test user to associate with files
    user = {
        "username": "test_fileuploader",
        "email": "test_fileuploader@EC500.edu",
        "password": 123
    }

    # Invalid Delete - bad file name
    invalid_id = '{"Name":"nonexistentfile.pdf"}'
    msg, code = fup.delete(user["username"], invalid_id, test=True, fn=file)
    assert msg == "Unable to delete file"
    assert code == 404

    # Invalid Delete - bad request params
    invalid_id = 7
    msg, code = fup.delete(user["username"], invalid_id, test=True, fn=file)
    assert msg == "Invalid request Parameters"
    assert code == 400

    # Valid Delete 1
    idobj = '{"Name":"test.pdf"}'
    msg, code = fup.delete(user["username"], idobj, test=True, fn=file)
    assert msg == "Deleted 1 documents"
    assert code == 200

    idobj2 = '{"Name":"test2.pdf"}'
    msg, code = fup.delete(user["username"], idobj2, test=True, fn=file)
    assert msg == "Deleted 1 documents"
    assert code == 200

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 5 ]")
    for stat in top_stats[:5]:
        print(stat)




# ==================
# Ends Tests
# ==================

#Print header for report
def printTitle():
    print()
    print("===FILE UPLOAD TESTS===")
    print()


