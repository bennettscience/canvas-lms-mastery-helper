from flask import abort, jsonify, request, render_template
from flask_login import current_user
from flask.views import MethodView
from typing import List
from webargs import fields
from webargs.flaskparser import parser

from app import db
from app.models import Assignment, Course, Manager, Outcome
from app.schemas import CourseSchema, OutcomeListSchema


class CourseListAPI(MethodView):
    def get(self: None) -> List[Course]:
        """ Get stored courses

        Returns:
            List[Course]: List of <Course>
        """
        courses = current_user.enrollments.all()

        return render_template(
            'shared/partials/sidebar.html',
            position='left',
            partial='course/partials/course_card.html',
            items=CourseSchema(many=True).dump(courses)
        )

    def post(self: None) -> Course:
        """ Add a course record to the database

        Returns:
            Course: Instance of <Course>
        """
        from app.canvas_sync_service import CanvasSyncService

        args = parser.parse({"canvas_id": fields.Int(), "name": fields.Str()}, location="form")
        exists = Course.query.filter(Course.canvas_id == args['canvas_id']).scalar()
        
        if not exists:
            course = Manager().create(Course, args)

            # Add the requester to the course by default.
            current_user.enroll(course)

            service = CanvasSyncService()

            # Store all students as new users and enroll in the course.
            service.get_enrollments(course.canvas_id)

        else:
            abort(409, "{} already exists.".format(exists.name))
        
        return render_template(
            'course/partials/course_card_new.html',
            item=CourseSchema().dump(course)
        )


class CourseAPI(MethodView):
    def get(self: None, course_id: int) -> Course:
        """ Get a single course

        Args:
            course_id (int): Canvas ID
            canvas_id ([bool], optional): Search by Canvas ID instead of course ID

        Returns:
            Course: Instance of <Course>
        """
        from app.models import User
        args = parser.parse(CourseSchema(), location="querystring")

        if args and args['use_canvas_id']:
            course = Course.query.filter(Course.canvas_id == course_id).first()
        else:
            course = Course.query.filter(Course.id == course_id).first()
        
        if not course:
            abort(404)

        students = course.enrollments.filter(User.usertype_id == 3).all()

        # Aggregate all student scores into the course object.
        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user_score = getattr(outcome, current_user.preferences.score_calculation_method.name)(user.canvas_id)
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": user_score
                })
        
        return render_template(
            "course/index.html", 
            course=CourseSchema().dump(course), students=students
        )
    
    def delete(self: None, course_id: int) -> List[Course]:
        """ Remove a locally-stored course.

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[Course]: List of enrollments for the user.
        """
        course = Course.query.filter(Course.canvas_id == course_id).first()
        db.session.delete(course)
        db.session.commit()

        return "Course deleted."



class CourseAssignmentsAPI(MethodView):
    def get(self: None, course_id: int) -> List[Assignment]:
        """ Get assignments connected to a course by ID

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[Assignment]: Assignments linked to the course
        """
        from app.schemas import AssignmentSchema

        course = Course.query.filter(Course.canvas_id == course_id).first()
        return render_template(
            'assignment/partials/assignment_select.html',
            items=AssignmentSchema(many=True).dump(course.assignments),
            course_id=course_id
        )


class CourseEnrollmentsAPI(MethodView):
    def get(self: None, course_id: int) -> Course:
        """

        Args:
            self (None): [description]
            course_id (int): [description]

        Returns:
            Course: [description]
        """
        from app.models import User
        from app.schemas import UserSchema

        course = Course.query.filter(Course.canvas_id == course_id).first()
        if course is None:
            abort(404)
        
        students = course.enrollments.filter(User.usertype_id == 3).all()

        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": outcome.avg(user.canvas_id)
                })
        
        return jsonify(UserSchema(many=True, only=['canvas_id', 'name', 'scores']).dump(students))
        
        
class CourseOutcomesAPI(MethodView):
    def get(self: None, course_id: int) -> List[Outcome]:
        """ Retrieve a list of outcomes for a given course ID

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[Outcome]: List of Outcomes
        """
        from app.schemas import OutcomeSchema
        course = Course.query.filter(Course.canvas_id == course_id).first()

        if course is None:
            abort(404)
        
        return jsonify(OutcomeListSchema(many=True).dump(course.outcomes.all()))