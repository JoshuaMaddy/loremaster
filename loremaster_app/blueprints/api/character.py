from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():

    print("create")

    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.character_creation')})

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            character_info:dict = request.json

            if character_info:
                character:dict = character_info.get('character')
                name:str = character.get('name')
                description:str = character_info.get('description')
                traits:list[dict] = character_info.get('traits')
                stats:list[dict] = character_info.get('stats')
                relationships:list[dict] = character_info.get('relationships')
                familiar_ids:list[dict] = character_info.get('familiar_ids')
                editor_ids:list[dict] = character_info.get('editor_ids')
                image_ids:list[int] = character_info.get('image_ids')
                location_id:int = character_info.get('location_id')
                guild_id:int = character_info.get('guild_id')
                vis_int:int = character_info.get('visibility')
                
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user:
                    character:Character = Character(owner=user, name=name)

                    character.description = description

                    if image_ids:
                        character.set_images(sqlsession=sqlsession, image_ids=image_ids)

                    if stats:
                        character.set_stats(stats=stats)

                    if traits:
                        character.set_traits(traits=traits)

                    if relationships:
                        character.set_relationships(sqlsession=sqlsession, user=user, relationships=relationships)

                    if familiar_ids:
                        character.set_familiars(sqlsession=sqlsession, user=user, familiar_ids=familiar_ids)

                    if editor_ids:
                        character.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    if location_id:
                        character.set_location(sqlsession=sqlsession, user=user, location_id=location_id)

                    if guild_id:
                        character.set_guild(sqlsession=sqlsession, user=user, guild_id=guild_id)

                    if vis_int:
                        character.set_visibility(sqlsession=sqlsession, vis_int=vis_int)
                else:
                    flash('User not found in DB.')
                    return redirect

                sqlsession.add(character)
                sqlsession.flush()

                return(jsonify({'url':url_for('navi.character_page', character_id=character.id)}))

            else:
                flash('API received malformed JSON.')
                return redirect
    else:
        flash('API received something that was not JSON.')
        return redirect

def edit():

    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.index')})


    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            character_info:dict = request.json

            if character_info:
                character:dict = character_info.get('character')
                name:str = character.get('name')
                id:int = character.get('id')
                description:str = character_info.get('description')
                traits:list[dict] = character_info.get('traits')
                stats:list[dict] = character_info.get('stats')
                relationships:list[dict] = character_info.get('relationships')
                familiar_ids:list[dict] = character_info.get('familiar_ids')
                editor_ids:list[dict] = character_info.get('editor_ids')
                image_ids:list[int] = character_info.get('image_ids')
                location_id:int = character_info.get('location_id')
                guild_id:int = character_info.get('guild_id')
                vis_int:int = character_info.get('visibility')

                if id:
                    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.character_edit', character_id=id)})
                else:
                    flash('No character ID in form submission.')
                    return redirect

                character:Character = sqlsession.execute(select(Character).where(Character.id == id)).scalar()
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user:
                    if character:
                        if character in user.editor_perms: 
                            character.name = name
                            character.description = description

                            character.stats = []
                            character.traits = []
                            character.relationships = []
                            character.familiars = []
                            character.images = []

                            character.editors = []
                            character.editors.append(user)

                            if image_ids:
                                character.set_images(sqlsession=sqlsession, image_ids=image_ids)

                            if stats:
                                character.set_stats(stats=stats)

                            if traits:
                                character.set_traits(traits=traits)

                            if relationships:
                                character.set_relationships(sqlsession=sqlsession, user=user, relationships=relationships)

                            if familiar_ids:
                                character.set_familiars(sqlsession=sqlsession, user=user, familiar_ids=familiar_ids)

                            if editor_ids:
                                character.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                            if location_id:
                                character.set_location(sqlsession=sqlsession, user=user, location_id=location_id)

                            if guild_id:
                                character.set_guild(sqlsession=sqlsession, user=user, guild_id=guild_id)

                            if vis_int:
                                character.set_visibility(sqlsession=sqlsession, vis_int=vis_int)

                            return(jsonify({'url':url_for('navi.character_page', character_id=character.id)}))

                        else:
                            flash('Character not in User edit permissions.')
                            return redirect
                    else:
                        flash('Character not found in DB.')
                        return redirect
                else:
                    flash('User not found in DB.')
                    return redirect
    else:
        flash('API received something that was not JSON.')
        return redirect