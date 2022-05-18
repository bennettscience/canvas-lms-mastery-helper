import logging
from logging.handlers import RotatingFileHandler

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
    # Handle logging for this execution

    file_handler = RotatingFileHandler('logs/nightly_sync.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))

    # Define the log level in the appropriate environment
    file_handler.setLevel('INFO')
    app.logger.addHandler(file_handler)

    app.logger.setLevel('INFO')
    app.logger.info('Startup')

    from app.canvas_sync_service import CanvasSyncService
    app.logger.info('Starting sync...')
    courses = Course.query.all()
    service = CanvasSyncService('server_only')
    for course in courses:
        app.logger.info('Starting {}'.format(course.name))
        outcome_ids = [outcome.canvas_id for outcome in course.outcomes.all()]
        if outcome_ids:
            result = service.get_outcome_attempts(course.canvas_id, outcome_ids)
        else:
            result = "No outcomes stored for {}".format(course.name)
        app.logger.info(result)
    app.logger.info('Finished')

    app.logger.removeHandler(file_handler)
