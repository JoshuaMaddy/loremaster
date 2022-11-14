from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def create():
    print("creating guild")

    """Creates a guild from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('guild_id', ''), ('parent_guild', ''), ('parent_guild_id', ''), 
        ('single_guild', ''), ('single_guild_id', ''), ('single_editor', ''), ('editor_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the newly created guild page.
    """

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.guild_create')})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            # Retrieve user given name of image from form data.
            name:str = request.form.get('name', default=None, type=str)

            if not name:
                flash('No name for guild.')
                return redirect

            description:str = request.form.get('description', default=None, type=str)

            guild_leader_id:int = request.form.get('guild_leader_id', default=None, type=int)
            member_ids:int = request.form.getlist('guild_member_id', type=int)

            editor_ids:list[int] = request.form.getlist('editor_id', type=int)

            image_ids:list[int] = request.form.getlist('image_id', type=int)

            guild:Guild = Guild(owner=user, name=name)

            guild.description = description

            if guild_leader_id:
                guild.set_leader(sqlsession=sqlsession, user=user, leader_id=guild_leader_id)
            
            if member_ids:
                guild.set_members(sqlsession=sqlsession, member_ids=member_ids)
            
            if image_ids:
                guild.set_images(sqlsession=sqlsession, image_ids=image_ids)
            
            if editor_ids:
                guild.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

            sqlsession.add(guild)
            sqlsession.flush()

            # Return the url as a JSON object, directs to page for newly created image.
            return(jsonify({'url':url_for('navi.guild_page', guild_id=guild.id)}))
        else:
            flash('User not found in DB.')
            return redirect

def edit():
    """Edits a guild from a POST request with the given form data:
    ImmutableMultiDict([('name', ''), ('guild_id', ''), ('parent_guild', ''), ('parent_guild_id', ''), 
        ('single_guild', ''), ('single_guild_id', ''), ('single_editor', ''), ('editor_id', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the edited guild page.
    """

    id:int = request.form.get('guild_id', default=None, type=int)

    # Redirect JSON for flashing errors, will be used in fetch's response section
    redirect:str = jsonify({'ok': False, 'status':405, 'url':url_for('navi.guild_edit', guild_id = id)})

    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Retrieve user given name of image from form data.
        name:str = request.form.get('name', default=None, type=str)

        if not name:
            flash('No name for guild.')
            return redirect

        description:str = request.form.get('description', default=None, type=str)

        guild_leader_id:int = request.form.get('guild_leader_id', default=None, type=int)
        member_ids:int = request.form.getlist('guild_member_id', type=int)

        editor_ids:list[int] = request.form.getlist('editor_id', type=int)

        image_ids:list[int] = request.form.getlist('image_id', type=int)


        guild:Guild = sqlsession.execute(select(Guild).where(Guild.id == id)).scalar()
        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            if guild:
                if guild in user.editor_perms: 
                    guild.name = name
                    guild.description = description

                    guild.parent = None
                    guild.children = []
                    guild.images = []

                    guild.editors = []
                    guild.editors.append(user)

                    if guild_leader_id:
                        guild.set_leader(sqlsession=sqlsession, user=user, leader_id=guild_leader_id)
                    
                    if member_ids:
                        guild.set_members(sqlsession=sqlsession, member_ids=member_ids)
                    
                    if image_ids:
                        guild.set_images(sqlsession=sqlsession, image_ids=image_ids)
                    
                    if editor_ids:
                        guild.set_editors(sqlsession=sqlsession, editor_ids=editor_ids)

                    return(jsonify({'url':url_for('navi.guild_page', guild_id=guild.id)}))

                else:
                    flash('Location not in editor permissions.')
                    return redirect
            else:
                flash('Location not found in DB.')
                return redirect
        else:
            flash('User not found in DB.')
            return redirect