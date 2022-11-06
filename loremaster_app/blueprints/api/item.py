from flask import (
    g, request, url_for, jsonify, flash, render_template
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def user_grid():
    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            items:list[Item] = sqlsession.execute(select(Item).where(Item.editors.contains(user))).scalars().all()

            return render_template('snippets/item_grid.html', items=items)

def create():
    """Creates an item from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('item_id', ''), ('single_editor', ''), 
        ('editor_id', ''), ('image_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the newly created item page.
    """

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.item_creation')})

    print(request.form)

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            # Retrieve user given name of image from form data.
            name:str = request.form.get('name', default=None, type=str)

            if not name:
                flash('No name for item.')
                return redirect

            description:str = request.form.get('description', default=None, type=str)

            editor_ids:list[int] = request.form.getlist('editor_id', type=int)

            image_ids:list[int] = request.form.getlist('image_id', type=int)

            item:Item = Item(owner=user, name=name)

            item.description = description

            if image_ids:
                item.set_images(sqlsession=sqlsession, image_ids=image_ids)
            
            if editor_ids:
                item.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

            sqlsession.add(item)
            sqlsession.flush()

            # Return the url as a JSON object, directs to page for newly created image.
            return(jsonify({'url':url_for('navi.item_page', item_id=item.id)}))
        else:
            flash('User not found in DB.')
            return redirect

def edit():
    """Edits a location from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('item_id', ''), ('single_editor', ''), 
        ('editor_id', ''), ('image_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the edited item page.
    """

    id:int = request.form.get('item_id', default=None, type=int)

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.item_edit', item_id = id)})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Retrieve user given name of image from form data.
        name:str = request.form.get('name', default=None, type=str)

        if not name:
            flash('No name for location')
            return redirect

        description:str = request.form.get('description', default=None, type=str)

        editor_ids:list[int] = request.form.getlist('editor_id', type=int)

        image_ids:list[int] = request.form.getlist('image_id', type=int)

        item:Item = sqlsession.execute(select(Item).where(Item.id == id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            if item:
                if item in user.editor_perms: 
                    item.name = name
                    item.description = description

                    item.images = []

                    item.editors = []
                    item.editors.append(user)

                    if image_ids:
                        item.set_images(sqlsession=sqlsession, image_ids=image_ids)
                    
                    if editor_ids:
                        item.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    return(jsonify({'url':url_for('navi.item_page', item_id=item.id)}))

                else:
                    flash('Item not in editor permissions.')
                    return redirect
            else:
                flash('Item not found in DB.')
                return redirect
        else:
            flash('User not found in DB.')
            return redirect