import json
import unittest
from app.errors import DuplicateException

from tests.util import TestBase, captured_templates

from app import app, db
from app.enums import MasteryCalculation
from app.models import Assignment, Course, Outcome, User, UserPreferences

class TestAssignments(TestBase):

    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        assignment = Assignment(canvas_id=123, name='Assignment 1', points_possible=10)
        user = User(name="User", usertype_id=2, canvas_id=123)
        prefs = UserPreferences(user_id=1, score_calculation_method=MasteryCalculation(1), mastery_score=3)
        course = Course(name="Course 1", canvas_id=999)

        db.session.add_all([assignment, course, user, prefs])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    # GET not allowed on this route
    def test_get_assignments(self):
        self.login("User")
        resp = self.client.get('/assignments')

        self.assertEqual(resp.status_code, 405)

    # Make a new assignment in the DB
    def test_create_assignment(self):
        self.login("User")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "assignment_canvas_id": 222,
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

    # Error if the assignment already exists
    def test_assignment_conflict(self):
        self.login("User")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "assignment_canvas_id": 123,
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
    
    # Bad post data
    def test_malformed_assignment(self):
        self.login("User")
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

    # 404 if the local db ID is used
    def test_get_assignment_by_local_id(self):
        self.login("User")
        resp = self.client.get('/assignments/1')
        self.assertEqual(resp.status_code, 404)
    
    def test_get_assignment_by_canvas_id(self):
        self.login("User")
        resp = self.client.get('/assignments/123')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], 'Assignment 1')
    
    def test_get_missing_assignment(self):
        self.login("User")
        resp = self.client.get('/assignments/999')
        self.assertEqual(resp.status_code, 404)


class TestAlignAssignmentModel(unittest.TestCase):
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

        db.session.add_all([a1, o1, o2])
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
    
    def test_assignment_already_aligned_to_outcome(self):
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
        self.assertEqual(outcome2.alignment, assignment)
        self.assertTrue(outcome.alignment is None)


class TestAlignAssignmentAPI(TestBase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        course = Course(canvas_id=123, name='Course 1')
        a1 = Assignment(canvas_id=123, name='Assignment 1')
        a2 = Assignment(canvas_id=456, name='Assignment 2')
        o1 = Outcome(canvas_id=123, name='Outcome 1')
        o2 = Outcome(canvas_id=456, name='Outcome 2')

        db.session.add_all([course, a1, a2, o1, o2])

        course.assignments.append(a1)
        course.outcomes.extend([o1, o2])

        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_alignment_card(self):
        with captured_templates(app) as templates:
            resp = self.client.get('/courses/123/outcomes/123/edit')
            self.assertTrue(resp.status_code == 200)
            self.assertTrue(len(templates), 1)

            template = templates[0]

            self.assertEqual(template['template_name'], 'outcome/partials/outcome_alignment_form.html')
            self.assertEqual(len(template['context']['assignments']), 1)
    
    def test_align_assignment_to_outcome(self):
        with captured_templates(app) as templates:
            data = {
                'assignment_canvas_id': 123
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            resp = self.client.put('/courses/123/outcomes/123/edit',
                data=data,
                headers=headers
            )
            self.assertTrue(resp.status_code == 200)
            
            # A successful response returns at least two templates:
            # `outcome/partials/alignment_change_oob.html` -> handles the DOM swap
            # `outcome/partials/outcome_card.html` -> The actual outcome card element
            self.assertTrue(len(templates) >= 2)

            templates_rendered = [template['template_name'] for template in templates]

            self.assertTrue('outcome/partials/alignment_change_oob.html' in templates_rendered)
            self.assertTrue('outcome/partials/outcome_card.html' in templates_rendered)

            # the wrapper template is always last in the array, so get that one to check context
            # for partials rendered
            template = templates[-1]

            # The actual outcome is rendered in a partial _inside_ the OOB swap template
            self.assertEqual(template['template_name'], 'outcome/partials/alignment_change_oob.html')
            self.assertTrue(len(template['context']['items']) == 2)

    def test_remove_alignment_from_outcome(self):
        # Set up the alignment
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()

        assignment.watch(outcome)

        with captured_templates(app) as templates:
            resp = self.client.delete('/courses/123/outcomes/123/edit')

            self.assertTrue(resp.status_code == 200)

            self.assertTrue(len(templates) >= 2)

            templates_rendered = [template['template_name'] for template in templates]

            self.assertTrue('outcome/partials/alignment_change_oob.html' in templates_rendered)
            self.assertTrue('outcome/partials/outcome_card.html' in templates_rendered)

            # the wrapper template is always last in the array, so get that one to check context
            # for partials rendered
            template = templates[-1]

            # The actual outcome is rendered in a partial _inside_ the OOB swap template
            self.assertEqual(template['template_name'], 'outcome/partials/alignment_change_oob.html')
            self.assertTrue(len(template['context']['items']) == 2)
            self.assertEqual(template['context']['items'][0]['alignment'], None)
    
    def test_add_already_aligned_outcome_to_new_assignment(self):
        # This tests that an assignment already aligned to an outcome is moved
        # to the _new_ alignment and returns TWO outcome cards in the template.
        # This is not the same as a conflict test because that only prevents
        # aligning the _same_ assignment to an outcome.
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()

        assignment.watch(outcome)

        self.assertTrue(assignment.is_watching(outcome))

        data = {
            "assignment_canvas_id": 456,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with captured_templates(app) as templates:
            resp = self.client.put('/courses/123/outcomes/123/edit',
                data=data,
                headers=headers
            )

            self.assertTrue(resp.status_code == 200)
            self.assertTrue(len(templates) >= 2)

            templates_rendered = [template['template_name'] for template in templates]

            self.assertTrue('outcome/partials/alignment_change_oob.html' in templates_rendered)
            self.assertTrue('outcome/partials/outcome_card.html' in templates_rendered)

            # the wrapper template is always last in the array, so get that one to check context
            # for partials rendered
            template = templates[-1]

            # The actual outcome is rendered in a partial _inside_ the OOB swap template
            self.assertEqual(template['template_name'], 'outcome/partials/alignment_change_oob.html')
            self.assertTrue(template['context']['items'][0]['alignment']['name'] == 'Assignment 2')
            self.assertTrue(template['context']['items'][1]['alignment'] ==  None)

    

    def test_align_same_assignment(self):
        assignment = Assignment.query.filter(Assignment.canvas_id == 123).first()
        outcome = Outcome.query.filter(Outcome.canvas_id == 123).first()

        assignment.watch(outcome)

        self.assertTrue(assignment.is_watching(outcome))

        data = {
            'assignment_canvas_id': 123
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        # Try to align the same assignment with the API
        resp = self.client.put('/courses/123/outcomes/123/edit',
            data=data,
            headers=headers
        )
        self.assertEqual(resp.status_code, 409)

