from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import current_user, logout_user

from app.canvas_auth import CanvasAuthService

home_bp = Blueprint('home_bp', __name__)

@home_bp.get('/')
def index():
    if not current_user.is_anonymous and session['_fresh']:
        return render_template('home/index.html')
    else:
        session.clear()
        logout_user()
        return render_template('auth/login.html')


@home_bp.get('/preferences')
def user_preferences():
    from app.schemas import UserSchema
    return render_template(
        'preferences/index.html',
        user=UserSchema().dump(current_user)
    )