# EC500 News Analyzer

## Introduction/Purpose

Our EC500 News Analyzer provides a full web application for journalists to upload, view, and analyze PDFs for research purposes.
The goal of this project is to provide a one-stop solution to many of the disparate resources that a journalist or researcher may need.

## Setup

Before setup, ensure that you have API keys for Google's NLP, the New York Times API, and set up your own MongoDB Atlas database. Please look closely at the key names implemented in our code to corretly export them to your local environment.

- Clone and `cd` into repository
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip3 install -r requirements.txt`
- `python3`
- `>>> from app import db, create_app`
- `>>> db.create_all(app=create_app())`
- exit python3 termial (ctrl-d)
- `python3 run.py`
- Visit localhost:8080

## Demo Video

[Video Link](https://github.com/benleone90/EC500_News_Analyzer/blob/main/video/demo.mp4)

## Enhancements/New Features Implemented

- Integration of API's into a single web application.
- Login mechanism using a SQL database to securely store user credentials.
- Report Generator - runs NLP analysis (sentiment, entity, and content classification) on a designated document stored in the database and generates a comprehensive report.
- Document Viewer - Displays document metadata and text for a document stored in the database.
- Document Search - Users can search all document for comma-separated key words and see results.
- Document Deletion - After viewing the document, the user can delete the document from their lists.

## Future Work

- Search functionality could take in a CSV file with search terms already filled in to quicken the search.
- Mulitple language support - currenlty only English is supported in our NLP implementation. Will throw error if it recognizes another language.
- Accessability features - alternate text for images, document reader for visually impared users, etc.

## Notes

Website is currently deployed on AWS EC2 instance. To view the page in its current state, please contact the developers directly.
