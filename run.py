# This relies on a forked version of canvasapi
# which has OutcomeResult classed into a PaginatedList!

from app import app, db
from app.models import (
    Assignment, 
    Course, 
    Outcome,
    OutcomeAttempt, 
    User,
    UserType
    )

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Assignment': Assignment,
        'Course': Course,
        'Outcome': Outcome,
        'OutcomeAttempt': OutcomeAttempt,
        'User': User,
        'UserType': UserType
    }
