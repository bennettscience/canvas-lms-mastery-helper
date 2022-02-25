import unittest

from flask_login import login_user
from tests.util import TestBase, captured_templates

from app import app, db
from app.enums import MasteryCalculation
from app.models import (
    Assignment, 
    Course, 
    Outcome,
    User, 
    UserPreferences
)


class TestCourseListAPI(TestBase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        course = Course(canvas_id=123, name="Course 1")
        user = User(name="User", usertype_id=2, canvas_id=123)
        prefs = UserPreferences(user_id=1, score_calculation_method=MasteryCalculation(1), mastery_score=3)

        db.session.add_all([user, prefs, course])
        
        # Make sure the user has at least one enrollment
        user.enroll(course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_course_list(self):
        self.login(1)
        # resp = self.client.get('/courses')

        with captured_templates(app) as templates:
            resp = self.client.get('/courses')
            template, context = templates[0]

            self.assertEqual(resp.status_code, 200)

            # Should return the sidebar and the course_card partial
            self.assertTrue(len(templates) == 2)

            # Check for all templates returned
            templates_rendered = [template['template_name'] for template in templates]
            self.assertIn('course/partials/course_card.html', templates_rendered)
            self.assertIn('shared/partials/sidebar.html', templates_rendered)

            # TODO: Check for items in template list
            # TODO: Are these loaded in reverse order (recursive)?
    
    @unittest.skip(
        "This needs a refactor. The POST endpoint inits a new CanvasSync \
         object to pull the course enrollments. If you want to test this \
             function on it's own, comment out those lines in the post function. \
        ")
    def test_create_new_course(self):
        self.login(1)
        payload = {
            "canvas_id": 456,
            "name": "Course 2"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        with captured_templates(app) as templates:
            resp = self.client.post('/courses',
                data=payload,
                headers=headers
            )
            template, context = templates[0]
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(len(templates) == 1)
            self.assertEqual(template.name, 'sidebar.html')

    
    def test_create_duplicate_course(self):
        from app.errors import DuplicateException
        self.login(1)
        payload = {
            "canvas_id": 123,
            "name": "Course 2"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        resp = self.client.post('/courses',
            data=payload,
            headers=headers
        )
        self.assertEqual(resp.status_code, 409)



class TestCourseAPI(TestBase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()
        self.client = app.test_client()

        # Create a full course with associations for users, assignments, and outcomes
        course = Course(canvas_id=123, name="Course 1")
        user = User(name="User", usertype_id=2, canvas_id=123)
        student = User(name='Student', usertype_id=3, canvas_id=456)
        prefs = UserPreferences(user_id=1, score_calculation_method=MasteryCalculation(1), mastery_score=3)
        outcome = Outcome(name="Outcome 1", canvas_id=123)
        assignment = Assignment(name="Assignmetn 1", canvas_id=123)

        db.session.add_all([assignment, course, outcome, prefs, student, user])
        
        user.enroll(course)
        student.enroll(course)
        course.assignments.append(assignment)
        course.outcomes.append(outcome)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_get_single_course(self):
        self.login(1)

        with captured_templates(app) as templates:
            resp = self.client.get('/courses/1')
            self.assertTrue(resp.status_code == 200)

            # A full course renders:
            #  course/index.html
            #  outcome/partials/outcome_card.html for aligned outcomes
            #  course/partials/score_table.html for the roster
            #  course/partials/student_entry.html for each student
            self.assertTrue(len(templates) == 4)
            
            templates_rendered = [template['template_name'] for template in templates]

            self.assertTrue('course/index.html' in templates_rendered)
            self.assertTrue('course/partials/score_table.html' in templates_rendered)
            self.assertTrue('course/partials/student_entry.html' in templates_rendered)
            self.assertTrue('outcome/partials/outcome_card.html' in templates_rendered)
    
    def test_get_single_course_by_canvas_id(self):
        self.login(1)
        resp = self.client.get('/courses/123?use_canvas_id=True')

        self.assertTrue(resp.status_code == 200)

    def test_get_missing_course(self):
        self.login(1)
        resp = self.client.get('/courses/2')

        self.assertTrue(resp.status_code == 404)


