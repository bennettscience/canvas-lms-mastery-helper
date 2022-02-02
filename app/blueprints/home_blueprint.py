from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

home_bp = Blueprint('home_bp', __name__)

@home_bp.get('/')
def index():
    if(current_user.is_anonymous):
        return render_template('auth/login.html')
    return render_template('home/index.html')

@home_bp.get('/preferences')
def user_preferences():
    from app.schemas import UserSchema
    return render_template(
        'preferences/index.html',
        user=UserSchema().dump(current_user)
    )