import json
from typing import List
from flask import jsonify, abort, make_response, render_template, session
from flask_login import current_user
from flask.views import MethodView

from app import db
from app.schemas import AssignmentSchema, OutcomeSchema, CourseSchema, CanvasSyncServiceOutcome
from app.canvas_sync_service import CanvasSyncService

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
        from app.models import Course
        fetched_courses = self.service.get_courses("teacher", "available")
        stored_courses = [course.canvas_id for course in Course.query.all()]

        courses = [
            {
                "start_at": course.start_at,
                "name": f"{course.start_at[0:4]} - {course.name}", 
                "id": course.id, 
            } 
            for course in fetched_courses if course.id not in stored_courses and course.start_at is not None
        ]

        content = {
            "items": CourseSchema(many=True).dump(sorted(courses, key=lambda d: d['start_at'], reverse=True)),
            "partial": 'course/partials/course_small.html',
            "title": 'Import a course'
        }

        return render_template(
            'shared/partials/sidebar.html',
            position="right",
            **content
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
        from app.models import Course


        course = Course.query.filter(Course.canvas_id == course_id).first()

        # We don't want to duplicate Outcomes already stored in the database, so
        # this filters those out before returning the list. The Outcomes fetched
        # are specific to the course.
        fetched_outcomes = self.service.get_outcomes(course_id)

        # Filter out items that are not already associated with a course. The course
        # relationship is required because other courses might be using the same outcome 
        # from Canvas.
        stored_outcomes = [outcome.canvas_id for outcome in course.outcomes.all()]

        outcomes = [outcome for outcome in fetched_outcomes if outcome['id'] not in stored_outcomes]

        # Return a list of Outcomes in the right sidebar
        content = {
            "items": outcomes,
            "course_id": course_id,
            "partial": "outcome/partials/outcome_small.html",
            "title": "Import outcome..."
        }
        
        response = make_response(render_template(
            'shared/partials/sidebar.html',
            position="right",
            **content
        ))
        response.headers.set('HX-Trigger', json.dumps({'showToast': "Found {} outcomes".format(len(outcomes))}))
        
        return response


class SyncOutcomeAttemptsAPI(MethodView):
    def __init__(self):
        self.service = CanvasSyncService()

    def get(self: None, course_id: int) -> list:
        """ Fetch Outcome attempts from Canvas.

        Args:
            course_id (int): Canvas course ID

        Returns:
            list: List of Canvas Outcomes which can be stored locally.
        """
        from app.models import Course
        course = Course.query.filter(Course.id == course_id).first()

        if course is None:
            abort(404)
        
        # Get attempts for all outcomes already synced to a course locally.
        outcome_ids = [outcome.canvas_id for outcome in course.outcomes.all()]

        if bool(outcome_ids):
            try:
                result = self.service.get_outcome_attempts(course.canvas_id, outcome_ids)
                return jsonify({
                    "message": result,
                    "error": False
                })
            except Exception as e:
                abort(422)
        else:
            return jsonify({
                "message": "Sync at least one outcome from Canvas before importing results.",
                "error": True
            })
            

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
        from app.models import Assignment

        fetched_assignments = self.service.get_assignments(course_id)
        stored_assignments = [assignment.canvas_id for assignment in Assignment.query.all()]

        assignments = [assignment for assignment in fetched_assignments if assignment.id not in stored_assignments]

        content = {
            "items": assignments,
            "course_id": course_id,
            "partial": "assignment/partials/assignment_small.html",
            "title": "Import assignment..."
        }

        response = make_response(render_template(
            'shared/partials/sidebar.html',
            position="right",
            **content
        ))
        response.headers.set('HX-Trigger', json.dumps({'showToast': "Found {} assignments".format(len(assignments))}))
        
        return response
