import unittest

from app import app, db
from app.models import Course 


class TestCourseListAPI(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        course = Course(canvas_id=41015, name="Course 1")

        db.session.add(course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_course_list(self):
        resp = self.client.get('/courses')

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(len(resp.json), 1)


class TestCourseAPI(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        course = Course(canvas_id=41015, name="Course 1")
        
        db.session.add(course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_single_course(self):
        resp = self.client.get('/courses/1')

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(resp.json['name'], 'Course 1')
    
    def test_get_missing_course(self):
        resp = self.client.get('/courses/2')

        self.assertTrue(resp.status_code == 404)


