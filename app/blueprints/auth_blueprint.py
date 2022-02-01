from flask import abort, Blueprint, jsonify, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user
from webargs.flaskparser import parser

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from app.models import User
from app.schemas import UserLoginSchema

# @auth_bp.route("/getsession", methods=["GET"])
# def check_session():
#     if current_user.is_authenticated:
#         user = User.query.get(current_user.id)
#         print(f'{user} exists')
#         print('Redirecting to home')
#         return redirect(url_for('home_bp.index'))
#         # return jsonify({"login": True, "user": UserSchema().dump(user)})
#     return render_template('auth/login.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Fake a login for the time being
    login_user(User.query.get(2))
    return render_template('home/partials/user_ready.html')
    # return redirect(url_for('home_bp.index'))
    # args = parser.parse(UserLoginSchema(), location='json')
    # user = User.query.get(args['id'])
    # if not user:
    #     # TODO: Add new user to database and login
    #     abort(404)
    # else:
    #     login_user(User.query.get(1), True)
    #     print(f'{current_user} is logged in')
    #     print('Rendering the home template from /auth/login')
    #     return render_template('home/index.html')

@auth_bp.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for('home_bp.index'))