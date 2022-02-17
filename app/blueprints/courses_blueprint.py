from flask import abort, Blueprint, jsonify
from flask_login import current_user
from app import app

courses_bp = Blueprint('courses', __name__, template_folder='views')
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

# TODO: Update the endpoint
@courses_bp.route('/courses/<int:course_id>/scores', methods=['POST'])
def sync_all_outcome_scores(course_id: int):
    """ Post scores to aligned assignments for all outcomes in a course.

    Args:
        course_id (int): Course Canvas ID
    """
    from app.models import Course, User
    from app.canvas_sync_service import CanvasSyncService

    app.logger.info('Posting scores to Canvas for {}'.format(course_id))

    service = CanvasSyncService()

    # Get the stored outcomes
    course = Course.query.filter(Course.canvas_id == course_id).first()
    if course is None:
        abort(404)

    outcomes = course.outcomes.all()

    # TODO: Filter by UserType string name instead of ID
    students = course.enrollments.filter(User.usertype_id == 3).all()
    mastery_score = current_user.preferences.mastery_score
    calculation_method = current_user.preferences.score_calulcation_method.name


    for outcome in outcomes:
        if outcome.alignment is not None:
            app.logger.info('Outcome {} is aligned to assignment {}'.format(outcome.name, outcome.alignment.name))
            for student in students:
                student_score = getattr(outcome, calculation_method)(student.canvas_id)
                app.logger.info('{} has {} on {}'.format(student.name, student_score, outcome.name))
                
                if type(student_score) != str:
                    if student_score >= mastery_score:
                        request = service.post_assignment_submission(
                            course.canvas_id, 
                            outcome.alignment.canvas_id, 
                            student.canvas_id, 
                            1
                        )

    return jsonify({'message': 'Finished processing students.'})

@courses_bp.route('/courses/<int:course_id>/outcome/<int:outcome_id>/score', methods=['POST'])
def sync_single_outcome_score(course_id: int, outcome_id: int):
    """ Update student scores for a single outcome stored.

    Args:
        course_id (int): Canvas course ID
        assignment_id (int): Canvas assignment ID
    """
    from app.models import Course, Outcome, User
    from app.canvas_sync_service import CanvasSyncService

    mastery_score = current_user.preferences.mastery_score
    calculation_method = current_user.preferences.score_calculation_method.name
    service = CanvasSyncService()
    
    course = Course.query.filter(Course.canvas_id == course_id).first()

    # TODO: Filter by UserType string name instead of ID
    students = course.enrollments.filter(User.usertype_id == 3).all()

    if course is None:
        abort(404)
    
    outcome = course.outcomes.filter(Outcome.canvas_id == outcome_id).first()
    if outcome.alignment is not None:
        for student in students:
            student_score = getattr(outcome, calculation_method)(student.canvas_id)

            if type(student_score) != str:
                if student_score >= mastery_score:
                    request = service.post_assignment_submission(
                        course.canvas_id, 
                        outcome.alignment.canvas_id, 
                        student.canvas_id, 
                        1
                    )
    return jsonify({'message': 'Finished processing.'})
