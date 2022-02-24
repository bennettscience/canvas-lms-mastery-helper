import json
import unittest
from flask_login.utils import login_user

from tests.base import TestBase

from app import app, db
from app.enums import MasteryCalculation
from app.models import Assignment, Course, Outcome, User, UserPreferences

class TestAssignments(TestBase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.config['FLASK_ENV'] = 'testing'
        db.create_all()
        self.client = app.test_client()

        assignment = Assignment(canvas_id=123, name='Assignment 1')
        user = User(name="User", usertype_id=2, canvas_id=123)
        prefs = UserPreferences(user_id=1, score_calculation_method=MasteryCalculation(1), mastery_score=3)
        course = Course(name="Course 1", canvas_id=999)

        db.session.add_all([assignment, course, user, prefs])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_assignments(self):
        self.login(1)
        resp = self.client.get('/assignments')

        self.assertEqual(resp.status_code, 405)

    def test_create_assignment(self):
        self.login(1)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "canvas_id": 222,
            "name": "Assignment 2",
            "course_id": 999
        }
        resp = self.client.post(
            "/assignments",
            data=payload,
            headers=headers
        )

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(resp.json['message'], 'Import successful')

    def test_assignment_conflict(self):
        self.login(1)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "canvas_id": 123,
            "name": "Assignment 2",
            "course_id": 999
        }
        resp = self.client.post(
            "/assignments",
            data=payload,
            headers=headers
        )

        response_body = json.loads(resp.json)

        self.assertTrue(resp.status_code == 409)
        self.assertEqual(response_body['description'], 'Assignment already exists. Please select a different assignment.')
    
    def test_malformed_assignment(self):
        self.login(1)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            
        }
        resp = self.client.post(
            "/assignments",
            data=json.dumps(payload),
            headers=headers
        )

        self.assertTrue(resp.status_code == 422)
    

class TestSingleAssignment(TestBase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        a1 = Assignment(canvas_id=123, name='Assignment 1')

        db.session.add(a1)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_assignment_by_id(self):
        resp = self.client.get('/assignments/1')
        self.assertEqual(resp.status_code, 200)
    
    def test_get_assignment_by_canvas_id(self):
        resp = self.client.get('/assignments/123?use_canvas_id=True')
        self.assertEqual(resp.status_code, 200)
    
    def test_get_missing_assignment(self):
        resp = self.client.get('/assignments/999')
        self.assertEqual(resp.status_code, 404)


class TestUpdateAssignment(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        a1 = Assignment(canvas_id=123, name='Assignment 1')
        o1 = Outcome(canvas_id=999, name='Outcome 1')

        db.session.add_all([a1, o1])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_align_assignment(self):
        payload = {
            "outcome_canvas_id": 999
        }
        headers = {"Content-Type": "application/json"}
        resp = self.client.put('/assignments/1/alignment', data=json.dumps(payload), headers=headers)

        self.assertEqual(resp.status_code, 200)
    
    def test_align_no_payload(self):
        payload = {}
        headers = {"Content-Type": "application/json"}
        resp = self.client.put('/assignments/1/alignment', data=json.dumps(payload), headers=headers)

        self.assertEqual(resp.status_code, 422)
    
    def test_delete_alignment(self):
        headers = {"Content-Type": "application/json"}
        resp = self.client.delete('/assignments/1/alignment', headers=headers)

        self.assertEqual(resp.status_code, 200)

    def test_alignment_already_exists(self):
        a = Assignment.query.get(1)
        o = Outcome.query.get(1)
        a.watch(o)

        payload = {
            "outcome_canvas_id": 999
        }
        headers = {"Content-Type": "application/json"}
        resp = self.client.put('/assignments/1/alignment', data=json.dumps(payload), headers=headers)

        self.assertEqual(resp.status_code, 409)

    def test_alignment_assignment_404(self):
        payload = {
            "outcome_canvas_id": 999
        }
        headers = {"Content-Type": "application/json"}
        resp = self.client.put('/assignments/2/alignment', data=json.dumps(payload), headers=headers)

        self.assertEqual(resp.status_code, 404)