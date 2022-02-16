from flask import (
    abort, 
    Blueprint, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    session
)
from flask_login import current_user, login_user, logout_user
from webargs.flaskparser import parser

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from app import db
from app.models import User
from app.enums import MasteryCalculation
from app.canvas_auth import CanvasAuthService


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    authorization_url, state = CanvasAuthService().login()
    session['oauth_state'] = state

    return redirect(authorization_url)

@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home_bp.index'))

@auth_bp.route("/callback", methods=["GET"])
def callback():
    from app.models import UserPreferences
    token = CanvasAuthService().get_token()
    session['oauth_token'] = token

    user_id = session['oauth_token']['user']['id']
    user_name = session['oauth_token']['user']['name']

    user = User.query.filter(User.canvas_id == user_id).first()

    if user is None:

        # The UserType ID field is seeded at startup, so setting an
        # integer directly is okay. 
        # TODO: Make this more reliable with enums?
        user = User(
            canvas_id=user_id,
            name=user_name,
            usertype_id=2,
            token=session['oauth_token']['access_token'],
            expiration=session['oauth_token']['expires_at'],
            refresh_token=session['oauth_token']['refresh_token']
        )
        db.session.add(user)

        # The user has to be committed in order to get the ID for the preferences record.
        db.session.commit()

        # Set default values for the score calculation method and score cutoff.
        ups = UserPreferences(user_id=user.id, score_calculation_method=MasteryCalculation(2), mastery_score=3)
        db.session.add(ups)

        db.session.commit()
    else:
        if user.token != session['oauth_token']['access_token']:
            user.token = session['oauth_token']['access_token']
            user.expires = session['oauth_token']['expires_at']
            db.session.commit()
    
    login_user(user, True)
    return redirect('/')