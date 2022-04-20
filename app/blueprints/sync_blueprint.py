from canvasapi import canvas
from flask import Blueprint, abort, jsonify

sync_bp = Blueprint('canvas_sync', __name__, url_prefix="/sync")
from app.controllers.sync import (
    SyncAssignmentsAPI,
    SyncOutcomeAttemptsAPI,
    SyncOutcomesAPI,
    SyncCoursesAPI
)

sync_assignments_view = SyncAssignmentsAPI.as_view("sync_assignments_api")
sync_outcome_attempts_view = SyncOutcomeAttemptsAPI.as_view("sync_outcome_attempts_api")
sync_outcomes_view = SyncOutcomesAPI.as_view("sync_outcomes_api")
sync_courses_view = SyncCoursesAPI.as_view("sync_courses_view")

sync_bp.add_url_rule("/outcomes/<course_id>", view_func=sync_outcomes_view, methods=['GET'])
sync_bp.add_url_rule("courses/<int:course_id>/outcomes/results", view_func=sync_outcome_attempts_view, methods=['GET', 'POST'])
sync_bp.add_url_rule("/assignments/<course_id>", view_func=sync_assignments_view, methods=['GET'])
sync_bp.add_url_rule("/courses", view_func=sync_courses_view, methods=['GET'])