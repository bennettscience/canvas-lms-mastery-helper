from canvasapi import Canvas
from canvasapi.course import Course
from typing import List

from app import db
from config import Config
from app.models import Assignment, Course, Outcome, User



class CanvasSyncService:
    """
    Much of this application depends on fetching and sorting data from Canvas. In order to maintain
    accurate records, this class handles the specific API endpoints needed from Canvas.

    Calls are made with canvasapi to keep things neat. Records are added to the database
    as needed for each function. Each resource's `canvas_id` is unique, so that constraint is
    applied when writing new resources to the database.

    In the future, Canvas will support a GraphQL API on all routes, which will help with the 
    querying and filtering to prevent duplicates. For now, only REST endpoints are supported, so
    resources are all checked before committing to memory.
    """

    # TODO: Set current user param on Sync object to cut down on passing IDs around
    def __init__(self):
        self.canvas = Canvas(Config.CANVAS_URI, Config.CANVAS_KEY)

    def get_courses(self: None, enrollment_type: str='TeacherEnrollment', state: str='active') -> List[Course]:
        """ Fetch all courses from Canvas. Calls `canvasapi.Canvas.get_courses()`.

        Args:
            enrollment_type ([str], optional): Canvas enrollment type to filter by. Defaults to 'TeacherEnrollment'.
            state ([str], optional): Canvas enrollment state to filter. Defaults to 'active'.

        Returns:
            List[Course]: List of <Course>
        """
        return self.canvas.get_courses(enrollment_role=enrollment_type, state=state)
    
    def get_course(self: None, course_id: int) -> Course:
        """ Fetch a single course from Canvas.

        Args:
            course_id (int): Canvas course ID

        Returns:
            Course: instance of <Course>
        """
        return self.canvas.get_course(course_id)
    
    def get_outcomes(self, course_id: int) -> List["Outcome"]:
        """ Get Outcomes from Canvas, but don't store in the database

        This fetches outcomes from Canvas. All storage will go into the POST route
        from the frontend.

        Args:
            endpoint (str): which resource to get

        Returns:
            list: list of dict(Outcome)
        """
        from canvasapi.outcome import Outcome

        request = self.canvas.get_course(course_id).get_all_outcome_links_in_context()
        # Instantiate each Outcome as a canvas object to maintain methods
        outcomes = [
            {"name": item.outcome['title'], "id": item.outcome['id']} for item in request
            ]
        return outcomes

    def get_outcome(self: None, outcome_id: int) -> None:
        """ 
        Retrieve a single Outcome from Canvas. This does not include results. For
        Outcomes with results, use `Sync().get_outcome_results()`.

        Args:
            course_id (int): Canvas course ID
            outcome_id (int): Canvs Outcome ID

        Returns:
            Outcome: <Outcome>
        """
        outcome_exists = Outcome.query.filter(Outcome.canvas_id == outcome_id).scalar()
        if outcome_exists is None:
            outcome = self.canvas.get_outcome(outcome_id)
            db.session.add(Outcome(canvas_id=outcome.id, name=outcome.title))
            db.session.commit()
        else:
            outcome = Outcome.query.filter(Outcome.canvas_id == outcome_id).first()
        
        return outcome

    def get_outcome_attempts(self: None, course_id: int, outcome_id: int=None, user_id: int=None, ) -> None:
        """ 
        Sync all attempts on an outcome for a student. This requests results for all students in a course. Each
        attempt has a unique ID already assigned. If it exists in the database, move on.

        This operations writes outcome attempts to persistent storage.

        {
            'outcome_results': [
                {
                    'hidden': False,
                    'hide_points': False,
                    'id': 200559,
                    'links': {
                        'alignment': 'assignment_259284',
                        'assignment': 'assignment_259284',
                        'learning_outcome': '16987',
                        'user': '31871'
                    },
                    'mastery': True,
                    'percent': 0.75,
                    'possible': 4.0,
                    'score': 3.0,
                    'submitted_or_assessed_at': '2021-03-04T17:46:29Z'
                },
                ...
            ]
        }

        Args:
            course_id (int): Canvas course ID.
            user_id (int): Canvas user ID.
            outcome_id ([int], optional): Limit results to a single outcome result. Defaults to None.

        Returns:
            None
        """
        from datetime import datetime
        from app.models import Course, Outcome, OutcomeAttempt

        # Track how many attempts are added to the DB
        count = 0

        # Outcome results are stored at the Course context, which is why the course needs
        # to be loaded first.
        canvas_course = self.canvas.get_course(course_id)
        
        # This is run when a single outcome is imported from the sync service.
        # This process relies on a modded version of canvasapi stored _locally_
        # which returns results in a PaginatedList.
        
        # TODO: Handle single outcome request vs all
        results = canvas_course.get_outcome_results(outcome_ids=[outcome_id])

        # Put new results into an array for a single db write.
        attempts = []

        for attempt in results:
            # breakpoint()
            # Handle outcomes first. The OutcomeAttempt model has a foreignkey constraint against
            # outcome foreign keys.
            # outcome_exists = Outcome.query.filter(Outcome.canvas_id == result['links']['learning_outcome']).scalar()
            
            # if outcome_exists is None:
            #     course = Course.query.filter(Course.canvas_id == course_id).first()
            #     canvas_outcome = self.canvas.get_outcome(result['links']['learning_outcome'])
            #     outcome = Outcome(canvas_id=canvas_outcome.id, name=canvas_outcome.title)
            #     db.session.add(outcome)
            #     db.session.commit()
               
            #     # Store the retrieved outcome in the course context
            #     course.outcomes.append(outcome)
            #     db.session.commit()

            attempt_exists = OutcomeAttempt.query.filter(OutcomeAttempt.attempt_canvas_id == attempt.id).scalar()
            
            if attempt_exists is None:
                # Convert the datetime string into a Python DateTime object
                dt = datetime.strptime(attempt.submitted_or_assessed_at[:-1], "%Y-%m-%dT%H:%M:%S")
                attempts.append(
                    OutcomeAttempt(
                        user_canvas_id=int(attempt.links['user']),
                        outcome_canvas_id=int(attempt.links['learning_outcome']),
                        attempt_canvas_id=attempt.id,
                        success=attempt.mastery,
                        score=attempt.score,
                        occurred=dt
                    )
                )

        if len(attempts) > 0:
            db.session.add_all(attempts)
            result = f"Stored {len(attempts)} new attempts."
        else: 
            result = "No new attempts saved."
            
        db.session.commit()
        return result

    def get_assignments(self: None, course_id: int) -> List[Assignment]:
        """ Get a list of assignments from a Canvas course. This DOES NOT put the 
        assignments into the database.

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[Assignment]: List of <Assignment>
        """
        assignments = self.canvas.get_course(course_id).get_assignments()
        return assignments

    def get_assignment(self: None, course_id: int, assignment_id: int) -> None:
        """
        Get a single assignment from Canvas and store locally. A locally stored assignment can be set
        to watch an Outcome overall score and updated automatically.

        This method should be used to sync assignments after an initial assignment sync.

        Args:
            course_id (int): Canvas course ID
            assignment_id (int): Canvas assignment ID
        """
        assignment = self.canvas.get_course(course_id).get_assignment(assignment_id)
        return assignment

    def post_assignment_scores(self: None, course_id: int, assignment) -> None:
        """
        Post assignment scores to Canvas.

        Based on Outcome scores, send AssignmentAttempt scores to the Canvas gradebook.

        Args:
            course_id (int): Canvas course ID
            assignment (List[AssignmentAttempt]): List of <AssignmentAttempt>
        """
        pass

    
    def get_enrollments(self: None, course_id: int) -> Course:
        """ Get all enrollments for a course. 

        This method stores all users in a course when it is added by the user for tracking.
        Students are added as users via their Canvas ID.

        Args:
            course_id (int): Canvas course ID

        Returns:
            List[User]: List of Users to append to the course.
        """
        users = []
        new_users = []
        canvas_course = self.canvas.get_course(course_id)
        enrollments = canvas_course.get_enrollments(
            type='StudentEnrollment',
            state='active'
        )
        
        # This is a poor way to get new users added to the database _and_ associated 
        # with the course. Right now, this saves multiple database commits after each
        # record is created. It might not be making any performance difference.
        for enrollment in enrollments:
            user_exists = User.query.filter(User.canvas_id == enrollment.user_id).scalar()
            if not user_exists:
                user = User(
                    canvas_id=enrollment.user_id, 
                    name=enrollment.user['sortable_name'], 
                    usertype_id=2,
                    email=None
                )
                new_users.append(user)
                users.append(user)
            else:
                users.append(user_exists)

        if len(new_users) > 0:
            db.session.add_all(users)

        course = Course.query.filter(Course.canvas_id == course_id).first()
        course.enrollments.extend(users)
        
        db.session.commit()

        # Return the updated <Course> because it includes all information.
        return course
