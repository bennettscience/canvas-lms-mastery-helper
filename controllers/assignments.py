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
        
        return render_template(
            'shared/partials/sidebar.html',
            position="right",
            partial='assignment/partials/assignment_card.html',
            items=AssignmentSchema(many=True).dump(assignments),
            )

    def post(self: None) -> Assignment:
        """ Add an assignment to the database

        Assignments _cannot_ be orphans! They must be aligned to the current course when aligned
        for proper tracking.

        Returns:
            Assignment: <Assignment> instance
        """
        from app.models import Course
        args = parser.parse(CreateAssignmentSchema(), location="form")
        exists = Assignment.query.filter(Assignment.canvas_id == args['canvas_id']).scalar()

        if not exists:
            assignment = Assignment(name=args['name'], canvas_id=args['canvas_id'])
            course = Course.query.filter(Course.canvas_id == args['course_id']).first()
            assignment.course.append(course)
            db.session.add(assignment)
            db.session.commit()

            result = jsonify(AssignmentSchema().dump(assignment))
        else:
            abort(409, 'Assignment already exists. Please select a different assignment.')
        
        # Return a sidebar of all of the assignments.
        return jsonify({"message": "Import successful"}), 200
        # return render_template(
        #     'shared/partials/sidebar.html', 
        #     position="right",
        #     method="get",
        #     endpoint="/courses/{}/assignments".format(args['course_id']),
        #     )


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

