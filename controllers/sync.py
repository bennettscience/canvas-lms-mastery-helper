from typing import List
from flask import jsonify, abort
from flask.views import MethodView

from app import db
from app.schemas import AssignmentSchema, OutcomeSchema, CourseSchema, CanvasSyncServiceOutcome
from app.canvas_sync import CanvasSyncService

"""
This module provides an HTTP interface with CanvasSyncService. CanvasSyncService
performs the large fetches and returns results for those operations for the client.
"""

class SyncCoursesAPI(MethodView):
    def __init__(self):
        self.service = CanvasSyncService()

    def get(self: None) -> list:
        """ Get a list of active courses for the user.

        Returns:
            list: Canvas courses as JSON
        """
        courses = self.service.get_courses("TeacherEnrollment", "available")
        
        length = len(list(courses))
        return jsonify(
            {
                "results": length, 
                "query_params": {
                    "enrollment_type": "TeacherEnrollment", 
                    "state": "available"
                }, 
            "courses": CourseSchema(many=True).dump(courses)
            }
        )


class SyncOutcomesAPI(MethodView):
    def __init__(self):
        self.service = CanvasSyncService()

    def get(self: None, course_id: int) -> list:
        """ Get a list of Outcomes attached to a course in Canvas.

        Args:
            course_id (int): Canvas course ID

        Returns:
            list: Outcomes represented as JSON
        """
        from canvasapi.outcome import Outcome

        outcomes = self.service.get_outcomes(course_id)
        return jsonify(OutcomeSchema(many=True).dump(outcomes))


class SyncOutcomeAttemptsAPI(MethodView):
    def __init__(self):
        self.service = CanvasSyncService()

    def get(self: None, course_id: int, outcome_id: int=None) -> list:
        try:
            result = self.service.get_outcome_attempts(course_id)
            return jsonify({"message": result})
        except Exception as e:
            abort(422)
            

class SyncAssignmentsAPI(MethodView):
    def __init__(self):
        self.service = CanvasSyncService()

    def get(self: None, course_id: int) -> list:
        """ Get a list of all active assignments in a course.

        Args:
            course_id (int): Canvas course ID

        Returns:
            list: <Assignment>
        """
        assignments = self.service.get_assignments(course_id)
        return jsonify(AssignmentSchema(many=True).dump(assignments))


# class SyncAssignmentAPI(MethodView):
#     def __init__(self):
#         self.service = CanvasSyncService()

#     def get(self: None, course_id: int, assignment_id: int) -> "Assignment":
#         assignment = self.service.get_assignment(course_id, assignment_id)

