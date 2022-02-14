from flask import Blueprint

courses_bp = Blueprint('courses', __name__, template_folder='templates')
from controllers.courses import (
    CourseEnrollmentsAPI,
    CourseListAPI,
    CourseAPI,
    CourseAssignmentsAPI,
    CourseOutcomesAPI
)
from controllers.outcome_attempt import OutcomeAttemptsAPI, UserOutcomeAttemptAPI

courses_view = CourseListAPI.as_view("course_list_view")
course_view = CourseAPI.as_view("course_view")
course_assignments_view = CourseAssignmentsAPI.as_view("course_assignments_view")
course_enrollments_view = CourseEnrollmentsAPI.as_view("course_enrollments_view")
course_outcomes_view = CourseOutcomesAPI.as_view("course_outcomes_view")
outcome_attempts_view = OutcomeAttemptsAPI.as_view("outcome_attempts_view")
user_outcome_attempts_view = UserOutcomeAttemptAPI.as_view("user_outcome_attempts_view")

courses_bp.add_url_rule("/courses", view_func=courses_view, methods=['GET', 'POST'])
courses_bp.add_url_rule("/courses/<int:course_id>", view_func=course_view, methods=['GET', 'DELETE'])
courses_bp.add_url_rule("/courses/<int:course_id>/enrollments", view_func=course_enrollments_view, methods=['GET'])
courses_bp.add_url_rule("/courses/<int:course_id>/assignments", view_func=course_assignments_view, methods=['GET'])
courses_bp.add_url_rule("/courses/<int:course_id>/outcomes", view_func=course_outcomes_view, methods=['GET'])
courses_bp.add_url_rule(
    "/courses/<int:course_id>/outcomes/<int:outcome_id>", 
    view_func=outcome_attempts_view, 
    methods=['GET']
)
courses_bp.add_url_rule(
    "/courses/<int:course_id>/users/<int:user_id>/results/<int:outcome_id>",
    view_func=user_outcome_attempts_view,
    methods=['GET']
)