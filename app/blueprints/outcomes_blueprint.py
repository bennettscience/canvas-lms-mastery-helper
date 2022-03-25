from flask import Blueprint, abort, jsonify

outcomes_bp = Blueprint('outcomes', __name__)
from controllers.outcomes import (
    OutcomeAPI,
    OutcomeListAPI,
    AlignmentAPI
)

outcomes_view = OutcomeListAPI.as_view("outcome_list_view")
outcome_view = OutcomeAPI.as_view("outcome_view")
alignment_view = AlignmentAPI.as_view("alignment_view")

outcomes_bp.add_url_rule("/outcomes", view_func=outcomes_view, methods=['GET', 'POST'])
outcomes_bp.add_url_rule("/outcomes/<int:outcome_canvas_id>", view_func=outcome_view, methods=['GET', 'PUT'])

# Update an alignment to an outcome for an assignment. Accepts:
#  PUT -> create a new alignment on the item
#  DELETE -> removes alignment on the item.
# The endpoint can handle both types of request. Define the action by the request method.
outcomes_bp.add_url_rule("/courses/<int:course_canvas_id>/outcomes/<int:outcome_canvas_id>/edit", view_func=alignment_view, methods=["GET", "PUT", "DELETE"])