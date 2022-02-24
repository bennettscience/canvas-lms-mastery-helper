import unittest
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
