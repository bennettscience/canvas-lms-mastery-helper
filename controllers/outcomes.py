from flask import abort, jsonify, request, render_template
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser
from flask_login import current_user

from typing import List

from app import db
from app.models import Course, Outcome, Manager, Assignment
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
        from app.canvas_sync_service import CanvasSyncService
        self.service = CanvasSyncService()

        required_args = {
            'course_id': fields.Int(), 
            'canvas_id': fields.Int(), 
            'name': fields.Str()
        }
        args = parser.parse(required_args, request, location="form")
        outcome = Outcome.query.filter(Outcome.canvas_id == args['canvas_id']).first()
        
        if not outcome:
            outcome = Outcome(name=args['name'], canvas_id=args['canvas_id'])
            db.session.add(outcome)
        
         # All outcomes are attached to a course, so do that before returning.
        course = Course.query.filter(Course.canvas_id == args['course_id']).first()
        outcome_is_imported = course.outcomes.filter(Outcome.canvas_id == outcome.id).scalar()
        
        if outcome_is_imported is None:
            course.outcomes.append(outcome)

            try:
                self.service.get_outcome_attempts(args['course_id'], [args['canvas_id']])
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"messages": "Cannot import an outcome which isn't assessed in this course. Add the Outcome to your canvas course and try again."}), 422
        else:
            abort(409)

        students = course.enrollments.all()

        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user_score = getattr(outcome, current_user.preferences.score_calculation_method.name)(user.canvas_id)
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": user_score
                })
        
        return render_template(
            'outcome/partials/outcome_new_alignment.html',
            course_id=args['course_id'],
            course=CourseSchema().dump(course),
            students=students,
            item=OutcomeSchema().dump(outcome)
        )
            

class OutcomeAPI(MethodView):
    def get(self: None, outcome_id: int) -> Outcome:
        """ Get a single stored outcome

        Args:
            canvas_id (int): Canvas ID for the outcome

        Returns:
            Outcome: <Outcome> instance
        """
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()
        if not outcome:
            abort(404)
        
        return render_template(
            "outcome/partials/outcome_card.html",
            item=outcome,
            course_id=outcome.course[0].canvas_id
        )


class AlignmentAPI(MethodView):
    def get(self: None, outcome_id: int, course_id: int):
        """ Return an Outcome with Assignments available to link

        Args:
            outcome_id (int): Outcome Canvas ID
            course_id (int): Course Canvas ID

        Returns:
            _type_: _description_
        """
        from app.schemas import OutcomeSchema

        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()
        course = Course.query.filter(Course.canvas_id == course_id).first()
        if course is None:
            abort(404)

        if outcome is None:
            abort(404)
        
        assignments = course.assignments

        return render_template(
            'outcome/partials/outcome_alignment_card.html',
            outcome=OutcomeSchema().dump(outcome),
            assignments=assignments,
            course_id=course.canvas_id
        )

    def put(self: None, course_id: int, outcome_id: int):
        """ Align an outcome to an assignment.

        The payload should include a valid Canvas ID for the 
        assignment to align

        Args:
            assignment_id (int): Assignment ID

        Returns:
            Assignment: Updated <Assignment>
        """
        from app.errors import AlignmentExistsException
        from app.schemas import OutcomeSchema

        # This aborts if the argument is missing, so no need for an if block
        args = parser.parse({"assignment_id": fields.Str()}, location='form')

        assignment = Assignment.query.filter(Assignment.canvas_id == args['assignment_id']).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()

        if not assignment:
            abort(404, f"No assignment with ID {args['assignment_id']} found.")
        
        if not outcome:
            abort(404, f"No outcome with ID {outcome_id} found.")

        try:
            assignment.watch(outcome)
        except AlignmentExistsException as e:
            abort(409, e.__str__())
        
        course_id = assignment.course[0].canvas_id

        # Return an Assignment object as an Assignment Card
        return render_template(
            'outcome/partials/outcome_card.html',
            item=OutcomeSchema().dump(outcome),
            course_id=course_id
        )

    def delete(self: None, course_id: int, outcome_id: int) -> Outcome:
        """ Remove an Outcome alignment from an assignment

        Args:
            assignment_id (int): Valid assignment ID

        Returns:
            Assignment: Updated Assignment
        """
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()
        if not outcome:
            abort(404, f"No outcome with ID {outcome_id} found.")

        outcome.alignment.unwatch()

        return render_template(
            'outcome/partials/outcome_card.html',
            item=OutcomeSchema().dump(outcome),
            course_id=course_id)