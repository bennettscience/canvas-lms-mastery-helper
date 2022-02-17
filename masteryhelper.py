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

@app.cli.command('seed')
def seed():
    """ Seed the database with roles, permissions, defaults """
    print('Starting db setup')
    user_types = [
        UserType(name='Admin'),
        UserType(name='Teacher'),
        UserType(name='Student')
    ]
    print('Creating Admin, Teacher, and Student roles')
    db.session.add_all(user_types)
    db.session.commit()
    print('Roles created successfully.')


@app.cli.command('sync')
def sync():
    """ Sync outcome attempts from Canvas for all courses.
    """
    from app.canvas_sync_service import CanvasSyncService
    print('Starting sync...')
    courses = Course.query.all()
    service = CanvasSyncService()
    for course in courses:
        print('Syncing {}'.format(course.name))
        outcome_ids = [outcome.canvas_id for outcome in course.outcomes.all()]
        result = service.get_outcome_attempts(course.canvas_id, outcome_ids)
        print(result)
    print('Done!')