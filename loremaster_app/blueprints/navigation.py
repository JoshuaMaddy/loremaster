from ast import In
from operator import inv
from flask import (
    Blueprint, g, redirect, render_template, url_for
)
from ..database.init_db import Session
from ..database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .auth import login_required

bp = Blueprint('navi', __name__)

@bp.route('/')
def index():
    if g.user:
        with Session.begin() as sqlsession:
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            return render_template('homepage.html', user=user)

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

@bp.route('/create/')
def create():
    return render_template('navigation/editables/create_editable.html')

@bp.route('/character/<int:character_id>')
def character_page(character_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Try to retrieve character from DB session
        character:Character = sqlsession.execute(select(Character).where(Character.id == character_id)).scalar()

        # If no character for id (or subclass of familiar), fail silently
        if character is None or character.type == 'familiar':
            return redirect(url_for('navi.index'))

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

        # Pass character and editor perms to character page to be rendered
        return render_template('navigation/editables/character/character.html', editable=character, editor_perms=editor_perms, image=image, Visibility=Visibilites)

@bp.route('/character/create/')
@login_required
def character_creation():
        return render_template('navigation/editables/character/character_creation.html', character=None, Visibility=Visibilites)

@bp.route('/character/edit/<int:character_id>')
@login_required
def character_edit(character_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        character:Character = sqlsession.execute(select(Character).where(Character.id == character_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and character: 
            if character in user.editor_perms:
                return render_template('navigation/editables/character/character_edit.html', character=character, Visibility=Visibilites)
        
        return redirect(url_for('navi.index'))

@bp.route('/image/<int:image_id>')
def image_page(image_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # Try to retrieve image from DB session
        image:Image = sqlsession.execute(select(Image).where(Image.id == image_id)).scalar()

        # If no image for id (or subclass of familiar), fail silently
        if not image:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If image is owned/can be edited by the viewer
            if image in user.editor_perms:
                editor_perms = True

        # Pass image and editor perms to image page to be rendered
        return render_template('navigation/editables/image/image.html', editable=image, editor_perms=editor_perms)

@bp.route('/image/create/')
@login_required
def image_creation():
        return render_template('navigation/editables/image/image_creation.html', image=None)

@bp.route('/image/edit/<int:image_id>')
@login_required
def image_edit(image_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        image:Image = sqlsession.execute(select(Image).where(Image.id == image_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and image: 
            if image in user.editor_perms:
                return render_template('navigation/editables/image/image_edit.html', image=image)
        
        return redirect(url_for('navi.index'))

@bp.route('/familiar/<int:familiar_id>')
def familiar_page(familiar_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # Try to retrieve familiar from DB session
        familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.id == familiar_id)).scalar() 

        # If no image for id (or subclass of familiar), fail silently
        if not familiar:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If image is owned/can be edited by the viewer
            if familiar in user.editor_perms:
                editor_perms = True

        # Find first image
        if familiar.images:
            images = familiar.images
            images.sort(key = lambda image : image.index)
            image = images[0]

        return render_template('navigation/editables/familiar/familiar.html', editable=familiar, editor_perms=editor_perms, image=image)

@bp.route('/familiar/edit/<int:familiar_id>')
@login_required
def familiar_edit(familiar_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.id == familiar_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and familiar: 
            if familiar in user.editor_perms:
                return render_template('navigation/editables/familiar/familiar_edit.html', familiar=familiar)
        
        return redirect(url_for('navi.index'))

@bp.route('/location/<int:location_id>')
def location_page(location_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # Try to retrieve image from DB session
        location:Location = sqlsession.execute(select(Location).where(Location.id == location_id)).scalar()

        # If no image for id (or subclass of familiar), fail silently
        if not location:
            return redirect(url_for('navi.index'))

        # Find first image
        if location.images:
            images = location.images
            images.sort(key = lambda image : image.index)
            image = images[0]

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If image is owned/can be edited by the viewer
            if location in user.editor_perms:
                editor_perms = True

        # Pass image and editor perms to image page to be rendered
        return render_template('navigation/editables/location/location.html', editable=location, image=image, editor_perms=editor_perms)

@bp.route('/location/create/')
@login_required
def location_creation():
        return render_template('navigation/editables/location/location_creation.html', location=None)

@bp.route('/location/edit/<int:location_id>')
@login_required
def location_edit(location_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        location:Location = sqlsession.execute(select(Location).where(Location.id == location_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and location: 
            if location in user.editor_perms:
                return render_template('navigation/editables/location/location_edit.html', location=location)
        
        return redirect(url_for('navi.index'))

@bp.route('/inventory/<int:inventory_id>')
def inventory_page(inventory_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image

        # Try to retrieve image from DB session
        inventory:Inventory = sqlsession.execute(select(Inventory).where(Inventory.id == inventory_id)).scalar()

        # If no image for id (or subclass of familiar), fail silently
        if not inventory:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If image is owned/can be edited by the viewer
            if inventory in user.editor_perms:
                editor_perms = True

        # Pass image and editor perms to image page to be rendered
        return render_template('navigation/editables/inventory/inventory.html', editable=inventory, editor_perms=editor_perms)

@bp.route('/inventory/create/')
@login_required
def inventory_creation():
        return render_template('navigation/editables/inventory/inventory_creation.html', inventory=None)

@bp.route('/inventory/edit/<int:inventory_id>')
@login_required
def inventory_edit(inventory_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        inventory:Inventory = sqlsession.execute(select(Inventory).where(Inventory.id == inventory_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and inventory: 
            if inventory in user.editor_perms:
                return render_template('navigation/editables/inventory/inventory_edit.html', inventory=inventory)
        
        return redirect(url_for('navi.index'))

@bp.route('/item/<int:item_id>')
def item_page(item_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # Try to retrieve image from DB session
        item:Item = sqlsession.execute(select(Item).where(Item.id == item_id)).scalar()

        # If no image for id (or subclass of familiar), fail silently
        if not item:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
            # If image is owned/can be edited by the viewer
            if item in user.editor_perms:
                editor_perms = True

        # Find first image
        if item.images:
            images = item.images
            images.sort(key = lambda image : image.index)
            image = images[0]

        # Pass image and editor perms to image page to be rendered
        return render_template('navigation/editables/inventory/item/item.html', editable=item, image=image, editor_perms=editor_perms)

@bp.route('/item/create/')
@login_required
def item_creation():
        return render_template('navigation/editables/inventory/item/item_creation.html', item=None)

@bp.route('/item/edit/<int:item_id>')
@login_required
def item_edit(item_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        item:Item = sqlsession.execute(select(Item).where(Item.id == item_id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user and item: 
            if item in user.editor_perms:
                return render_template('navigation/editables/inventory/item/item_edit.html', item=item)
        
        return redirect(url_for('navi.index'))

@bp.route('/guild/<int:guild_id>')
def guild_page(guild_id:int):
    with Session.begin() as sqlsession: 
        sqlsession:Ses

        guild:Guild = sqlsession.execute(select(Guild).where(Guild.id == guild_id)).scalar()

        return render_template('navigation/editables/guild/guild_page.html', guild = guild )

@bp.route('/search')
def search():
    return render_template('search.html')

@bp.route('/browse')
def browse():
    with Session.begin() as sqlsession: 
        sqlsession:Ses
        characters:list[Character] = sqlsession.execute(select(Character).where(Editable.visibility == Visibilites.public)).scalars()

        return render_template('navigation/browse.html', characters=characters)
