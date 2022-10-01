from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, jsonify
)
from flask import session as fsession

bp = Blueprint('navi', __name__)

@bp.route('/')
def index():
    return render_template('homepage.html')
