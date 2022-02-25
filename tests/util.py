from multiprocessing import context
import unittest
from contextlib import contextmanager
from flask import template_rendered
from flask_login.utils import login_user

from app import app
from app.models import User

class TestBase(unittest.TestCase):
    @app.route('/auto_login/<int:user_id>')
    def auto_login(user_id):
        user = User.query.filter_by(id=user_id).first()
        login_user(user, remember=True)
        return "ok"

    def login(self, user_id):
        response = self.client.get(f"/auto_login/{user_id}")


@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append({
            "template_name": template.name,
            "context": context
        })
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)