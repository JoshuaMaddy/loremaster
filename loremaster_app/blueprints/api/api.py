import os

from flask import (
    Blueprint, g, redirect, request, jsonify, render_template, url_for
)

from ...database.init_db import Session
from ...database.table_declarations import *
from ...database.queries import *

from sqlalchemy import or_, select, and_
from sqlalchemy.orm import Session as Ses

from ..auth import login_required

from . import image, character, familiar, location, item, inventory, guild, user


bp = Blueprint('api', __name__)

@bp.route('/api/user_edit', methods=['POST'])
def user_edit():
    return user.edit()

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

@bp.route('/api/familiar_create', methods=['POST'])
@login_required
def familiar_create():
    return familiar.create()

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

@bp.route('/api/guild_create', methods=['POST'])
@login_required
def guild_create():
    return guild.create()

@bp.route('/api/guild_edit', methods=['POST'])
@login_required
def guild_edit():
    return guild.edit()

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
                    locations = sqlsession.execute(select(Location).where(and_(Location.name.ilike('%'+query+'%'), Location.editors.contains(user)))).scalars().all()

                    location_list = [{'label':location.name, 'value':location.id} for location in locations]

                    return jsonify(location_list)

                if search_type == 'character' or search_type == 'leader':
                    characters:set[Character] = sqlsession.execute(\
                        select(Character).where(\
                            and_(\
                                Character.name.ilike('%'+query+'%') , \
                                    #or_(\
                                        Character.editors.contains(user) \
                                        #Character.visibility == Visibilites.public)\
                                    #)\
                                ))).scalars().all()

                    characters_list = [{'label':character.name, 'value':character.id} for character in characters]

                    return jsonify(characters_list)
                
                if search_type == 'familiar':
                    familiars:set[Familiar] = sqlsession.execute(select(Familiar).where(and_(Familiar.name.ilike('%'+query+'%'), Familiar.editors.contains(user)))).scalars().all()

                    familiars_list = [{'label':familiar.name, 'value':familiar.id} for familiar in familiars]

                    return jsonify(familiars_list)

                if search_type == 'user':
                    users = sqlsession.execute(select(User).where(User.name.ilike('%'+query+'%'))).scalars().all()

                    users_list = [{'label':user.name, 'value':user.id} for user in users]

                    return jsonify(users_list)

                if search_type == 'guild':
                    guilds = sqlsession.execute(select(Guild).where(and_(Guild.name.ilike('%'+query+'%') , Guild.editors.contains(user)))).scalars().all()

                    guild_list = [{'label':guild.name, 'value':guild.id} for guild in guilds]

                    return jsonify(guild_list)

                if search_type == 'item':
                    items = sqlsession.execute(select(Item).where(and_(Item.name.ilike('%'+query+'%') , Item.editors.contains(user)))).scalars().all()

                    item_list = [{'label':item.name, 'value':item.id} for item in items]

                    return jsonify(item_list)

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
def list_query():
    normal_browse:str = 'snippets/browse.html'
    admin_browse:str = 'snippets/admin_browse.html'

    route:str = normal_browse

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            user:User = None

            if g.user:
                user:User = get_user(session=sqlsession, user_id=g.user.id)

            if user and user.admin_status:
                route = admin_browse

            search_info:dict = request.json
            search_type:str = search_info.get('search_type')
            
            if search_type:
                query:str = search_info.get('query')
                tag:str = search_info.get('tag')

                if not query:
                    query = ''
                
                if search_type == 'character':

                    characters:list[Character] = None

                    if query == "":
                        characters:list[Character] = sqlsession.execute(select(Character).where(Character.visibility == Visibilites.public)).scalars()
                    else:   
                        if not tag:
                            tag = 'character'                    

                        if (tag == 'character'):
                            characters:list[Character] = sqlsession.execute(select(Character)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Character.name.ilike('%'+query+'%'),\
                                                                                        #or_(\
                                                                                        #   Character.editors.contains(user),\
                                                                                            Character.visibility == Visibilites.public
                                                                                        #)
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters2:list[Character] = sqlsession.execute(select(Character)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Character.name.ilike('%'+query+'%'),\
                                                                                        #or_(\
                                                                                           Character.editors.contains(user)
                                                                                            #Character.visibility == Visibilites.public
                                                                                        #)
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters = set(characters).union(set(characters2))

                        if (tag == 'location'):
                            characters:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(Location, Character.location_id == Location.editable_id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Location.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                            #    Character.editors.contains(user),\
                                                                                                Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                        #or_(\
                                                                                            #    Location.editors.contains(user),\
                                                                                                Location.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters2:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(Location, Character.location_id == Location.editable_id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Location.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                               Character.editors.contains(user)
                                                                                            #    Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                        #or_(\
                                                                                                Location.editors.contains(user)
                                                                                            #    Location.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters = set(characters).union(characters2)

                        if (tag == 'user'):
                            characters:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(User, Character.owner_id == User.id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        User.name.ilike('%'+query+'%'),\
                                                                                        #or_(\
                                                                                        #    Character.editors.contains(user),\
                                                                                            Character.visibility == Visibilites.public
                                                                                        #)
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters2:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(User, Character.owner_id == User.id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        User.name.ilike('%'+query+'%'),\
                                                                                        #or_(\
                                                                                            Character.editors.contains(user)
                                                                                        #    Character.visibility == Visibilites.public
                                                                                        #)
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)     

                            characters = set(characters).union(characters2)                                                                       

                        if (tag == 'guild'):
                            characters:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(Guild, Character.guild_id == Guild.editable_id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Guild.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                            #    Character.editors.contains(user),\
                                                                                                Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                            #    Guild.editors.contains(user),\
                                                                                                Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)

                            characters2:list[Character] = sqlsession.execute(select(Character)\
                                                                                .join(Guild, Character.guild_id == Guild.editable_id)\
                                                                                .where(\
                                                                                    and_(\
                                                                                        Guild.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                                Character.editors.contains(user)
                                                                                            #    Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                                Guild.editors.contains(user)
                                                                                            #    Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                    )
                                                                                )
                                                                            ).scalars().fetchmany(100)    

                            characters = set(characters).union(set(characters2))                                                                                                                            

                        if (tag == 'familiar'):
                            characters:set[Character] = set()
                            familiars:list[Familiar] = sqlsession.execute(select(Familiar)\
                                .where(\
                                    and_(\
                                        Familiar.name.ilike('%'+query+'%') ,\
                                            and_(\
                                                #or_(\
                                                #    Character.editors.contains(user),\
                                                    Character.visibility == Visibilites.public
                                                ,#),
                                                #or_(\
                                                #    Familiar.editors.contains(user),\
                                                    Familiar.visibility == Visibilites.public
                                                #)                                                                                    
                                            )
                                        )
                                    )
                                ).scalars().fetchmany(100)
                            
                            familiars2:list[Familiar] = sqlsession.execute(select(Familiar)\
                                .where(\
                                    and_(\
                                        Familiar.name.ilike('%'+query+'%') ,\
                                            and_(\
                                                #or_(\
                                                    Character.editors.contains(user)
                                                #    Character.visibility == Visibilites.public
                                                ,#),
                                                #or_(\
                                                   Familiar.editors.contains(user)
                                                #    Familiar.visibility == Visibilites.public
                                                #)                                                                                    
                                            )
                                        )
                                    )
                                ).scalars().fetchmany(100)

                            familiars = set(familiars).union(set(familiars2))

                            for familiar in familiars:
                                if familiar.owners:
                                    for owner in familiar.owners:
                                        characters.add(owner)

                    return render_template(route, characters=characters)

                if search_type == 'location':

                    locations:list[Location] = None

                    if query == "":
                        locations:list[Character] = sqlsession.execute(select(Location).where(Location.visibility == Visibilites.public)).scalars()
                    else:   

                        if not tag:
                            tag = 'location'
                        if (tag == 'location'):
                            locations:list[Location] = sqlsession.execute(select(Location)\
                                                                            .where(\
                                                                                and_(\
                                                                                    Location.name.ilike('%'+query+'%'),\
                                                                                    #or_(\
                                                                                    #    Location.editors.contains(user),\
                                                                                        Location.visibility == Visibilites.public
                                                                                    #)
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)

                            locations2:list[Location] = sqlsession.execute(select(Location)\
                                                                            .where(\
                                                                                and_(\
                                                                                    Location.name.ilike('%'+query+'%'),\
                                                                                    #or_(\
                                                                                        Location.editors.contains(user),\
                                                                                        #Location.visibility == Visibilites.public
                                                                                    #)
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)  

                            locations = set(locations).union(set(locations2))

                        if (tag == 'character'):
                            locations:list[Location] = sqlsession.execute(select(Location)\
                                                                            .join(Character, Character.location_id == Location.editable_id)\
                                                                            .where(\
                                                                                and_(\
                                                                                    Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                            #    Character.editors.contains(user),\
                                                                                                Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                                #Location.editors.contains(user),\
                                                                                                Location.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)

                            locations2:list[Location] = sqlsession.execute(select(Location)\
                                                                            .join(Character, Character.location_id == Location.editable_id)\
                                                                            .where(\
                                                                                and_(\
                                                                                    Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                                Character.editors.contains(user)
                                                                                            #    Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                                Location.editors.contains(user)
                                                                                            #    Location.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)     

                            locations = set(locations).union(set(locations2))

                        if (tag == 'user'):
                            locations:list[Location] = sqlsession.execute(select(Location)\
                                                                            .join(User, Location.owner_id == User.id)\
                                                                            .where(\
                                                                                and_(\
                                                                                    User.name.ilike('%'+query+'%'),\
                                                                                    #or_(\
                                                                                    #    Location.editors.contains(user),\
                                                                                        Location.visibility == Visibilites.public
                                                                                    #)
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)

                            locations2:list[Location] = sqlsession.execute(select(Location)\
                                                                            .join(User, Location.owner_id == User.id)\
                                                                            .where(\
                                                                                and_(\
                                                                                    User.name.ilike('%'+query+'%'),\
                                                                                    #or_(\
                                                                                       Location.editors.contains(user),\
                                                                                    #    Location.visibility == Visibilites.public
                                                                                    #)
                                                                                )
                                                                            )
                                                                        ).scalars().fetchmany(100)

                            locations = set(locations).union(locations2)                                            

                    return render_template(route, locations=locations)

                if search_type == 'guild':

                    guilds:list[Guild] = None

                    if query == "":
                        guilds:list[Guild] = sqlsession.execute(select(Guild).where(Guild.visibility == Visibilites.public)).scalars()
                    else:   

                        if not tag:
                            tag = 'guild'
                        if (tag == 'guild'):
                            guilds:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .where(\
                                                                            and_(\
                                                                                Guild.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    #Guild.editors.contains(user),\
                                                                                    Guild.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            guilds2:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .where(\
                                                                            and_(\
                                                                                Guild.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    Guild.editors.contains(user)
                                                                                    #Guild.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)      

                            guilds = set(guilds).union(set(guilds2))                                                                                                      

                        if (tag == 'character'):
                            guilds:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(Character, Character.guild_id == Guild.editable_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                            #    Character.editors.contains(user),\
                                                                                                Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                            #    Guild.editors.contains(user),\
                                                                                                Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            guilds2:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(Character, Character.guild_id == Guild.editable_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                            #or_(\
                                                                                                Character.editors.contains(user)
                                                                                            #    Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                               Guild.editors.contains(user)
                                                                                            #    Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)       

                            guilds = set(guilds).union(set(guilds2))

                        if (tag == 'leader'):
                            guilds:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(Character, Guild.character_id == Character.editable_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                        #    or_(\
                                                                                        #        Character.editors.contains(user),\
                                                                                                Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                            #    Guild.editors.contains(user),\
                                                                                                Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            guilds2:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(Character, Guild.character_id == Character.editable_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                Character.name.ilike('%'+query+'%'),\
                                                                                        and_(\
                                                                                        #    or_(\
                                                                                                Character.editors.contains(user)
                                                                                                #Character.visibility == Visibilites.public
                                                                                            ,#),
                                                                                            #or_(\
                                                                                                Guild.editors.contains(user)
                                                                                            #    Guild.visibility == Visibilites.public
                                                                                            #)                                                                                    
                                                                                        )
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)    

                            guilds = set(guilds).union(set(guilds2))                                                                               

                        if (tag == 'user'):
                            guilds:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(User, User.id == Guild.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    #Guild.editors.contains(user)
                                                                                    Guild.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            guilds2:list[Guild] = sqlsession.execute(select(Guild)\
                                                                        .join(User, User.id == Guild.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    Guild.editors.contains(user)
                                                                                    #Guild.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)    

                        guilds = set(guilds).union(set(guilds2))

                    return render_template(route, guilds=guilds)

                if search_type == "familiar":
                    familiars:list[Familiar] = None

                    if query == "":
                        familiars:list[Familiar] = sqlsession.execute(select(Familiar).where(Familiar.visibility == Visibilites.public)).scalars()
                    else:   

                        if not tag:
                            tag = 'familiar'
                        if (tag == 'familiar'):
                            familiars:list[Familiar] = sqlsession.execute(select(Familiar)\
                                                                        .where(\
                                                                            and_(\
                                                                                Familiar.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    #Familiar.editors.contains(user),\
                                                                                    Familiar.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            familiars2:list[Familiar] = sqlsession.execute(select(Familiar)\
                                                                        .where(\
                                                                            and_(\
                                                                                Familiar.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                    Familiar.editors.contains(user),\
                                                                                    #Familiar.visibility == Visibilites.public
                                                                                #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            familiars = set(familiars).union(set(familiars2))

                        if (tag == 'character'):
                            familiars:set[Familiar] = set()
                            characters:list[Character] = sqlsession.execute(select(Character)\
                                .where(\
                                    and_(\
                                        Character.name.ilike('%'+query+'%') ,\
                                        and_(\
                                            #or_(\
                                            #    Character.editors.contains(user),\
                                                Character.visibility == Visibilites.public
                                            ,#),
                                            #or_(\
                                            #    Familiar.editors.contains(user),\
                                                Familiar.visibility == Visibilites.public
                                            #)                                                                                    
                                        )
                                    )
                                )
                            ).scalars().fetchmany(100)

                            characters2:list[Character] = sqlsession.execute(select(Character)\
                                .where(\
                                    and_(\
                                        Character.name.ilike('%'+query+'%') ,\
                                        and_(\
                                            #or_(\
                                                Character.editors.contains(user)
                                            #    Character.visibility == Visibilites.public
                                            ,#),
                                            #or_(\
                                               Familiar.editors.contains(user)
                                            #   Familiar.visibility == Visibilites.public
                                            #)                                                                                    
                                        )
                                    )
                                )
                            ).scalars().fetchmany(100)

                            characters = set(characters).union(set(characters2))

                            for character in characters:
                                if character.familiars:
                                    for familiar in character.familiars:
                                        familiars.add(familiar)

                        if (tag == 'user'):
                            familiars:list[Familiar] = sqlsession.execute(select(Familiar)\
                                                                        .join(User, User.id == Familiar.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                #Familiar.editors.contains(user),\
                                                                                    Familiar.visibility == Visibilites.public
                                                                            #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            familiars2:list[Familiar] = sqlsession.execute(select(Familiar)\
                                                                        .join(User, User.id == Familiar.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                Familiar.editors.contains(user)
                                                                                #    Familiar.visibility == Visibilites.public
                                                                            #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            familiars = set(familiars).union(set(familiars2))
                            
                    return render_template(route, familiars=familiars)

                if search_type == "item":
                    items:list[Item] = None

                    if query == "":
                        items:list[Item] = sqlsession.execute(select(Item).where(Item.visibility == Visibilites.public)).scalars()
                    else:   

                        if not tag:
                            tag = 'item'
                        if (tag == 'item'):
                            items:list[Item] = sqlsession.execute(select(Item)\
                                                .where(\
                                                    and_(\
                                                        Item.name.ilike('%'+query+'%'),\
                                                        #or_(\
                                                            #Item.editors.contains(user),\
                                                            Item.visibility == Visibilites.public
                                                        #)
                                                    )
                                                )
                                            ).scalars().fetchmany(100)

                            items2:list[Item] = sqlsession.execute(select(Item)\
                                                .where(\
                                                    and_(\
                                                        Item.name.ilike('%'+query+'%'),\
                                                        #or_(\
                                                            Item.editors.contains(user),\
                                                            #Item.visibility == Visibilites.public
                                                        #)
                                                    )
                                                )
                                            ).scalars().fetchmany(100)

                            items = set(items).union(set(items2))

                            items:list[Item] = sqlsession.execute(select(Item)\
                                                                        .join(User, User.id == Item.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                #Familiar.editors.contains(user),\
                                                                                    Item.visibility == Visibilites.public
                                                                            #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            items2:list[Item] = sqlsession.execute(select(Item)\
                                                                        .join(User, User.id == Item.owner_id)\
                                                                        .where(\
                                                                            and_(\
                                                                                User.name.ilike('%'+query+'%'),\
                                                                                #or_(\
                                                                                Item.editors.contains(user)
                                                                                #    Familiar.visibility == Visibilites.public
                                                                            #)
                                                                            )
                                                                        )
                                                                    ).scalars().fetchmany(100)

                            items = set(items).union(set(items2))
                    return render_template(route, items=items)

            if search_type == "user":
                users:list[User] = None

                if query == "":
                    users:list[User] = sqlsession.execute(select(User)).scalars()
                else:   

                    if not tag:
                        tag = 'user'
                    if (tag == 'user'):
                        users:list[User] = sqlsession.execute(select(User)\
                            .where(\
                                User.name.ilike('%'+query+'%'),\
                            )
                        ).scalars().fetchmany(100)
                    if (tag == 'character' or tag == 'location' or tag == 'familiar' or tag == 'item' or tag == ' guild'):
                            users:list[User] = sqlsession.execute(select(User)\
                                .join(Editable, User.id == Editable.owner_id)\
                                .where(\
                                    and_(\
                                        Editable.name.ilike('%'+query+'%'),\
                                        #or_(\
                                            #Editable.editors.contains(user),\
                                            Editable.visibility == Visibilites.public
                                        #)
                                    )
                                )
                            ).scalars().fetchmany(100)

                            users2:list[User] = sqlsession.execute(select(User)\
                                .join(Editable, User.id == Editable.owner_id)\
                                .where(\
                                    and_(\
                                        Editable.name.ilike('%'+query+'%'),\
                                        #or_(\
                                            Editable.editors.contains(user),\
                                            #Editable.visibility == Visibilites.public
                                        #)
                                    )
                                )
                            ).scalars().fetchmany(100)

                            users = set(users).union(set(users2))

                return render_template(route, users=users)
                    
            return render_template(route)

@bp.route('/api/admin_query', methods=['POST'])
@login_required
def admin_query():
    admin_browse:str = 'snippets/admin_browse.html'

    route:str = admin_browse

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            user:User = get_user(session=sqlsession, user_id=g.user.id)

            if user and user.admin_status:
                route = admin_browse

            search_info:dict = request.json
            search_type:str = search_info.get('search_type')
            
            if search_type:
                query:str = search_info.get('query')
                tag:str = search_info.get('tag')

                print(search_type, " tag: ", tag, " query: ", query)

                if not query:
                    query = ''
                
                if search_type == 'editable':

                    editables:list[Editable] = None

                    if not tag:
                        tag = 'editable'                    

                    if (tag == 'editable'):
                        editables:list[Editable] = sqlsession.execute(select(Editable).where(Editable.name.ilike('%'+query+'%'))).scalars().fetchmany(100)
                        users:list[User] = sqlsession.execute(select(User).where(User.name.ilike('%'+query+'%'))).scalars().fetchmany(100)
                        editables = editables + users
                        return render_template(route, editables=editables)

@bp.route('/api/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        admin:bool = is_admin(session=sqlsession, user_id=g.user.id)
        banned_user:User = get_user(session=sqlsession, user_id=user_id)

        if admin:
            banned_user.banned_status=True

            return {'status':'success'}

        return {'status':'failure'}

@bp.route('/api/unban_user/<int:user_id>', methods=['POST'])
@login_required
def unban_user(user_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        admin:bool = is_admin(session=sqlsession, user_id=g.user.id)
        banned_user:User = get_user(session=sqlsession, user_id=user_id)

        if admin:
            banned_user.banned_status=False

            return {'status':'success'}

        return {'status':'failure'}
        