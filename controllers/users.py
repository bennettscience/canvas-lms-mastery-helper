from flask import abort, jsonify, request
from flask.views import MethodView
from webargs.flaskparser import parser

from typing import List

from app import db
from app.models import User, Manager, Course
from app.schemas import UserSchema, CourseSchema


class UserListAPI(MethodView):
    def get(self: None) -> List[User]:
        users = User.query.all()
        return jsonify(UserSchema(many=True).dump(users))


class UserAPI(MethodView):
    def get(self: None, user_id: int) -> User:
        user = User.query.get(user_id)
        if not user:
            abort(404)
        
        return UserSchema().dump(user)


class UserCourseAPI(MethodView):
    def get(self: None, user_id: int) -> List[Course]:
        user = User.query.get(user_id)
        if user is None:
            abort (404)
        
        return jsonify(CourseSchema(many=True, exclude=["assignments"]).dump(user.enrollments.all()))