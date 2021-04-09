# Source:
# main.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from docIngester.src import fileuploader as fu
from werkzeug.utils import secure_filename
import os
import pathlib
from .models import Document
from . import db

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
    rows = Document.query.filter_by(email=current_user.email)
    for row in rows:
        docs.append(row.name)
    print(docs)
    return render_template('profile.html', name=current_user.name, data=docs)

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
        pathlib.Path(UPLOAD_FOLDER, current_user.email).mkdir(parents=True, exist_ok=True)
        path = os.path.join(UPLOAD_FOLDER, current_user.email, filename)
        file.save(path)
        ret, msg, docName = fu.create(current_user.email, path)
        path = pathlib.Path(path)
        path.unlink()  # Delete file from local file store to save memory
        if ret is None:
            flash(msg)
            return redirect(request.url)

        # add the new doc to the database
        new_doc = Document(email=current_user.email, name=docName)
        db.session.add(new_doc)
        db.session.commit()

        flash('Upload Successful!')
        return redirect(request.url)
