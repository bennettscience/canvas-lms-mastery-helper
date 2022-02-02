from flask import Blueprint, abort, jsonify

assignments_bp = Blueprint('assignments', __name__)
from controllers.assignments import (
    AssignmentAPI,
    AssignmentListAPI,
)

assignments_view = AssignmentListAPI.as_view("assignment_list_view")
assignment_view = AssignmentAPI.as_view("assignment_view")

assignments_bp.add_url_rule("/assignments", view_func=assignments_view, methods=['GET', 'POST'])
assignments_bp.add_url_rule("/assignments/<assignment_id>", view_func=assignment_view, methods=['GET', 'PUT'])