from flask import Blueprint, abort, jsonify

assignments_bp = Blueprint('assignments', __name__)
from controllers.assignments import (
    AssignmentAPI,
    AssignmentListAPI,
    AlignmentAPI
)

assignments_view = AssignmentListAPI.as_view("assignment_list_view")
assignment_view = AssignmentAPI.as_view("assignment_view")
alignment_view = AlignmentAPI.as_view("alignment_view")


assignments_bp.add_url_rule("/assignments", view_func=assignments_view, methods=['GET', 'POST'])
assignments_bp.add_url_rule("/assignments/<assignment_id>", view_func=assignment_view, methods=['GET', 'PUT'])

# Update an alignment to an outcome for an assignment. Accepts:
#  PUT -> create a new alignment on the item
#  DELETE -> removes alignment on the item.
# The endpoint can handle both types of request. Define the action by the request method.
assignments_bp.add_url_rule("/assignments/<int:assignment_id>/alignment", view_func=alignment_view, methods=["PUT", "DELETE"])