from flask import (
    Blueprint, g, redirect, render_template, url_for
)
from ..database.init_db import Session
from ..database.table_declarations import *
from ..database.queries import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .auth import login_required

bp = Blueprint('navi', __name__)

@bp.route('/')
def index():
    if g.user:
        with Session.begin() as sqlsession:
            user:User = get_user(session=sqlsession, user_id=g.user.id)

            return render_template('homepage.html', user=user)

    return render_template('homepage.html')

@bp.route('/admin_panel')
@login_required
def admin_panel():
    if g.user:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            user:User = get_user(session=sqlsession, user_id=g.user.id)

            if user and user.admin_status:
                return render_template('navigation/admin/admin_panel.html', user=user)

    return redirect(url_for('navi.index'))

@bp.route('/user_panel')
@login_required
def user_panel():
    if g.user:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            user:User = get_user(session=sqlsession, user_id=g.user.id)

            if user:
                return render_template('navigation/user/user_info_edit.html', user=user)

    return redirect(url_for('navi.index'))

@bp.route('/user/<int:user_id>')
def user_page(user_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        #  Try to retrieve user from DB session
        user:User = get_user(session=sqlsession, user_id=g.user.id)

        # If no character for id, fail silently
        if user is None:
            return redirect(url_for('navi.index'))
        else:
            # Render user page by passing in user
            return render_template('navigation/user_page.html', user=user)

@bp.route('/create/')
def create():
    return render_template('navigation/editables/create_editable.html')


@bp.route('/guild/<int:guild_id>')
def guild_page(guild_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Try to retrieve guild from DB session
        guild:Guild = sqlsession.execute(select(Guild).where(Guild.id == guild_id)).scalar()

        # If no guild for id (or subclass of familiar), fail silently
        if guild is None:
            return redirect(url_for('navi.index'))

        # Assume that viewer is not editor
        editor_perms = False
        # Assume no image
        image = None

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = get_user(session=sqlsession, user_id=g.user.id)
            # If guild is owned/can be edited by the viewer
            if guild in user.editor_perms:
                editor_perms = True

        # Find first image
        if guild.images:
            images = guild.images
            images.sort(key = lambda image : image.index)
            image = images[0]

        # Pass guild and editor perms to character page to be rendered
        return render_template('navigation/editables/guild/guild.html', editable=guild, editor_perms=editor_perms, image=image, Visibility=Visibilites)

@bp.route('/guild/guild_create')
@login_required
def guild_create():
        return render_template('navigation/editables/guild/guild_create.html', guild=None, Visibility=Visibilites)

@bp.route('/guild/edit/<int:guild_id>')
@login_required
def guild_edit(guild_id:int):
     with Session.begin() as sqlsession:
        sqlsession:Ses

        guild:Guild = sqlsession.execute(select(Guild).where(Guild.id == guild_id)).scalar()
        user:User = get_user(session=sqlsession, user_id=g.user.id)

        if user and guild: 
            if guild in user.editor_perms:
                return render_template('navigation/editables/guild/guild_edit.html', guild=guild, Visibility=Visibilites)
        
        return redirect(url_for('navi.index'))

@bp.route('/character/<int:character_id>')
def character_page(character_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Try to retrieve character from DB session
        character:Character = get_element_by_id(session=sqlsession, element_type=Character, element_id=character_id)

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
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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

        character:Character = get_element_by_id(session=sqlsession, element_type=Character, element_id=character_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

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
        image:Image = get_element_by_id(session=sqlsession, element_type=Image, element_id=image_id)

        # If no image for id (or subclass of familiar), fail silently
        if not image:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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

        image:Image = get_element_by_id(session=sqlsession, element_type=Image, element_id=image_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

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
        familiar:Familiar = get_element_by_id(session=sqlsession, element_type=Familiar, element_id=familiar_id)

        # If no image for id (or subclass of familiar), fail silently
        if not familiar:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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


        familiar:Familiar = get_element_by_id(session=sqlsession, element_type=Familiar, element_id=familiar_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

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
        location:Location = get_element_by_id(session=sqlsession, element_type=Location, element_id=location_id)

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
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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

        location:Location = get_element_by_id(session=sqlsession, element_type=Location, element_id=location_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

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
        inventory:Inventory = get_element_by_id(session=sqlsession, element_type=Inventory, element_id=inventory_id)

        # If no image for id (or subclass of familiar), fail silently
        if not inventory:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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

        inventory:Inventory = get_element_by_id(session=sqlsession, element_type=Inventory, element_id=inventory_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

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
        item:Item = get_element_by_id(session=sqlsession, element_type=Item, element_id=item_id)

        # If no image for id (or subclass of familiar), fail silently
        if not item:
            return redirect(url_for('navi.index'))

        # If logged in
        if g.user:
            # Retrieve up to date user info
            user:User = get_user(session=sqlsession, user_id=g.user.id)
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

        item:Item = get_element_by_id(session=sqlsession, element_type=Item, element_id=item_id)
        user:User = get_user(session=sqlsession, user_id=g.user.id)

        if user and item: 
            if item in user.editor_perms:
                return render_template('navigation/editables/inventory/item/item_edit.html', item=item)
        
        return redirect(url_for('navi.index'))



@bp.route('/search')
def search():
    return render_template('search.html')

@bp.route('/browse')
def browse():
    with Session.begin() as sqlsession: 
        sqlsession:Ses
        characters:list[Character] = sqlsession.execute(select(Character).where(Character.visibility == Visibilites.public)).scalars()

        return render_template('navigation/browse.html', characters=characters)
