from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():
    """Creates a location from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('location_id', ''), ('parent_location', ''), ('parent_location_id', ''), 
        ('single_location', ''), ('single_location_id', ''), ('single_editor', ''), ('editor_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the newly created location page.
    """

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.location_creation')})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            # Retrieve user given name of image from form data.
            name:str = request.form.get('name', default=None, type=str)

            if not name:
                flash('No name for location.')
                return redirect

            description:str = request.form.get('description', default=None, type=str)

            parent_location_id:int = request.form.get('parent_location_id', default=None, type=int)
            children_location_ids:int = request.form.getlist('single_location_id', type=int)

            editor_ids:list[int] = request.form.getlist('editor_id', type=int)

            image_ids:list[int] = request.form.getlist('image_id', type=int)

            location:Location = Location(owner=user, name=name)

            location.description = description

            if parent_location_id:
                location.set_parent(sqlsession=sqlsession, parent_location_id=parent_location_id)
            
            if children_location_ids:
                location.set_children(sqlsession=sqlsession, children_location_ids=children_location_ids)
            
            if image_ids:
                location.set_images(sqlsession=sqlsession, image_ids=image_ids)
            
            if editor_ids:
                location.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

            sqlsession.add(location)
            sqlsession.flush()

            # Return the url as a JSON object, directs to page for newly created image.
            return(jsonify({'url':url_for('navi.location_page', location_id=location.id)}))
        else:
            flash('User not found in DB.')
            return redirect

def edit():
    """Edits a location from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('location_id', ''), ('parent_location', ''), ('parent_location_id', ''), 
        ('single_location', ''), ('single_location_id', ''), ('single_editor', ''), ('editor_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the edited location page.
    """

    id:int = request.form.get('location_id', default=None, type=int)

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.location_edit', location_id = id)})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Retrieve user given name of image from form data.
        name:str = request.form.get('name', default=None, type=str)

        if not name:
            flash('No name for location.')
            return redirect

        description:str = request.form.get('description', default=None, type=str)

        parent_location_id:int = request.form.get('parent_location_id', default=None, type=int)
        children_location_ids:int = request.form.getlist('single_location_id', type=int)

        editor_ids:list[int] = request.form.getlist('editor_id', type=int)

        image_ids:list[int] = request.form.getlist('image_id', type=int)


        location:Location = sqlsession.execute(select(Location).where(Location.id == id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            if location:
                if location in user.editor_perms: 
                    location.name = name
                    location.description = description

                    location.parent = None
                    location.children = []
                    location.images = []

                    location.editors = []
                    location.editors.append(user)

                    if parent_location_id:
                        location.set_parent(sqlsession=sqlsession, parent_location_id=parent_location_id)
                    
                    if children_location_ids:
                        location.set_children(sqlsession=sqlsession, children_location_ids=children_location_ids)
                    
                    if image_ids:
                        location.set_images(sqlsession=sqlsession, image_ids=image_ids)
                    
                    if editor_ids:
                        location.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    return(jsonify({'url':url_for('navi.location_page', location_id=location.id)}))

                else:
                    flash('Location not in editor permissions.')
                    return redirect
            else:
                flash('Location not found in DB.')
                return redirect
        else:
            flash('User not found in DB.')
            return redirect