from flask import abort, jsonify, request, render_template, make_response
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser
from flask_login import current_user

from typing import List

from app import app, db
from app.errors import DuplicateException
from app.models import Course, Outcome, Manager, Assignment
from app.schemas import CourseSchema, OutcomeSchema, OutcomeListSchema


class OutcomeListAPI(MethodView):
    def get(self: None) -> List[Outcome]:
        """ Get a list of stored outcomes

        Returns:
            List[Outcome]: List of <Outcome>
        """
        app.logger.warning('Endpoint deprecated. Use "/courses/<int:course_id>/outcomes" insetead.')
        outcomes = Outcome.query.all()
        return jsonify(OutcomeListSchema(many=True, exclude=('alignment',)).dump(outcomes))

    def post(self: None) -> Outcome:
        """ Add a new outcome to the database

        Returns:
            Outcome: <Outcome> instance
        """
        import json
        from app.models import User
        from app.canvas_sync_service import CanvasSyncService
        self.service = CanvasSyncService()

        required_args = {
            'outcome_id': fields.Int(), 
            'course_id': fields.Int(), 
            'name': fields.Str()
        }
        args = parser.parse(required_args, location="form")
        target_outcome = Outcome.query.filter(Outcome.canvas_id == args['outcome_id']).first()
        
        if not target_outcome:
            target_outcome = Outcome(name=args['name'], canvas_id=args['outcome_id'])
            db.session.add(target_outcome)
        
         # All outcomes are attached to a course, so do that before returning.
        course = Course.query.filter(Course.canvas_id == args['course_id']).first()
        outcome_is_imported = course.outcomes.filter(Outcome.canvas_id == target_outcome.id).scalar()
        
        if outcome_is_imported is None:
            course.outcomes.append(target_outcome)

            try:
                self.service.get_outcome_attempts(args['course_id'], [args['outcome_id']])
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"messages": e}), 422
        else:
            abort(409)

        students = course.enrollments.filter(User.usertype_id == 3).all()

        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user_score = getattr(outcome, current_user.preferences.score_calculation_method.name)(user.canvas_id)
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": user_score
                })
        
        has_alignment = any(o.alignment for o in course.outcomes.all())

        response = make_response(render_template(
            'outcome/partials/outcome_new_alignment_oob.html',
            course_id=args['course_id'],
            course=CourseSchema().dump(course),
            students=students,
            item=OutcomeSchema().dump(target_outcome),
            has_alignment=has_alignment
        ))
        response.headers.set('HX-Trigger', json.dumps({'showToast': "Imported {} to the course.".format(target_outcome.name)}))

        
        return response
            

class OutcomeAPI(MethodView):
    def get(self: None, outcome_canvas_id: int) -> Outcome:
        """ Get a single stored outcome

        Args:
            canvas_id (int): Canvas ID for the outcome

        Returns:
            Outcome: <Outcome> instance
        """
        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_canvas_id).first()

        if not outcome:
            abort(404, 'Outcome not found. Check the outcome ID and try again.')
        
        return render_template(
            "outcome/partials/outcome_card.html",
            item=outcome,
            course_id=outcome.course[0].canvas_id
        )


class AlignmentAPI(MethodView):
    def get(self: None, outcome_canvas_id: int, course_canvas_id: int):
        """ Return an Outcome card with Assignments available to link

        Args:
            outcome_id (int): Outcome Canvas ID
            course_id (int): Course Canvas ID

        Returns:
            _type_: _description_
        """
        from app.schemas import OutcomeSchema

        outcome = Outcome.query.filter(Outcome.canvas_id == outcome_canvas_id).first()
        course = Course.query.filter(Course.canvas_id == course_canvas_id).first()
        if course is None:
            app.logger.warning('Did you use the course Canvas ID?')
            abort(404)

        if outcome is None:
            app.logger.warning('Did you use the outcome Canvas ID?')
            abort(404)
        
        assignments = course.assignments

        return render_template(
            'outcome/partials/outcome_alignment_form.html',
            outcome=OutcomeSchema().dump(outcome),
            assignments=assignments,
            course_id=course.canvas_id
        )

    def put(self: None, course_canvas_id: int, outcome_canvas_id: int):
        """ Align an outcome to an assignment.

        The payload should include a valid Canvas ID for the 
        assignment to align

        Args:
            assignment_canvas_id (int): Assignment ID

        Returns:
            Assignment: Updated <Assignment>
        """
        from app.models import User
        from app.schemas import OutcomeSchema

        args = parser.parse({"assignment_canvas_id": fields.Int()}, location='form')

        assignment = Assignment.query.filter(Assignment.canvas_id == args['assignment_canvas_id']).first()
        target_outcome = Outcome.query.filter_by(canvas_id=outcome_canvas_id).first()

        if not assignment:
            abort(404, f"No assignment with ID {args['assignment_canvas_id']} found.")
        
        if not target_outcome:
            abort(404, f"No outcome with ID {outcome_canvas_id} found.")

        course = target_outcome.course[0]
        students = course.enrollments.filter(User.usertype_id == 3).all()

        try:
            assignment.watch(target_outcome)
            # TODO: move into it's own util function
            for user in students:
                user.scores = []
                for outcome in course.outcomes.all():
                    user_score = getattr(outcome, current_user.preferences.score_calculation_method.name)(user.canvas_id)
                    user.scores.append({
                        "outcome_canvas_id": outcome.canvas_id,
                        "score": user_score
                    })
        except DuplicateException as e:
            abort(409, e.__str__())

        has_alignment = any(o.alignment for o in course.outcomes.all())    

        # Return an Assignment object as an Assignment Card
        return render_template(
            'outcome/partials/alignment_change_oob.html',
            course_id=course_canvas_id,
            course=CourseSchema().dump(course),
            students=students,
            items=OutcomeSchema(many=True).dump(course.outcomes.all()),
            has_alignment=has_alignment
        )

    def delete(self: None, course_canvas_id: int, outcome_canvas_id: int) -> Outcome:
        """ Remove an Outcome alignment from an assignment

        Args:
            assignment_id (int): Valid assignment ID

        Returns:
            Assignment: Updated Assignment
        """
        from app.models import User
        target_outcome = Outcome.query.filter(Outcome.canvas_id == outcome_canvas_id).first()
        if not target_outcome:
            abort(404, f"No outcome with ID {outcome_canvas_id} found.")

        target_outcome.alignment.unwatch()
        
        course = target_outcome.course[0]
        students = course.enrollments.filter(User.usertype_id == 3).all()
        
        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user_score = getattr(outcome, current_user.preferences.score_calculation_method.name)(user.canvas_id)
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": user_score
                })
        
        has_alignment = any(o.alignment for o in course.outcomes.all())

        return render_template(
            'outcome/partials/alignment_change_oob.html',
            course_id=course_canvas_id,
            course=CourseSchema().dump(course),
            students=students,
            items=OutcomeSchema(many=True).dump(course.outcomes.all()),
            has_alignment=has_alignment
        )