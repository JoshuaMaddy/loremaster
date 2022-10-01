from unicodedata import name
from cryptography.fernet import Fernet

key = b'3G2g0L32hrr1zIiX4Bd369dWdnNzLK-WiSwh-d37LpM='

f = Fernet(key)

def encrypt(string_:str) -> bytes:
    """Encrypts a string to a sequence of bytes based on private key."""
    return f.encrypt(bytes(string_, encoding='utf8'))

def decrypt(bytes_:bytes) -> str:
    """Decrypts a sequence of bytes to a string based on private key."""
    return f.decrypt(bytes_).decode('utf-8')

def check_password_hash(stored:bytes, given:str) -> bool:
    """Determined if a password is correct based on the stored bytes."""
    return decrypt(stored) == given

# Modified from: https://flask.palletsprojects.com/en/2.2.x/tutorial/views/
from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from flask import session as fsession
import functools

from ..database.init_db import Session
from loremaster_app.database.table_declarations import *

from sqlalchemy.orm import Session as Ses
from sqlalchemy import select

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Retrieve information from the form
        username = request.form['username']
        password = request.form['password']
                
        error = None

        # Open connection to the DB
        with Session.begin() as sqlsession:
            sqlsession:Ses

            # Search for User where the name matches the given name
            user:User = sqlsession.execute(select(User).where(User.name == username)).scalar()

            # If no user is found with the given name
            if user is None:
                error = 'Incorrect username.'
            # If user is found but password is incorrect
            elif not check_password_hash(user.password, password):
                error = 'Incorrect password.'

            # If no errors
            if error is None:
                # Reset session and add user_id
                fsession.clear()
                fsession['user_id'] = user.id

                # Redirect to homepage
                return redirect(url_for('index'))

            # If error, set error for next render
            flash(error)

    #If not POST
    return render_template('auth/login.html')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Retrieve information from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        error = None

        # If element missing
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not first_name:
            error = 'First name is required.'
        elif not last_name:
            error = 'Last name is required.'

        if error is None:
            with Session.begin() as sqlsession:
                sqlsession:Ses

                # Test if user is already in DB
                user:User = sqlsession.execute(select(User).where(User.name == username)).scalar()

                if user:
                    error = f"User {username} is already registered."
                else:
                    # Create user object
                    user = User(username=username, password=encrypt(password), first_name=first_name, last_name=last_name, email=email, admin_status=False)

                    # Add user to DB
                    sqlsession.add(user)

                    return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = fsession.get('user_id')

    if user_id is None:
        g.user = None
    else:
        with Session.begin() as sqlsession:
            # Get user from DB
            user = sqlsession.execute(select(User).where(User.id == user_id)).scalar()
            
            # If found, expunge info (detach info) so it can be called out of sqlsession context.
            if user:
                sqlsession.expunge(user)

            g.user = user

@bp.route('/logout')
def logout():
    # Remove user from flask session
    fsession.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if not g.user:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view