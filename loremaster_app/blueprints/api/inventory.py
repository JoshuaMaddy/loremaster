from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():
    """Creates an inventory from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('inventory_id', ''), ('single_editor', ''), ('editor_id', ''), 
        ('item_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the newly created item page.
    """

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.inventory_creation')})

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

            item_ids:list[int] = request.form.getlist('item_id', type=int)
            item_counts:list[int] = request.form.getlist('item_count', type=float)

            inventory:Inventory = Inventory(owner=user, name=name)

            inventory.description = description

            if item_ids:
                inventory.set_items(sqlsession=sqlsession, item_ids=item_ids, item_counts=item_counts)

            if editor_ids:
                inventory.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

            sqlsession.add(inventory)
            sqlsession.flush()

            # Return the url as a JSON object, directs to page for newly created image.
            return(jsonify({'url':url_for('navi.inventory_page', inventory_id=inventory.id)}))
        else:
            flash('User not found in DB.')
            return redirect

def edit():
    """Edits a location from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('inventory_id', ''), ('single_editor', ''), ('editor_id', ''), 
        ('item_id', ''), ('item_count', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the edited item page.
    """

    print(request.form)

    id:int = request.form.get('inventory_id', default=None, type=int)

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.inventory_edit', inventory_id = id)})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            inventory:Inventory = sqlsession.execute(select(Inventory).where(Inventory.id == id)).scalar()

            # Retrieve user given name of image from form data.
            name:str = request.form.get('name', default=None, type=str)

            if not name:
                flash('No name for item.')
                return redirect

            description:str = request.form.get('description', default=None, type=str)

            editor_ids:list[int] = request.form.getlist('editor_id', type=int)

            item_ids:list[int] = request.form.getlist('item_id', type=int)
            item_counts:list[int] = request.form.getlist('item_count', type=float)

            print(item_ids)
            print(item_counts)

            inventory:Inventory = sqlsession.execute(select(Inventory).where(Inventory.id == id)).scalar()

            if inventory:
                if inventory in user.editor_perms: 
                    inventory.name = name
                    inventory.description = description

                    inventory.items = []

                    inventory.editors = []
                    inventory.editors.append(user)

                    if item_ids:
                        inventory.set_items(sqlsession=sqlsession, item_ids=item_ids, item_counts=item_counts)
                    
                    if editor_ids:
                        inventory.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    sqlsession.add(inventory)
                    sqlsession.flush()

                    return(jsonify({'url':url_for('navi.inventory_page', inventory_id=inventory.id)}))

                else:
                    flash('Inventory not in editor permissions.')
                    return redirect
            else:
                flash('Inventory not found in DB.')
                return redirect
        else:
            flash('Inventory not found in DB.')
            return redirect