from flask import abort, Blueprint, jsonify
from flask_login import current_user, login_user, logout_user
from webargs.flaskparser import parser

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from app.models import User
from app.schemas import UserSchema, UserLoginSchema

@auth_bp.route("/getsession", methods=["GET"])
def check_session():
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        return jsonify({"login": True, "user": UserSchema().dump(user)})
    return jsonify({"login": False})

@auth_bp.route("/login", methods=["POST"])
def login():
    args = parser.parse(UserLoginSchema(), location='json')
    print(args)
    user = User.query.get(args['id'])
    if not user:
        abort(404)
    else:
        login_user(user, True)
        return jsonify({"login": True, "user": UserSchema().dump(user)})

@auth_bp.route("/logout")
def logout():
    logout_user()
    return jsonify({"login": False})