# Source:
# main.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from docIngester.src import fileuploader as fu
from werkzeug.utils import secure_filename
import os
import pathlib

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
