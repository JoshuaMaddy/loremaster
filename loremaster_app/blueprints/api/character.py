from flask import (
    g, request, url_for, jsonify
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():
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


                sqlsession.add(character)
                sqlsession.flush()

                return(jsonify({'url':url_for('navi.character_page', character_id=character.editable_id)}))
            
    return('probably bad')

def edit():
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

                character:Character = sqlsession.execute(select(Character).where(Character.editable_id == id)).scalar()
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user and character and character in user.editor_perms: 
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

            return('probably good')
            
    return('probably bad')