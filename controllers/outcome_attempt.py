from flask import abort, jsonify, request, render_template
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser

from typing import List

from app import db
from app.models import Course, Outcome, User


class OutcomeAttemptsAPI(MethodView):
    def get(self: None, course_id: int, outcome_id: int) -> List[Outcome]:
        """ Get structured data about student statuses in a course 
            based on saved attempts.

        Args:
            course_id (int): [description]
        """
        args = parser.parse({"calc_method": fields.Str()}, location='querystring')

        course = Course.query.filter(Course.canvas_id == course_id).first()
        if course is None:
            abort(404)

        outcome = course.outcomes.filter(Outcome.canvas_id == outcome_id).first()

        # The calculation method is a querystring right now. 
        # See https://stackoverflow.com/questions/3061/calling-a-function-of-a-module-by-using-its-name-a-string
        # for info on calling methods by string names.
        func = getattr(outcome, args['calc_method'])

        scores = [ 
            { "canvas_id": user.canvas_id, "name": user.name, "score": func(user.canvas_id) } for user in course.enrollments.all() if user.usertype_id == 2
        ]
        
        return jsonify(scores)


class UserOutcomeAttemptAPI(MethodView):
    def get(self: None, course_id: int, user_id: int, outcome_id: int) -> object:
        """ Get all attempts on a single outcome for a single user

        Args:
            course_id (int): Canvas course ID
            outcome_id (int): Canvas outcome ID
            user_id (int): Canvas user ID

        Returns:
            obj: Object with attempts sorted by date.
        """
        from app.models import OutcomeAttempt
        from app.schemas import OutcomeAttemptSchema, OutcomeSchema

        course = Course.query.filter(Course.canvas_id == course_id).first()
        user = course.enrollments.filter(User.canvas_id == user_id).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()
        scores = user.assessments.filter(OutcomeAttempt.outcome_canvas_id == outcome_id).all()
        
        # return jsonify({
        #     "user": user.name,
        #     "outcome": OutcomeSchema().dump(outcome),
        #     "scores": OutcomeAttemptSchema(many=True).dump(scores)
        # })

        return render_template(
            'outcome/partials/outcome_results.html', 
            student=user.name,
            outcome=OutcomeSchema().dump(outcome),
            scores=OutcomeAttemptSchema(many=True).dump(scores),
            colspan=len(course.outcomes.all())
            )