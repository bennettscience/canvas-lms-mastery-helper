import json
import unittest

from app import app, db
from app.models import Assignment, Outcome

class TestAssignments(unittest.TestCase):
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
    
    def test_get_assignments(self):
        resp = self.client.get('/assignments')
        assignments = resp.json

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(assignments) == 1)

    def test_create_assignment(self):
        headers = {"Content-Type": "application/json"}
        payload = {
            "canvas_id": 222,
            "name": "Assignment 2"
        }
        resp = self.client.post(
            "/assignments",
            data=json.dumps(payload),
            headers=headers
        )

        self.assertTrue(resp.status_code == 200)
        self.assertEqual(resp.json['name'], 'Assignment 2')
        self.assertEqual(resp.json['watching'], None)

    def test_assignment_conflict(self):
        headers = {"Content-Type": "application/json"}
        payload = {
            "canvas_id": 123,
            "name": "Assignment 2"
        }
        resp = self.client.post(
            "/assignments",
            data=json.dumps(payload),
            headers=headers
        )

        self.assertTrue(resp.status_code == 409)
        self.assertEqual(resp.json['description'], 'Assignment already exists. Please select a different assignment.')
    
    def test_malformed_assignment(self):
        headers = {"Content-Type": "application/json"}
        payload = {
            
        }
        resp = self.client.post(
            "/assignments",
            data=json.dumps(payload),
            headers=headers
        )

        self.assertTrue(resp.status_code == 422)
    

class TestSingleAssignment(unittest.TestCase):
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