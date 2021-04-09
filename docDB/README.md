# Database
This Folder contains the functions used to manage interactions between the API's and the application's MongoDB database.

## Database Overview
For the database, I chose to use MongoDB due to the unstructured nature of the documents we will be processing. This database contains 1 collection: *Documents* 

### Documents
Our documents collection is used to store documents uploaded by users through the document ingester. Each document is stored as a JSON in the following format: 
<pre>
   {
       "_id": < id assigned by MongoDB >,
       "Name": < the file name extracted from the path >,
       "path": < The file path as uploaded in the database >,
       "UID":< User ID associated with file > 
       "Upload_Date":< YYYY-MM-DD >, 
       "File_Metadata":{
           "Title":< Title extracted from PDF file >, 
           "Author":< Author extracted from PDF file >, 
           "Creator":< Creator extracted from PDF file >
        }, 
       "Text":{
           "Text":[< Paragraph1 >, ...],
           "Sentiment":[< Paragraph1_Sentiment >, ...],
           "Entity":[< Paragraph1_Entity >, ...],
           "Entity_Sentiment":[< Paragraph1_Entity_Sentiment >, ...],
           "Content_Classification":[< Paragraph1_Content_Class >, ...],
        },
        "Deleted" : < "True" or "False" indicating whether the document has been marked as deleted > 
   }
</pre>

#### Document Accessor Public Methods
- **addDocument(document_input)**: ***Add a document to the DB***
   - @param< document > A JSON document object to store in the database. Note: To prevent duplicates, the document's "Name" and "UID" fields must not match an existing (non-deleted) document in the database (ie, it must not have both the same UID and Name as another document already stored and not marked as deleted)
   - @return 1 if the document is successfully added and None otherwise

- **getDocument(username, docobj)**: ***Retrieve a single document from the DB***
   - @param< username >   A string containing the username of a user whose documents we wish to access
   - @param< docobj > A JSON object containing the UID and another valid identifier (id or Name) associated with the document
   - @return The document (as a JSON) if one is found and None otherwise

- **getDocuments(uid)**: ***Retrieve multiple documents belonging to a single user from the DB***
   - @param< uid > A string containing the username of a user whose documents we wish to access
   - @return The documents (as a JSON) if atleast one is found and None otherwise

- **updateDocument(username, idObj, update)**: ***Update a document in DB***
   - @param< username >   A string containing the username of a user whose documents we wish to access
   - param< idObj > A JSON object containing a valid identifier (id or Name) associated with the document
   - @param< update > A JSON object containing the update to apply to the document
   - @return The updated document (as a JSON) if one is updates and none otherwise

- **deleteDocument(username, idObj)**: ***Mark a document in the DB as deleted***
   - @param< username >   A string containing the username of a user whose documents we wish to mark as deleted
   - @param< idObj >  A JSON object containing the UID and another valid identifier (id or Name) associated with the document
   - @return The number of documents marked as deleted 

- **deleteAllUserDocs(username)**: ***Mark all documents associated with a username as deleted***
   - @param< username > A string containing the username of a user who's documents we wish to mark as deleted
   - @return  The number of documents marked with a deleted flag or None if no m matching users are found


#### Documents Collection Snaphot
A snapshot of the current Documents collection is included here (containing a few sample documents uploaded during testing):

![snapshot](https://github.com/BUEC500C1/news-analyzer-whunt1965/blob/main/photos/docs.png)


