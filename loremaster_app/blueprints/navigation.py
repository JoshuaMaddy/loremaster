from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, jsonify
)
from flask import session as fsession
from ..database.init_db import Session
from ..database.table_declarations import *

from sqlalchemy import select
from sqlalchemy.orm import Session as Ses

from .auth import login, login_required

bp = Blueprint('navi', __name__)

@bp.route('/')
def index():
    return render_template('homepage.html')

@bp.route('/user/<int:user_id>')
@login_required
def user_page(user_id:int):
    with Session.begin() as sqlsession:
        sqlsession:Ses

        user:User = sqlsession.execute(select(User).where(User.id == user_id)).scalar()

        if user is None:
            return redirect(url_for('navi.index'))
        else:
            return render_template('navigation/user_page.html', user=user)