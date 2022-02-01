from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

home_bp = Blueprint('home_bp', __name__, template_folder='templates')

@home_bp.get('/')
def index():
    if(current_user.is_anonymous):
        return render_template('auth/login.html')
    return render_template('home/index.html')