import json
from flask import jsonify
from marshmallow.exceptions import ValidationError
from warnings import warn

from app import app

def deprecation(message: str) -> str:
    warn(message, DeprecationWarning, stacklevel=2)

class DuplicateException(Exception):
    def __init__(self, description):
        super().__init__(description)


@app.errorhandler(ValidationError)
def marshmallow_error_handler(error):
    app.logger.info('Caught validation error')
    return jsonify(error.messages), 422

@app.errorhandler(401)
def unauthorized(err):
    response = err.get_response()
    response.data = json.dumps(
        {
            "code": err.code,
            "name": "Wrong Authorization",
            "description": "Incorrect authorization credentials used in the request."
        }
    )
    response.content_type = "application/json"
    return response

@app.errorhandler(403)
def forbidden(err):
    response = err.get_response()
    response.data = json.dumps(
        {
            "code": err.code,
            "name": "Forbidden",
            "description": "You do not have permission to access this resource."
        }
    )
    response.content_type = "application/json"
    return response

@app.errorhandler(404)
def page_not_found(err):
    response = err.get_response()
    response.errors = json.dumps(
        {
            "code": err.code,
            "name": err.name,
            "description": err.description,
        }
    )
    # response.content_type = "application/json"
    return jsonify(response.errors), 404

@app.errorhandler(409)
def request_conflict(err):
    response = err.get_response()
    response.errors = json.dumps(
        {
            "code": err.code,
            "name": err.name,
            "description": err.description
        }
    )
    # response.content_type = "application/json"
    return jsonify(response.errors), 409

@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    # Catch errors from webargs and Marshmallow
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:    
        return jsonify({"errors": messages}), err.code

@app.errorhandler(500)
def internal_error(err):
    response = err.get_response()
    response.data = json.dumps(
        {
            "code": err.code,
            "name": err.name,
            "description": err.description
        }
    )
    response.content_type = "applicaton/json"
    return response
