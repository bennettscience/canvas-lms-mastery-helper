import json
from flask import abort, jsonify, request, render_template
from flask.views import MethodView
from flask_login import current_user
from webargs import fields
from webargs.flaskparser import parser
from typing import List

from app import app, db
from app.errors import DuplicateException
from app.models import Assignment, Manager
from app.schemas import AssignmentSchema, CourseSchema, CreateAssignmentSchema


class AssignmentListAPI(MethodView):

    # TODO: These aren't necessary for every operation. Can loading of these values be put off
    # until they're needed by a function?
    def __init__(self):
        self.calculation_method = current_user.preferences.score_calculation_method.name
        self.mastery_score = current_user.preferences.mastery_score
    
    # only return assignments for the current course.
    # This isn't necessary for anything in the application. Assignments linked to a course are returned 
    # from CourseAssignmentsAPI now. 
    # Syncing assignments from canvas happens through CanvasSyncService().
    app.logger.warning('Endpoint deprecated. Will be removed in a future version. Use "/sync/assignments/<int:course_id>" instead.')
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
        required_args = {
            "name": fields.Str(required=True),
            "canvas_id": fields.Int(required=True),
            "course_id": fields.Int(required=True),
            "points_possible": fields.Float(required=True)
        }
        args = parser.parse(required_args, location="form")
        exists = Assignment.query.filter(Assignment.canvas_id == args['canvas_id']).scalar()

        if not exists:
            assignment = Assignment(name=args['name'], canvas_id=args['canvas_id'], points_possible=args['points_possible'])
            course = Course.query.filter(Course.canvas_id == args['course_id']).first()
            assignment.course.append(course)
            db.session.add(assignment)
            db.session.commit()
        else:
            abort(409, 'Assignment already exists. Please select a different assignment.')
        
        return jsonify({"message": "Import successful"}), 200
    
    def put(self: None, course_id: int) -> List[Assignment]:
        """ Update student scores for all assignments stored in the course

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[Assignment]: List of UserAssignment
        """
        from datetime import datetime
        from app.models import Course, User, UserAssignment
        from app.canvas_sync_service import CanvasSyncService

        service = CanvasSyncService()

        course = Course.query.filter(Course.canvas_id == course_id).first()
        if course is None:
            abort(404)
        
        assignments = course.assignments
        students = course.enrollments.filter(User.usertype_id == 3).all()

        for assignment in assignments:
            if assignment.watching is not None:
                app.logger.info('Assignment {} is aligned to outcome {}'.format(assignment.name, assignment.watching.name))
                for student in students:
                    student_score = getattr(assignment.watching, self.calculation_method)(student.canvas_id)
                    app.logger.info('{} has {} on {}'.format(student.name, student_score, assignment.watching.name))
                    
                    if type(student_score) != str:
                        if student_score >= self.mastery_score:
                            score = assignment.points_possible
                        else:
                            score = 0

                    # Find the current assignment record for the student
                    user_assignment = UserAssignment.query.filter_by(
                        user_id=student.canvas_id, 
                        assignment_id=assignment.canvas_id
                    ).first()

                    if user_assignment is None:
                        student_record = UserAssignment(
                            assignment_id=assignment.canvas_id,
                            user_id=student.canvas_id,
                            score=score,
                            occurred=datetime.now()
                        )
                        db.session.add(student_record)
                    else:
                        user_assignment.score = score
                        user_assignment.occurred = datetime.now()
                        db.session.add(user_assignment)
                    
                    db.session.commit()
        
        service.post_all_assignment_submissions(course)

        return jsonify({'message': 'All student scores updated'})
        # request = service.post_assignment_submission(
        #     course.canvas_id, 
        #     outcome.alignment.canvas_id, 
        #     student.canvas_id, 
        #     1
        # )

       

class AssignmentAPI(MethodView):
    def __init__(self):
        self.calculation_method = current_user.preferences.score_calculation_method.name
        self.mastery_score = current_user.preferences.mastery_score
    
    def get(self: None, assignment_canvas_id: int) -> Assignment:
        """ Get a single assignment

        Args:
            assignment_id (int): Canvas assignment ID

        Returns:
            Assignment: <Assignment> instance
        """
        assignment = Assignment.query.filter(Assignment.canvas_id == assignment_canvas_id).first()
        
        if not assignment:
            abort(404, 'Assignment not found. Check the Assignment ID and try again.')
        
        return AssignmentSchema().dump(assignment)

    def put(self: None, assignment_canvas_id: int) -> Assignment:
        """ Update scores for a single assignment

        Args:
            assignment_id (int): Assignment Canvas ID

        Returns:
            Assignment: Updated Assignment
        """
        from datetime import datetime
        from app.models import User, UserAssignment
        from app.canvas_sync_service import CanvasSyncService

        service = CanvasSyncService()
        assignment = Assignment.query.filter(Assignment.canvas_id == assignment_canvas_id).first()
        if assignment is None:
            abort(404)
        
        students = assignment.course[0].enrollments.filter(User.usertype_id == 3).all()

        # TODO: This is exactly the same as the AssignmentListAPI method above.
        # Inherit from a base class?
        if assignment.watching is not None:
            app.logger.info('Assignment {} is aligned to outcome {}'.format(assignment.name, assignment.watching.name))
            for student in students:

                # Get the student's current score on the Outcome
                student_score = getattr(assignment.watching, self.calculation_method)(student.canvas_id)
                app.logger.info('{} has {} on {}'.format(student.name, student_score, assignment.watching.name))
                
                if type(student_score) != str:
                    if student_score >= self.mastery_score:
                        score = assignment.points_possible
                    else:
                        score = 0

                # Find the current assignment record for the student
                user_assignment = UserAssignment.query.filter_by(
                    user_id=student.canvas_id, 
                    assignment_id=assignment.canvas_id
                ).first()

                if user_assignment is None:
                    student_record = UserAssignment(
                        assignment_id=assignment.canvas_id,
                        user_id=student.canvas_id,
                        score=score,
                        occurred=datetime.now()
                    )
                    db.session.add(student_record)
                else:
                    user_assignment.score = score
                    user_assignment.occurred = datetime.now()
                    db.session.add(user_assignment)
                
                db.session.commit()
        
        # Pass the entire assignment object to the function because it relies on
        # relationships and properties to build the Canvas API object
        service.post_assignment_submission(assignment)
        
        return jsonify({'message': 'Success'})

