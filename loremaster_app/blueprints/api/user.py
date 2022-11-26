from flask import (
    g, request, url_for, jsonify, flash
)
from ...database.init_db import Session
from ...database.table_declarations import *
from ..auth import encrypt
from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

def edit():
    """Edits a location from a POST request with the given form data:
    ImmutableMultiDict([('username', ''), ('first_name', ''), ('last_name', ''), 
    ('password', ''), ('email', ''), ('description', '')])

    Returns:
        Redirect: redirect JSON to the create page so as to flash error.
        Json: Json that directs to the edited item page.
    """
    print(request.form.values)
    with Session.begin() as sqlsession:
        sqlsession:Ses

        # Retrieve user given name of image from form data.
        username:str = request.form.get('username', default=None, type=str)

        first_name:str = request.form.get('first_name', default=None, type=str)

        last_name:str = request.form.get('last_name', default=None, type=str)

        password:str = request.form.get('password', default=None, type=str)

        email:str = request.form.get('email', default=None, type=str)

        description:str = request.form.get('description', default=None, type=str)

        user:User = sqlsession.execute(select(User).where(User.id == g.user.id)).scalar()

        if user:
            user.name = username
            user.description = description

            user.first_name = first_name

            user.last_name = last_name

            user.email = email

            if password:
                user.password = encrypt(password)


            return {'Status':'Success'}
    return {'Status':'Failure'}