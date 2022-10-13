from operator import and_
from time import sleep
from unicodedata import name
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, abort, jsonify, current_app
)
from flask import session as fsession
from ..database.init_db import Session
from ..database.table_declarations import *
from ..database.security import clean_html

from sqlalchemy import select, and_
from sqlalchemy.orm import Session as Ses

from .auth import login_required

from werkzeug.utils import secure_filename

import os

import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('api', __name__)

@bp.route('/api/image/<int:image_id>', methods=['GET'])
def image_retrieve(image_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        image:Image = sqlsession.execute(select(Image).where(Image.editable_id == image_id)).scalar()

        if image:
            if os.path.exists(image.image_path):
                return send_file(image.image_path, mimetype='image')
    return str(image_id)

# Taken from https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Taken from https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
@bp.route('/api/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    with Session.begin() as sqlsession:
        sqlsession:Ses

        user = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if request.method == 'POST' and user:
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                original_filename = file.filename
                filename = secure_filename(file.filename)


                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
                    file_type = filename.rsplit('.', 1)[1].lower()

                    filename = str(uuid.uuid4()) + f".{file_type}"
                
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                image = Image(owner = user, name = original_filename, \
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                sqlsession.add(image)
                return ':)'
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

@bp.route('/api/image_grid', methods=['GET'])
@login_required
def image_grid():
    with Session.begin() as sqlsession:
        sqlsession:Ses

        images = sqlsession.execute(select(Image).where(Image.owner_id == g.user.id)).scalars().all()

        return render_template('snippets/image_grid.html', images=images)

@bp.route('/api/character_edit', methods=['POST'])
@login_required
def character_edit():
    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            character_info:dict = request.json

            if character_info:
                character_id = character_info.get('character_id')

                character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user and character: 
                    if character in user.editor_perms:
                        character.name = character_info.get('character_name')
                        character.description = character_info.get('character_description')

            return('probably good')
            
    return('probably bad')

@bp.route('/api/location_search', methods=['POST'])
@login_required
def location_search():

    print(request.data)

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            search_info:dict = request.json
            search_type = search_info.get('search_type')

            if search_type:
                if search_type == 'location':
                    query = search_info.get('query')
                    if not query:
                        query = ''

                    user = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
                    locations = sqlsession.execute(select(Location).where(and_(Location.name.ilike('%'+query+'%') , Location.editors.contains(user)))).scalars().all()
                    print(locations)

                    location_list = [{'label':element.name, 'value':element.editable_id} for element in locations]

                    return jsonify(location_list)
    return jsonify('not json')
        