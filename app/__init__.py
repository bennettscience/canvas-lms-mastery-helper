import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory, render_template, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from extensions import metadata
from config import Config

import jinja_partials

app = Flask(__name__, static_folder='static', template_folder='views')
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
ma = Marshmallow(app)
lm = LoginManager(app)
admin = Admin(app, name='masteryhelper')

jinja_partials.register_extensions(app)

# Logging settings

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/masteryhelper.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    # Define the log level in the appropriate environment
    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
    file_handler.setLevel(LOGLEVEL)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(LOGLEVEL)
    app.logger.info('Startup')


from app import app, db
from app.models import Course, Outcome, User, UserType
from app.blueprints.home_blueprint import home_bp
from app.blueprints.sync_blueprint import sync_bp
from app.blueprints.courses_blueprint import courses_bp
from app.blueprints.assignments_blueprint import assignments_bp
from app.blueprints.outcomes_blueprint import outcomes_bp
from app.blueprints.users_blueprint import users_bp
from app.blueprints.auth_blueprint import auth_bp

# Register admin pages
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Outcome, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(UserType, db.session))

# Register routes
app.register_blueprint(sync_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(assignments_bp)
app.register_blueprint(outcomes_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)