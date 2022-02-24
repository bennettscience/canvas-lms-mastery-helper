import unittest

from app import app, db
from app.models import Course, User

@unittest.skip('Needs refactor')
class TestUserListAPI(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        user = User(canvas_id=41015, usertype_id=1, name="Teacher", email="teacher@example.com")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_users(self):
        resp = self.client.get("/users")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 1)


@unittest.skip('Needs refactor')
class TestSingleUserAPI(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        user = User(canvas_id=41015, usertype_id=1, name="Teacher", email="teacher@example.com")
        
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_single_user(self):
        resp = self.client.get('/users/1')

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(resp.json['name'], 'Teacher')
        self.assertEqual(resp.json['usertype_id'], 1)

    def test_get_missing_user(self):
        resp = self.client.get('/users/2')

        self.assertTrue(resp.status_code == 404)

@unittest.skip('Needs refactor')
class TestUserCourseAPI(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        user = User(canvas_id=41015, usertype_id=1, name="Teacher", email="teacher@example.com")
        course = Course(canvas_id=90123, name="Test Course")
        
        db.session.add_all([user, course])
        db.session.commit()

        user.enroll(course)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_user_courses(self):
        resp = self.client.get('/users/1/courses')

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(len(resp.json), 1)