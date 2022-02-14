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


@app.cli.command('scheduled')
def scheduled():
    from app.canvas_sync import CanvasSyncService
    print('loading...')
    courses = Course.query.all()
    service = CanvasSyncService()
    for course in courses:
        print(f'Syncing {course.name}')
        outcome_ids = [outcome.canvas_id for outcome in course.outcomes.all()]
        service.get_outcome_attempts(course.canvas_id, outcome_ids)
    print('Done!')