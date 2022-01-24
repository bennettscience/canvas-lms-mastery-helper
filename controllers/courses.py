from flask import abort, jsonify, request, render_template
from flask_login import current_user
from flask.views import MethodView
from typing import List
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
        courses = Course.query.all()

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
        from app.canvas_sync import CanvasSyncService

        args = parser.parse(CourseSchema(), location="json")
        exists = Course.query.filter(Course.canvas_id == args['canvas_id']).scalar()
        
        # TODO: Get all students and outcome results for the course.
        if not exists:
            course = Manager().create(Course, args)
            current_user.enroll(course)

            service = CanvasSyncService()

            # Store all students as new users and enroll in the course.
            service.get_enrollments(course.canvas_id)
            result = jsonify(CourseSchema().dump(course))
        else:
            abort(409)
        
        return result



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

        students = course.enrollments.filter(User.usertype_id == 2).all()

        # Aggregate all student scores into the course object.
        for user in students:
            user.scores = []
            for outcome in course.outcomes.all():
                user.scores.append({
                    "outcome_canvas_id": outcome.canvas_id,
                    "score": outcome.avg(user.canvas_id)
                })
        
        return render_template(
            "course/index.html", 
            course=CourseSchema().dump(course), students=students
        )


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
            'assignments/partials/assignment_select.html',
            items=AssignmentSchema(many=True).dump(course.assignments)
        )
        # return render_template(
        #     'shared/partials/sidebar.html',
        #     position='right',
        #     partial='assignments/partials/assignment_card.html',
        #     items=AssignmentSchema(many=True).dump(course.assignments)
        # )


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
        
        students = course.enrollments.filter(User.usertype_id == 2).all()

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