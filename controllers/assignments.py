import json
from flask import abort, jsonify, request, render_template
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import parser
from typing import List

from app import db
from app.errors import AlignmentExistsException
from app.models import Assignment, Manager
from app.schemas import AssignmentSchema, CourseSchema, CreateAssignmentSchema


class AssignmentListAPI(MethodView):
    # only return assignments for the current course.
    def get(self: None, course_id: int) -> List[Assignment]:
        """ Get stored assignments

        Returns:
            List[Assignment]: <Assignment> objects
        """
        assignments = Assignment.query.filter(Assignment.course[0].canvas_id == course_id).all()
        
        print('rendering template?')
        return render_template(
            'shared/partials/sidebar.html',
            position="right",
            partial='assignment/partials/assignment_card.html',
            items=AssignmentSchema(many=True).dump(assignments)
            )

    def post(self: None) -> Assignment:
        """ Add an assignment to the database

        Assignments _cannot_ be orphans! They must be aligned to the current course when aligned
        for proper tracking.

        Returns:
            Assignment: <Assignment> instance
        """
        from app.models import Course
        args = parser.parse(CreateAssignmentSchema(), location="json")
        exists = Assignment.query.filter(Assignment.canvas_id == args['canvas_id']).scalar()
        
        if not exists:
            assignment = Assignment(name=args['name'], canvas_id=args['canvas_id'])
            assignment.course.append(Course.query.get(args['course_id']))
            db.session.add(assignment)
            db.session.commit()

            result = jsonify(AssignmentSchema().dump(assignment))
        else:
            abort(409, 'Assignment already exists. Please select a different assignment.')
        
        # Return a sidebar of all of the assignments.
        return render_template(
            'shared/partials/sidebar.html', 
            position="right",
            method="get",
            endpoint="/courses/{}/assignments".format(args['course_id']),
            )


class AssignmentAPI(MethodView):
    def get(self: None, assignment_id: int) -> Assignment:
        """ Get a single assignment

        Args:
            assignment_id (int): Canvas assignment ID

        Returns:
            Assignment: <Assignment> instance
        """
        args = parser.parse(AssignmentSchema(), location="querystring")

        if args and args['use_canvas_id']:
            assignment = Assignment.query.filter(Assignment.canvas_id == assignment_id).first()
        else:
            assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
        
        if not assignment:
            abort(404)
        
        return AssignmentSchema().dump(assignment)

    def put(self: None, assignment_id: int) -> Assignment:
        pass

class AlignmentAPI(MethodView):
    def put(self: None, assignment_id: int) -> Assignment:
        """ Align an outcome to an assignment.

        The payload should include a valid Canvas ID for the 
        Outcome to align:

        payload = { 
            outcome_canvas_id: <int>
        }

        Args:
            assignment_id (int): Assignment ID

        Returns:
            Assignment: Updated <Assignment>
        """
        from app.models import Outcome
        from app.schemas import OutcomeSchema

        # This aborts if the argument is missing, so no need for an if block
        args = parser.parse({"outcome_canvas_id": fields.Int()})

        assignment = Assignment.query.filter(Assignment.canvas_id == assignment_id).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == args['outcome_canvas_id']).first()

        if not assignment:
            abort(404, f"No assignment with ID {assignment_id} found.")
        
        if not outcome:
            abort(404, f"No outcome with ID {args['outcome_canvas_id']} found.")

        try:
            assignment.watch(outcome)
        except AlignmentExistsException as e:
            abort(409, e.__str__())
        
        course_id = assignment.course[0].canvas_id

        # Return an Assignment object as an Assignment Card
        return render_template(
            'outcome/partials/outcome_card.html',
            outcome=OutcomeSchema().dump(outcome),
            course_id=course_id
        )

    def delete(self: None, assignment_id: int) -> Assignment:
        """ Remove an Outcome alignment from an assignment

        Args:
            assignment_id (int): Valid assignment ID

        Returns:
            Assignment: Updated Assignment
        """
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            abort(404, f"Not assignment with ID {assignment_id} found.")

        assignment.unwatch()

        return jsonify(AssignmentSchema().dump(assignment))