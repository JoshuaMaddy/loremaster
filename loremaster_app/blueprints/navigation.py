from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, jsonify
)
from flask import session as fsession
from ..database.init_db import Session
from ..database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .auth import login_required

bp = Blueprint('navi', __name__)

@bp.route('/')
def index():
    return render_template('homepage.html')

@bp.route('/user/<int:user_id>')
def user_page(user_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        #  Try to retrieve user from DB session
        user:User = sqlsession.execute(select(User).where(User.id == user_id)).scalar()

        # If no character for id, fail silently
        if user is None:
            return redirect(url_for('navi.index'))
        else:
            # Render user page by passing in user
            return render_template('navigation/user_page.html', user=user)

@bp.route('/character/<int:character_id>')
def character_page(character_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Try to retrieve character from DB session
        character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If Character is owned/can be edited by the viewer
            if character in user.editor_perms:
                editor_perms = True

        # Find first image
        if character.images:
            images = character.images
            images.sort(key = lambda image : image.index)
            image = images[0]

        # If no character for id (or subclass of familiar), fail silently
        if character is None or character.type == 'familiar':
            return redirect(url_for('navi.index'))
        else:
            # Pass character and editor perms to character page to be rendered
            return render_template('navigation/editables/character/character.html', editable=character, editor_perms=editor_perms, image=image)

@bp.route('/character/edit/<int:character_id>')
@login_required
def character_edit(character_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and character: 
            if character in user.editor_perms:
                return render_template('navigation/editables/character/character_edit.html', character=character)
        
        return redirect(url_for('navi.index'))

@bp.route('/familiar/<int:familiar_id>')
def familiar_page(familiar_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.editable_id == familiar_id)).scalar() 

        return render_template('navigation/editables/familiar/familiar_page.html', familiar = familiar)

@bp.route('/location/<int:location_id>')
def location_page(location_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        location:Location = sqlsession.execute(select(Location).where(Location.editable_id == location_id)).scalar()

        return render_template('navigation/editables/location/location_page.html', location=location)

@bp.route('/inventory/<int:inventory_id>')
def inventory_page(inventory_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        inventory:Inventory = sqlsession.execute(select(Inventory).where(Inventory.editable_id == inventory_id)).scalar()

        return render_template('navigation/editables/inventory/inventory_page.html', inventory = inventory )

@bp.route('/item/<int:item_id>')
def item_page(item_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        item:Item = sqlsession.execute(select(Item).where(Item.editable_id == item_id)).scalar()

        return render_template('navigation/editables/inventory/item/item.html', item = item )

@bp.route('/image/<int:image_id>')
def image_page(image_id:int):
    return 'image page placeholder'

@bp.route('/guild/<int:guild_id>')
def guild_page(guild_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        guild:Guild = sqlsession.execute(select(Guild).where(Guild.editable_id == guild_id)).scalar()

        return render_template('navigation/editables/guild/guild_page.html', guild = guild )

@bp.route('/search')
def search():
    return render_template('search.html')
