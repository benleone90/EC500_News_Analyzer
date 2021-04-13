# ======================================================
# Private Helper Functions for File Uploader API
# ======================================================

# from PyPDF2 import PdfFileReader
import fitz
from datetime import datetime
import os


# Generate a default file object with empty fields
def _getDefaultFileObj():
    fileobj = {
        "Name": "",
        "path": "",
        "UID": "",
        "Upload_Date": "",
        "File_Metadata": {},
        "Text": {
            "Text": [],
            "Sentiment": [],
            "Entity": [],
            "Entity_Sentiment": [],
            "Content_Classification": [],
        },
    }
    return fileobj


# Method to generate our file object
def generateObject(path, userId):

    if not os.access(path, os.R_OK) and not os.path.exists(path):  # Check if file exists before processing
        return None, None

    myobj = _getDefaultFileObj()
    myobj["Name"] = _getDocName(path)  # Extract name from path
    myobj["path"] = path  # Add path
    myobj["UID"] = userId  # update later when we add user login support
    myobj["Upload_Date"] = str(datetime.now())  # Add upload date
    myobj["File_Metadata"] = _getMetadata(path)  # Extract and add metadata
    myobj["Text"]["Text"] = _generateText(path)  # Extract and add Text
    return myobj, myobj["Name"]


def _getDocName(path):
    path = path.strip().split('/')  # Strip off whitespace and break into components by '/' delimiter
    return path[len(path)-1]  # Return last element(the name of the document)

# Method to extract file metadata
def _getMetadata(path):
    metadata = {
        "Title": "",
        "Author": "",
        "Creator": ""
    }
    doc = fitz.open(path)
    doc_info = doc.metadata
    metadata["Title"] = doc_info.get('title')
    metadata["Author"] = doc_info.get('author')
    metadata["Creator"] = doc_info.get('creator')
    return metadata


# Extracts text from a PDF file into paragraphs
def _generateText(path):
    textArray = []
    doc = fitz.open(path)
    for page in doc:
        pagetext = page.get_text("blocks")
        for texts in pagetext:
            if len(texts) >= 4:
                text = texts[4]
                text = text.strip('\n')
                text = text.strip()
                text = text.replace('\n', '')
                if text and "<image:" not in text:
                    textArray.append(text)

    return textArray


if __name__ == '__main__':
    data = generateObject("./test/test.pdf", "journalist")
