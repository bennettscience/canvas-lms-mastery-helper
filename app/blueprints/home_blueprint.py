from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import current_user, logout_user

home_bp = Blueprint('home_bp', __name__)

@home_bp.get('/')
def index():
    print(current_user)
    if not current_user.is_anonymous:
        return render_template('home/index.html', current_user=current_user)
    else:
        session.clear()
        logout_user()
        return render_template('auth/login.html', current_user=current_user)


@home_bp.get('/preferences')
def user_preferences():
    from app.schemas import UserSchema, CourseSchema

    courses = current_user.enrollments.all()

    return render_template(
        'preferences/index.html',
        courses=CourseSchema(many=True).dump(courses),
        user=UserSchema().dump(current_user)
    )