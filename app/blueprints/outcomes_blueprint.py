from flask import Blueprint, abort, jsonify
from app.models import Outcome

outcomes_bp = Blueprint('outcomes', __name__)
from controllers.outcomes import (
    OutcomeAPI,
    OutcomeListAPI
)

outcomes_view = OutcomeListAPI.as_view("outcome_list_view")
outcome_view = OutcomeAPI.as_view("outcome_view")

outcomes_bp.add_url_rule("/outcomes", view_func=outcomes_view, methods=['GET', 'POST'])
outcomes_bp.add_url_rule("/outcomes/<outcome_id>", view_func=outcome_view, methods=['GET', 'PUT'])
