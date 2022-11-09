from operator import inv
import os

from flask import (
    Blueprint, g, redirect, request, jsonify, render_template, url_for
)

from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import or_, select, and_
from sqlalchemy.orm import Session as Ses

from ..auth import login_required

from . import image, character, familiar, location, item, inventory

bp = Blueprint('api', __name__)

@bp.route('/api/image/<int:image_id>', methods=['GET'])
def image_retrieve(image_id:int):
    return image.retrieve(image_id=image_id)

@bp.route('/api/user_image_grid', methods=['GET'])
def user_image_grid():
    return image.user_grid()

@bp.route('/api/user_item_grid', methods=['GET'])
def user_item_grid():
    return item.user_grid()

@bp.route('/api/character_create', methods=['POST'])
@login_required
def character_create():
    return character.create()

@bp.route('/api/character_edit', methods=['POST'])
@login_required
def character_edit():
    return character.edit()

@bp.route('/api/familiar_edit', methods=['POST'])
@login_required
def familiar_edit():
    return familiar.edit()

@bp.route('/api/image_create', methods=['POST'])
@login_required
def image_create():
    return image.create()

@bp.route('/api/image_edit', methods=['POST'])
@login_required
def image_edit():
    return image.edit()

@bp.route('/api/location_create', methods=['POST'])
@login_required
def location_create():
    return location.create()

@bp.route('/api/location_edit', methods=['POST'])
@login_required
def location_edit():
    return location.edit()

@bp.route('/api/item_create', methods=['POST'])
@login_required
def item_create():
    return item.create()

@bp.route('/api/item_edit', methods=['POST'])
@login_required
def item_edit():
    return item.edit()

@bp.route('/api/inventory_create', methods=['POST'])
@login_required
def inventory_create():
    return inventory.create()

@bp.route('/api/inventory_edit', methods=['POST'])
@login_required
def inventory_edit():
    return inventory.edit()

@bp.route('/api/search', methods=['POST'])
@login_required
def search():
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

                    location_list = [{'label':location.name, 'value':location.id} for location in locations]

                    return jsonify(location_list)

                if search_type == 'character':
                    characters = sqlsession.execute(select(Character).where(and_(Character.name.ilike('%'+query+'%') , Character.editors.contains(user)))).scalars().all()

                    characters_list = [{'label':character.name, 'value':character.id} for character in characters]

                    return jsonify(characters_list)
                
                if search_type == 'familiar':
                    familiars = sqlsession.execute(select(Familiar).where(and_(Familiar.name.ilike('%'+query+'%') , Familiar.editors.contains(user)))).scalars().all()

                    familiars_list = [{'label':familiar.name, 'value':familiar.id} for familiar in familiars]

                    return jsonify(familiars_list)

                if search_type == 'user':
                    users = sqlsession.execute(select(User).where(User.name.ilike('%'+query+'%'))).scalars().all()

                    users_list = [{'label':user.name, 'value':user.id} for user in users]

                    return jsonify(users_list)

    return jsonify('not json')

@bp.route('/api/delete_editable', methods=['POST'])
def delete_editable():
    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            delete_info:dict = request.json
            id = delete_info.get('id')

            editable:Editable = sqlsession.execute(select(Editable).where(Editable.id == id)).scalar()

            if editable:
                if editable.type == 'image':

                    imageListItems:list[ImageListItem] = sqlsession.execute(select(ImageListItem).where(ImageListItem.image_id == editable.id)).scalars().all()

                    for imageListItem in imageListItems:
                        sqlsession.delete(imageListItem)

                    editable:Image
                    os.remove(editable.image_path)

                sqlsession.delete(editable)

                return('probably good')
            
    return('probably bad')

@bp.route('/api/list_query', methods=['POST'])
@login_required
def list_query():
    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            search_info:dict = request.json
            search_type = search_info.get('search_type')
            
            if search_type:
                        query = search_info.get('query')
                        tag = search_info.get('tag')

                        if not query:
                            query = ''

                        user = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()
                        if search_type == 'character':
                            if not tag:
                                tag = 'character'
                            if (tag == 'character'):
                                characters = sqlsession.execute(select(Character).where(and_(Character.name.ilike('%'+query+'%'), or_((Character.editors.contains(user)), Character.visibility == Visibilites.public)))).scalars().all()
                                return render_template('snippets/browse.html', characters=characters)
                            if (tag == 'location'):
                                characters:Character = sqlsession.execute(select(Character).join(Location, Character.location_id == Location.editable_id).where(and_(Location.name.ilike('%'+query+'%'), or_((Character.editors.contains(user)), Character.visibility == Visibilites.public)))).scalars().all()
                                return render_template('snippets/browse.html', characters=characters)
                            if (tag == 'user'):
                                characters:Character = sqlsession.execute(select(Character).join(User, Character.owner_id == User.id).where(and_((User.name.ilike('%'+query+'%')), or_((Character.editors.contains(user)), Character.visibility == Visibilites.public)))).scalars().all()
                                return render_template('snippets/browse.html', characters=characters)

                        if search_type == 'location':
                            if not tag:
                                tag = 'location'
                            if (tag == 'location' or tag == 'character'):
                                locations:Location = sqlsession.execute(select(Location).where(and_(Location.name.ilike('%'+query+'%'), or_((Location.editors.contains(user)), Location.visibility == Visibilites.public)))).scalars().all()
                                return render_template('snippets/browse.html', locations=locations)
                            if (tag == 'user'):
                                locations:Location = sqlsession.execute(select(Location).join(User, Location.owner_id == User.id).where(and_((User.name.ilike('%'+query+'%')), or_((Location.editors.contains(user)), Location.visibility == Visibilites.public)))).scalars().all()
                                return render_template('snippets/browse.html', locations=locations)

            return render_template('navigation/browse.html')