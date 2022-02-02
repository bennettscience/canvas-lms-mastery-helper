from flask import abort, jsonify, request, render_template
from flask.views import MethodView
from webargs import fields
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
        
        return render_template(
            'preferences/partials/user_prefs.html',
            user=user
        )


class UserPrefsAPI(MethodView):
    def get(self: None, user_id: int) -> User:
        from app.enums import MasteryCalculation
        user = User.query.get(user_id)
        if user is None:
            abort(404)
        
        options = MasteryCalculation._member_names_
        print(options)
        return render_template(
            'preferences/partials/preference_update_form.html',
            user=user,
            opts=options
        )

    def put(self: None, user_id: int) -> User:
        user = User.query.get(user_id)
        if user is None:
            abort(404)
        
        args = parser.parse({"mastery_score": fields.Int(), "score_calculation_method": fields.Str()}, location='form')
        print(args)

        user.preferences.update(args)

        return render_template(
            'preferences/partials/user_prefs.html',
            user=user
        )


class UserCourseAPI(MethodView):
    def get(self: None, user_id: int) -> List[Course]:
        user = User.query.get(user_id)
        if user is None:
            abort (404)
        
        return jsonify(CourseSchema(many=True, exclude=["assignments"]).dump(user.enrollments.all()))