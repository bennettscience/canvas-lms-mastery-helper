import json
import unittest
from tests.util import TestBase

from app import app, db
from app.models import Assignment, Course, Outcome


class TestOutcomes(TestBase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        assignment = Assignment(canvas_id=123, name='Assignment 1')
        outcome = Outcome(canvas_id=123, name='Outcome 1')
        course = Course(name="Course 1", canvas_id=999)

        db.session.add_all([assignment, course, outcome])

        course.outcomes.append(outcome)

        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_course_outcomes(self):
        resp = self.client.get('/outcomes')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)
        self.assertEqual(len(resp.json), 1)

    # TODO: check the template actually rendered
    # https://stackoverflow.com/questions/23987564/test-flask-render-template-context/24914680#24914680
    def test_get_single_outcome(self):
        resp = self.client.get('/outcomes/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Outcome 1', resp.data)
    
    def test_get_outcome_404(self):
        resp = self.client.get('/outcomes/123')
        self.assertEqual(resp.status_code, 404)
    
    def test_get_single_outcome_by_canvas_id(self):
        resp = self.client.get('/outcomes/123?use_canvas_id=True')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Outcome 1', resp.data)
        self.assertIn(b'Set up alignment', resp.data)

    def test_get_missing_outcome(self):
        resp = self.client.get('/outcomes/999')
        self.assertEqual(resp.status_code, 404)
    
    @unittest.skip
    def test_post_outcome(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'canvas_id': 456,
            'course_id': 999,
            'name': 'Outcome 2'
        }
        resp = self.client.post('/outcomes',
            data=data,
            headers=headers
        )
        self.assertTrue(resp.status_code == 200)

class TestOutcomeAlignments(TestBase):
    
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        assignment = Assignment(canvas_id=123, name='Assignment 1')
        course = Course(canvas_id=123, name='Course 1')
        outcome = Outcome(canvas_id=123, name='Outcome 1')

        db.session.add_all([assignment, course,  outcome])
        course.outcomes.append(outcome)
        course.assignments.append(assignment)

        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    # TODO: Set up template_rendered signal for assertion
    def test_get_outcome_alignment_template(self):
        resp = self.client.get('courses/123/outcomes/123/edit')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'select', resp.data)
    
    def test_align_assignment_to_outcome(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'assignment_id': '123'
        }
        resp = self.client.put(
            'courses/123/outcomes/123/edit',
            data=payload,
            headers=headers
            )
        self.assertEqual(resp.status_code, 200)
    
    def test_align_missing_assignment(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'assignment_id': '999'
        }
        resp = self.client.put(
            'courses/123/outcomes/123/edit',
            data=payload,
            headers=headers
            )
        result = json.loads(resp.json)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(result['description'], "No assignment with ID 999 found.")
    
    def test_align_missing_course(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'assignment_id': '123'
        }
        resp = self.client.put(
            'courses/123/outcomes/999/edit',
            data=payload,
            headers=headers
            )
        result = json.loads(resp.json)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(result['description'], "No outcome with ID 999 found.")

    def test_remove_alignment(self):
        # add an alignment we can delete via the HTTP route
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()
        assignment.watch(outcome)

        self.assertTrue(assignment.is_watching(outcome))

        resp = self.client.delete('/courses/123/outcomes/123/edit')
        self.assertEqual(resp.status_code, 200)
