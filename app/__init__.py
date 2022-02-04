from flask import Flask, send_from_directory, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from extensions import metadata
from config import Config

import jinja_partials

app = Flask(__name__, static_folder='static', template_folder='views')
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
ma = Marshmallow(app)
lm = LoginManager(app)
# CORS(app, resources={r"/auth/*": {"origins": "https://elkhart.instructure.com/*"}})

# toolbar = DebugToolbarExtension(app)
jinja_partials.register_extensions(app)

from app import app, db
from app.models import User
from app.blueprints.home_blueprint import home_bp
from app.blueprints.sync_blueprint import sync_bp
from app.blueprints.courses_blueprint import courses_bp
from app.blueprints.assignments_blueprint import assignments_bp
from app.blueprints.outcomes_blueprint import outcomes_bp
from app.blueprints.users_blueprint import users_bp
from app.blueprints.auth_blueprint import auth_bp

@lm.user_loader
def load_user(id):
    return User.query.get(id)

# Pull live information from Canvas.
app.register_blueprint(sync_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(assignments_bp)
app.register_blueprint(outcomes_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)