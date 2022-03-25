from flask import abort, jsonify, make_response, request, render_template
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser

from typing import List

from app import db
from app.models import Course, Outcome, User


class OutcomeAttemptsAPI(MethodView):
    def get(self: None, course_canvas_id: int, outcome_canvas_id: int) -> List[Outcome]:
        """ Get structured data about student statuses in a course 
            based on saved attempts.

        Args:
            course_id (int): [description]
        """
        args = parser.parse({"calc_method": fields.Str()}, location='querystring')

        course = Course.query.filter(Course.canvas_id == course_canvas_id).first()
        if course is None:
            abort(404)

        outcome = course.outcomes.filter(Outcome.canvas_id == outcome_canvas_id).first()

        # The calculation method is a querystring right now. 
        # See https://stackoverflow.com/questions/3061/calling-a-function-of-a-module-by-using-its-name-a-string
        # for info on calling methods by string names.
        func = getattr(outcome, args['calc_method'])

        scores = [ 
            { "canvas_id": user.canvas_id, "name": user.name, "score": func(user.canvas_id) } for user in course.enrollments.all() if user.usertype_id == 2
        ]
        
        return jsonify(scores)
    
    def delete(self: None, course_canvas_id: int, outcome_canvas_id: int) -> str:
        """ Delete a single stored outcome in a course

        This does not remove the outcome from the <Outcome> table because other courses
        may rely on the same outcome. This removes the course assocication stored, which
        effectively removes it from the course.

        Student attempts are kept.

        Args:
            outcome_canvas_id (int): outcome Canvas ID

        Returns:
            str: result message
        """
        import json
        course = Course.query.filter(Course.canvas_id == course_canvas_id).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_canvas_id).first()

        if course is None:
            abort(404)
        
        if outcome is None:
            abort(404)
        
        course.outcomes.remove(outcome)
        db.session.commit()

        response = make_response(jsonify({'message': 'ok'}))
        response.headers.set('HX-Trigger', json.dumps({'showToast': "Removed {} from the course.".format(outcome.name)})) 
        return response


class UserOutcomeAttemptAPI(MethodView):
    def get(self: None, course_canvas_id: int, user_canvas_id: int, outcome_canvas_id: int) -> object:
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

        course = Course.query.filter(Course.canvas_id == course_canvas_id).first()
        user = course.enrollments.filter(User.canvas_id == user_canvas_id).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_canvas_id).first()
        
        scores = user.assessments.filter(OutcomeAttempt.outcome_canvas_id == outcome_canvas_id).all()
        scores_only = [score.score for score in scores]

        return render_template(
            'outcome/partials/outcome_results.html', 
            student=user.name,
            outcome=OutcomeSchema().dump(outcome),
            scores=OutcomeAttemptSchema(many=True).dump(scores),
            scores_only=scores_only,
            colspan=len(course.outcomes.all())+1
            )