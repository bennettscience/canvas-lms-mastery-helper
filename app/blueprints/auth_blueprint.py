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
from app.canvas_auth_service import CanvasAuthService


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    authorization_url, state = CanvasAuthService().login()
    session['oauth_state'] = state

    return redirect(authorization_url)

@auth_bp.route("/logout", methods=["GET"])
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home_bp.index'))

@auth_bp.route("/callback", methods=["GET"])
def callback():
    import os
    from canvasapi import Canvas
    from app.models import UserPreferences
    token = CanvasAuthService().get_token()
    session['oauth_token'] = token

    user_id = session['oauth_token']['user']['id']
    user_name = session['oauth_token']['user']['name']

    split_name = user_name.split(' ')

    user = User.query.filter(User.canvas_id == user_id).first()

    if user is None:

        # handle users with more than two names
        if len(split_name) > 2:
            split_name[:-1] = [' '.join(user_name[:-1])]
        
        # The name returned by the OAuth login is normal. Reverse for readability
        split_name.reverse()
       
        # The UserType ID field is seeded at startup, so setting an
        # integer directly is okay. 
        # TODO: Make this more reliable with enums?
        user = User(
            canvas_id=user_id,
            name=', '.join(split_name),
            usertype_id=3,
            token=session['oauth_token']['access_token'],
            expiration=session['oauth_token']['expires_at'],
            refresh_token=session['oauth_token']['refresh_token']
        )
        db.session.add(user)

        # The user has to be committed in order to get the ID for the preferences record.
        db.session.commit()

        # To store some information about the user, we have to fetch that user using the master API key.
        # Create a temporary service to run this section only.
        tmp_canvas_service = Canvas(os.environ.get('CANVAS_URI'), os.environ.get('CANVAS_KEY'))
        
        # Check the user's permissions and match. If they have a single TeacherEnrollment, then
        # elevate them to Teacher statuses.
        canvas_user_account = tmp_canvas_service.get_user(user_id)

        # Since we have the user, store the sortable name instead
        user.name = canvas_user_account.sortable_name

        courses = canvas_user_account.get_courses(enrollment_state='active')

        # Enrollment types are set by course, so create a set to get _unique_ enrollment types
        enrollment_types = set()

        for course in courses:
            enrollment_types.update([enrollment['type'] for enrollment in course.enrollments])
        
        # The enrollment types are stored by string. If 'teachers exists in even one course, they get the
        # teacher permissions here. Set a Mastery Calculation default.
        if 'teacher' in enrollment_types:
            user.usertype_id = 2
            ups = UserPreferences(user_id=user.id, score_calculation_method=MasteryCalculation(2), mastery_score=3)
        else:
            # Students get a None mastery calculation because we want it to follow the teacher's preferences.
            ups = UserPreferences(user_id=user.id, score_calculation_method=MasteryCalculation(6), mastery_score=None)

        # Set default values for the score calculation method and score cutoff.
        db.session.add(ups)
        db.session.commit()
    else:
        # The user already exists, so jusy update their access token and expiration.
        if user.token != session['oauth_token']['access_token']:
            user.token = session['oauth_token']['access_token']
            user.expires = session['oauth_token']['expires_at']
            db.session.commit()
    
    login_user(user)
    return redirect('/')
