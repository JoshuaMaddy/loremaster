from operator import and_
from time import sleep
from tkinter.font import families
from typing import Dict, List
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
                character:Dict = character_info.get('character')
                name:str = character.get('name')
                id:int = character.get('id')
                description:str = character_info.get('description')
                traits:List[Dict] = character_info.get('traits')
                stats:List[Dict] = character_info.get('stats')
                relationships:List[Dict] = character_info.get('relationships')
                familiar_ids:List[Dict] = character_info.get('familiar_ids')
                editor_ids:List[Dict] = character_info.get('editor_ids')

                character:Character = sqlsession.execute(select(Character).where(Character.editable_id == id)).scalar()
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user and character: 
                    if character in user.editor_perms:
                        character.name = name
                        character.description = description

                        character.stats = []
                        character.traits = []
                        character.relationships = []
                        character.familiars = []

                        character.editors = []
                        character.editors.append(user)

                        if stats:
                            for stat in stats:
                                new_stat:Stat = Stat(name=stat.get('stat_name'), short_description=stat.get('stat_description'))
                                character.stats.append(new_stat)

                        if traits:
                            for trait in traits:
                                new_trait:Trait = Trait(name=trait.get('trait_name'), short_description=trait.get('trait_description'))
                                character.traits.append(new_trait)

                        if relationships:
                            for relationship in relationships:
                                name:str = relationship.get('relationship_name')
                                character_id:int = relationship.get('character_id')
                                description:str = relationship.get('relationship_desc')

                                print(relationship)


                                if character_id != None:
                                    second_character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
                                    
                                    if second_character in user.editor_perms:
                                        new_relationship:Relationship = Relationship(name=name, short_description=description)
                                        new_relationship.character = second_character

                                        character.relationships.append(new_relationship)

                        if familiar_ids:
                            for familiar_id in familiar_ids:
                                familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.editable2_id == familiar_id)).scalar()

                                if familiar and not familiar in character.familiars:
                                    character.familiars.append(familiar)

                        if editor_ids:
                            for editor_id in editor_ids:
                                editor:User = sqlsession.execute(select(User).where(User.id == editor_id)).scalar()

                                if editor and not editor in character.editors:
                                    character.editors.append(editor)

            return('probably good')
            
    return('probably bad')

@bp.route('/api/search', methods=['POST'])
@login_required
def location_search():

    print(request.data)

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            search_info:dict = request.json
            search_type = search_info.get('search_type')

            if search_type:
                query = search_info.get('query')

                if not query:
                    query = ''

                user = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if search_type == 'location':
                    locations = sqlsession.execute(select(Location).where(and_(Location.name.ilike('%'+query+'%') , Location.editors.contains(user)))).scalars().all()

                    location_list = [{'label':location.name, 'value':location.editable_id} for location in locations]

                    return jsonify(location_list)

                if search_type == 'character':
                    characters = sqlsession.execute(select(Character).where(and_(Character.name.ilike('%'+query+'%') , Character.editors.contains(user), Character.type != 'familiar'))).scalars().all()

                    characters_list = [{'label':character.name, 'value':character.editable_id} for character in characters]

                    return jsonify(characters_list)
                
                if search_type == 'familiar':
                    familiars = sqlsession.execute(select(Familiar).where(and_(Familiar.name.ilike('%'+query+'%') , Familiar.editors.contains(user)))).scalars().all()

                    familiars_list = [{'label':familiar.name, 'value':familiar.editable2_id} for familiar in familiars]

                    return jsonify(familiars_list)

                if search_type == 'user':
                    users = sqlsession.execute(select(User).where(User.name.ilike('%'+query+'%'))).scalars().all()

                    users_list = [{'label':user.name, 'value':user.id} for user in users]

                    return jsonify(users_list)

    return jsonify('not json')
        