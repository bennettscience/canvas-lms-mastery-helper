from flask import Blueprint, abort, jsonify

users_bp = Blueprint('users', __name__)
from app.controllers.users import (
    UserListAPI,
    UserAPI,
    UserPrefsAPI,
    UserCourseAPI
)

users_view = UserListAPI.as_view("users_view")
user_view = UserAPI.as_view("user_view")
user_course_view = UserCourseAPI.as_view("user_course_view")
user_edit_view = UserPrefsAPI.as_view("user_edit_view")

users_bp.add_url_rule("/users", view_func=users_view, methods=["GET"])
users_bp.add_url_rule("/users/<user_canvas_id>", view_func=user_view, methods=['GET'])
users_bp.add_url_rule("/users/<user_canvas_id>/courses", view_func=user_course_view, methods=['GET'])
users_bp.add_url_rule("/users/<int:user_canvas_id>/edit", view_func=user_edit_view, methods=["GET", "PUT"])