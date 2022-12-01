from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():

    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.familiar_creation')})

    if request.is_json:
        with Session.begin() as sqlsession:
            sqlsession:Ses

            familiar_info:dict = request.json

            if familiar_info:
                familiar:dict = familiar_info.get('familiar')
                name:str = familiar.get('name')
                owner_id:int = familiar_info.get("owner_id")
                description:str = familiar_info.get('description')
                traits:list[dict] = familiar_info.get('traits')
                stats:list[dict] = familiar_info.get('stats')
                relationships:list[dict] = familiar_info.get('relationships')
                location_id:int = familiar_info.get('location_id')
                editor_ids:list[dict] = familiar_info.get('editor_ids')
                image_ids:list[int] = familiar_info.get('image_ids')
                vis_int:int = familiar_info.get('visibility')
                
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user:
                    familiar:Familiar = Familiar(owner=user, name=name)

                    familiar.description = description

                    if image_ids:
                        familiar.set_images(sqlsession=sqlsession, image_ids=image_ids)

                    if location_id != None:
                        familiar.set_location(sqlsession=sqlsession, location_id=location_id)

                    if stats:
                        familiar.set_stats(stats=stats)

                    if traits:
                        familiar.set_traits(traits=traits)

                    if relationships:
                        familiar.set_relationships(sqlsession=sqlsession, user=user, relationships=relationships)

                    if owner_id:
                        familiar.set_owner(sqlsession=sqlsession, user=user, owner_id=owner_id)

                    if editor_ids:
                        familiar.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    if vis_int:
                                familiar.set_visibility(sqlsession=sqlsession, vis_int=vis_int)
                else:
                    flash('User not found in DB.')
                    return redirect

                sqlsession.add(familiar)
                sqlsession.flush()

                return(jsonify({'url':url_for('navi.familiar_page', familiar_id=familiar.id)}))

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

            familiar_info:dict = request.json

            if familiar_info:
                familiar:dict = familiar_info.get('familiar')
                name:str = familiar.get('name')
                id:int = familiar.get('id')
                owner:int = familiar.get('character_owner_id')
                description:str = familiar_info.get('description')
                traits:list[dict] = familiar_info.get('traits')
                stats:list[dict] = familiar_info.get('stats')
                relationships:list[dict] = familiar_info.get('relationships')
                location_id:int = familiar_info.get('location_id')
                editor_ids:list[dict] = familiar_info.get('editor_ids')
                image_ids:list[int] = familiar_info.get('image_ids')
                vis_int:int = familiar_info.get('visibility')

                if id:
                    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.familiar_edit', familiar_id=id)})
                else:
                    flash('No familiar ID in form submission.')
                    return redirect

                familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.id == id)).scalar()
                user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

                if user:
                    if familiar:
                        if familiar in user.editor_perms: 
                            familiar.name = name
                            familiar.description = description
                            familiar.owner = owner

                            familiar.stats = []
                            familiar.traits = []
                            familiar.relationships = []
                            familiar.familiars = []
                            familiar.images = []

                            familiar.editors = []
                            familiar.editors.append(user)

                            if image_ids:
                                familiar.set_images(sqlsession=sqlsession, image_ids=image_ids)

                            if location_id != None:
                                familiar.set_location(sqlsession=sqlsession, location_id=location_id)

                            if stats:
                                familiar.set_stats(stats=stats)

                            if traits:
                                familiar.set_traits(traits=traits)

                            if relationships:
                                familiar.set_relationships(sqlsession=sqlsession, user=user, relationships=relationships)

                            if owner:
                                familiar.set_owner(sqlsession=sqlsession, user=user, owner=owner)

                            if editor_ids:
                                familiar.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                            if vis_int:
                                familiar.set_visibility(sqlsession=sqlsession, vis_int=vis_int)

                            return(jsonify({'url':url_for('navi.familiar_page', familiar_id=familiar.id)}))

                        else:
                            flash('Familiar not in User edit permissions.')
                            return redirect
                    else:
                        flash('Familiar not found in DB.')
                        return redirect
                else:
                    flash('User not found in DB.')
                    return redirect
    else:
        flash('API received something that was not JSON.')
        return redirect