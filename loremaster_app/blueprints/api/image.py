import os
import uuid

from flask import (
    flash, g, render_template, request, url_for, send_file, jsonify, current_app, Response
)
from werkzeug.utils import secure_filename

from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .utility import allowed_file

def retrieve(image_id:int) -> Response:
    """Provides an image as a file based on image_id.

    Args:
        image_id (int): An Image objects editable_id.

    Returns:
        Response
    """
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Select image object from DB based on image's id.
        image:Image = sqlsession.execute(select(Image).where(Image.editable_id == image_id)).scalar()

        if image:
            if os.path.exists(image.image_path):
                return send_file(image.image_path, mimetype='image')

def user_grid() -> str:
    """Generates an HTML snippet of all the user's photos in a grid.

    Returns:
        str: HTML snippet
    """
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Select all images from the currently logged in user's library.
        images = sqlsession.execute(select(Image).where(Image.owner_id == g.user.id)).scalars().all()

        return render_template('snippets/image_grid.html', images=images)

def create():
    """Creates an image from a POST request with the given form data:
        ImmutableMultiDict([('name', ''), ('image_id', ''), ('single_editor', ''),
            ('editor_id', ''), ('description', '')])
    Returns:
        Redirect: redirect JSON to the create page so as to flash error
        Json: Json that directs to the newly created image page
    """

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.image_creation')})

    # If the field 'choose-file' is not present in the files section of the request
    if 'choose-file' not in request.files:
        flash('No file part')
        return redirect
    
    file = request.files['choose-file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            if file and allowed_file(file.filename) and user:
                # Ensure secure filename.
                filename = secure_filename(file.filename)

                # If a file with the name already exists, create a random name.
                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
                    file_type = filename.rsplit('.', 1)[1].lower()

                    filename = str(uuid.uuid4()) + f".{file_type}"

                # Retrieve user given name of image from form data.
                name:str = request.form.get('name')

                if not name:
                    flash('No name for image')
                    return redirect
                
                # Create a list of given editor values from form data.
                editor_ids:list[int] = request.form.getlist('editor_id', type=int)

                # Set a description from form data.
                description:str = request.form.get('description')

                # Create a new Image object and set the appropriate values.
                image = Image(owner = user, name = name, \
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                image.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)
                image.description = description

                # After succesful object creation/assignment, save image form memory to hdd.
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                # Add object to DB and flush to assign editable_id.
                sqlsession.add(image)
                sqlsession.flush()

                # Return the url as a JSON object, directs to page for newly created image.
                return(jsonify({'url':url_for('navi.image_page', image_id=image.editable_id)}))

            # See corresponding if
            flash('Incorrect file type.')
            return redirect

        # See corresponding if
        flash('User not found in DB.')
        return redirect

def edit():
    """Edits an image from a POST request with the given form data:
        ImmutableMultiDict([('name', ''), ('image_id', ''), ('single_editor', ''),
            ('editor_id', ''), ('description', '')])
    Returns:
        Redirect: redirect JSON to the create page so as to flash error
        Json: Json that directs to the updated image page
    """

    # This is a similar format to image_creation, reference it for comments.
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.image_edit', image_id=int(request.form.get('image_id')))})

    if 'choose-file' not in request.files:
        flash('No file part')
        return redirect

    file = request.files['choose-file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    filename = None
    if file.filename != '':
        if file and allowed_file(file.filename):
                # File prep
                filename = secure_filename(file.filename)

                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)):
                    file_type = filename.rsplit('.', 1)[1].lower()

                    filename = str(uuid.uuid4()) + f".{file_type}"
        else:
            flash('Incorrect file type.')
            return redirect

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            name:str = request.form.get('name')

            if not name:
                flash('No name for image')
                return redirect

            image_id:int = request.form.get('image_id', default=None, type=int)

            if not image_id:
                flash('Image ID error')
                return redirect

            image:Image = sqlsession.execute(select(Image).where(Image.editable_id == image_id)).scalar()
            
            editor_ids:list[int] = request.form.getlist('editor_id', type=int)

            description:str = request.form.get('description')

            if image:
                image.editors = []
                image.editors.append(user)

                image.description = description
                image.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                if filename:
                    os.remove(image.image_path)
                    image.image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            sqlsession.flush()

            return(jsonify({'url':url_for('navi.image_page', image_id=image.editable_id)}))

        flash('User not found in DB.')
        return redirect