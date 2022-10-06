from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, jsonify
)
from flask import session as fsession
from ..database.init_db import Session
from ..database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .auth import login, login_required

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
        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If Character is owned/can be edited by the viewer
            if character in user.editor_perms:
                editor_perms = True

        # If no character for id (or subclass of familiar), fail silently
        if character is None or character.type == 'familiar':
            return redirect(url_for('navi.index'))
        else:
            # Pass character and editor perms to character page to be rendered
            return render_template('navigation/editables/character/character.html', editable=character, editor_perms=editor_perms)

@bp.route('/familiar/<int:familiar_id>')
def familiar_page(familiar_id:int):
    return 'familiar page placeholder'

@bp.route('/location/<int:location_id>')
def location_page(location_id:int):
    return 'location page placeholder'

@bp.route('/inventory/<int:inventory_id>')
def inventory_page(inventory_id:int):
    return 'inventory page placeholder'

@bp.route('/item/<int:item_id>')
def item_page(item_id:int):
    return 'item page placeholder'

@bp.route('/image/<int:image_id>')
def image_page(image_id:int):
    return 'image page placeholder'

@bp.route('/guild/<int:guild_id>')
def guild_page(guild_id:int):
    return 'guild page placeholder'