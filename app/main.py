# Source:
# main.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from docIngester.src import fileuploader as fu
from reportGenerator import generator as gen
from docSearch import search as search
from werkzeug.utils import secure_filename
import os
import pathlib
import json

UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure a file is an allowed file type (for now, just PDF)
# Source: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    docs = []
    elements, code = fu.read_many(current_user.email)
    for element in elements:
        docs.append(element.get("Name"))
    return render_template('profile.html', name=current_user.name, data=docs)


@main.route('/search', methods=['POST'])
@login_required
def keySearch():
    keywords = request.form.get('keywords')  # Get keywords from form
    if keywords is None or keywords == '':
        flash('Please enter search terms as a list of comma separated keywords')
        return redirect(url_for('main.profile'))
    keywords = keywords.split(',')  # Split keywords by comma separator
    # Retrieve results from entity analysis
    results = search.runSearch(current_user.email, keywords)
    if results is None or results == []:
        results = [{"Title": "No Results Found", "Paragraphs": []}]
    # Generate keyword string for display
    keystring = ', '.join([str(kword) for kword in keywords])
    return render_template('searchResults.html', keywords=keystring, results=results)


@main.route('/upload')
@login_required
def upload():
    return render_template('upload.html')


@main.route('/upload', methods=['POST'])
@login_required
def login_post():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('Choose a file')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Please select a file to upload!')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pathlib.Path(UPLOAD_FOLDER, current_user.email).mkdir(
            parents=True, exist_ok=True)
        path = os.path.join(UPLOAD_FOLDER, current_user.email, filename)
        file.save(path)
        ret, msg = fu.create(current_user.email, path)
        path = pathlib.Path(path)
        path.unlink()  # Delete file from local file store to save memory
        if ret == {}:
            flash(msg)
            return redirect(request.url)
        flash('Upload Successful!')
        return redirect(request.url)


@main.route('/report/<string:document>')
@login_required
def generate_report(document):
    doc_info = gen.generateReport(current_user.email, document)

    # If nothing in the DB, return to profiule
    if doc_info is None or doc_info == {}:
        flash('An Error Occurred')
        return redirect(url_for('main.profile'))

    score = doc_info["OVERALL_SENTIMENT"]  # A Float
    mpScore = doc_info["MOST_POSITIVE_PAR"][0]  # A Float
    mpText = doc_info["MOST_POSITIVE_PAR"][1]  # A Paragraph of text
    mnScore = doc_info["LEAST_POSITIVE_PAR"][0]  # A float
    mnText = doc_info["LEAST_POSITIVE_PAR"][1]  # A paragraph of text
    entities = doc_info["ENT_LIST"]  # A List of pairs
    links = doc_info["NEWS_LINKS"]  # A List of pairs
    # A List of dictionaries
    paragraphBreakdown = doc_info["PARAGRAPH_BREAKDOWN"]

    contentClass = [x.get("Category").strip(
        '/') for x in doc_info["CONTENT_CLASS"] if x.get("Category") is not None]

    if not contentClass:
        contentClass = ["No Categories Identified"]

    return render_template('report.html', docname=document, content=contentClass, nlpScore=score, mpScore=mpScore,
                           mpText=mpText, mnScore=mnScore, mnText=mnText, entities=entities, links=links,
                           pars=paragraphBreakdown)


@main.route('/view/<string:document>')
@login_required
def view_document(document):
    document_json = json.dumps({"Name": document})
    # Retrieves document from the DB
    doc, code = fu.read_one(current_user.email, document_json)
    if doc is None or doc == {}:
        flash('An Error Occurred in retrieving this document')
        return redirect(url_for('main.profile'))

    text = doc.get('Text').get('Text')  # Extract All paragraphs from text
    metadata = doc.get("File_Metadata").items()

    return render_template('docView.html', docName=document, text=text, metadata=metadata)

@main.route('/delete/<string:document>')
@login_required
def delete(document):
    document_json = json.dumps({"Name": document})
    # Retrieves document from the DB
    msg, code = fu.delete(current_user.email, document_json)
    if code == 404:
        flash(f'Unable to Delete {document}')
    else:
        flash(f'The document {document} has been successfully deleted')

    return redirect(url_for('main.profile'))
