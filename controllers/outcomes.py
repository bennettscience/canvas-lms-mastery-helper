from flask import abort, jsonify, request
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser

from typing import List

from app import db
from app.models import Course, Outcome, Manager
from app.schemas import CourseSchema, OutcomeSchema, OutcomeListSchema


class OutcomeListAPI(MethodView):
    def get(self: None) -> List[Outcome]:
        """ Get a list of stored outcomes

        Returns:
            List[Outcome]: List of <Outcome>
        """
        outcomes = Outcome.query.all()
        return jsonify(OutcomeListSchema(many=True, exclude=('alignment',)).dump(outcomes))

    def post(self: None) -> Outcome:
        """ Add a new outcome to the database

        Returns:
            Outcome: <Outcome> instance
        """
        from app.canvas_sync import CanvasSyncService
        self.service = CanvasSyncService()

        required_args = {
            'course_id': fields.Int(), 
            'canvas_id': fields.Int(), 
            'name': fields.Str()
        }
        args = parser.parse(required_args, request)
        outcome = Outcome.query.filter(Outcome.canvas_id == args['canvas_id']).first()
        
        if not outcome:
            outcome = Outcome(name=args['name'], canvas_id=args['canvas_id'])
            db.session.add(outcome)
        
         # All outcomes are attached to a course, so do that before returning.
        course = Course.query.filter(Course.canvas_id == args['course_id']).first()
        outcome_is_imported = course.outcomes.filter(Outcome.canvas_id == outcome.id).scalar()
        
        if outcome_is_imported is None:
            course.outcomes.append(outcome)
            result = jsonify(CourseSchema().dump(outcome))    
            try:
                self.service.get_outcome_attempts(args['course_id'], args['canvas_id'])
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"messages": "Cannot import an outcome which isn't assessed in this course. Add the Outcome to your canvas course and try again."}), 422
        else:
            abort(409)

        return result
            

class OutcomeAPI(MethodView):
    def get(self: None, outcome_id: int) -> Outcome:
        """ Get a single stored outcome

        Args:
            canvas_id (int): Canvas ID for the outcome

        Returns:
            Outcome: <Outcome> instance
        """
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id)
        if not outcome:
            abort(404)
        
        return jsonify(OutcomeSchema().dump(outcome))
