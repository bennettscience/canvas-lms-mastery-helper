import json
import unittest
from app.errors import DuplicateException

from tests.util import TestBase

from app import app, db
from app.enums import MasteryCalculation
from app.models import Assignment, Course, Outcome, User, UserPreferences

class TestAssignments(TestBase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
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
            "course_id": 999,
            "points_possible": 1
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
            "course_id": 999,
            "points_possible": 1
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

        assignment = Assignment(canvas_id=123, name='Assignment 1')
        user = User(name="User", usertype_id=2, canvas_id=123)
        prefs = UserPreferences(user_id=1, score_calculation_method=MasteryCalculation(1), mastery_score=3)
        course = Course(name="Course 1", canvas_id=999)

        db.session.add_all([assignment, user, prefs, course])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_assignment_by_id(self):
        self.login(1)
        resp = self.client.get('/assignments/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], 'Assignment 1')
    
    def test_get_assignment_by_canvas_id(self):
        self.login(1)
        resp = self.client.get('/assignments/123?use_canvas_id=True')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], 'Assignment 1')
    
    def test_get_missing_assignment(self):
        self.login(1)
        resp = self.client.get('/assignments/999')
        self.assertEqual(resp.status_code, 404)


class TestAlignAssignment(unittest.TestCase):
    """ Test the alignment mechanism on the <Assignment> model.
        URL paths for this work are done against the Outcome.
    """
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        a1 = Assignment(canvas_id=123, name='Assignment 1')
        o1 = Outcome(canvas_id=123, name='Outcome 1')
        o2 = Outcome(canvas_id=456, name='Outcome 2')

        db.session.add_all([a1, o1])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_align_outcome(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()
        assignment.watch(outcome)

        self.assertIsInstance(assignment.watching, Outcome)
        self.assertTrue(assignment.is_watching(outcome))
        self.assertEqual(assignment.watching.name, 'Outcome 1')
    
    def test_unalign_outcome(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()
        assignment.watch(outcome)
        
        self.assertIsInstance(assignment.watching, Outcome)
        self.assertTrue(assignment.is_watching(outcome))

        assignment.unwatch()

        self.assertFalse(assignment.is_aligned())
    
    def test_assignment_not_aligned(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()

        self.assertFalse(assignment.is_watching(outcome))
    
    def test_outcome_already_aligned(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()
        assignment.watch(outcome)

        with self.assertRaises(DuplicateException):
            assignment.watch(outcome)

    def test_align_with_new_outcome(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()
        assignment.watch(outcome)

        self.assertTrue(assignment.is_watching(outcome))

        outcome2 = Outcome.query.filter(Outcome.canvas_id == 456).first()
        assignment.watch(outcome2)

        self.assertTrue(assignment.is_watching(outcome2))
