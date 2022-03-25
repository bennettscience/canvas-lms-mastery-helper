
from flask_login import UserMixin
from sqlalchemy.orm import backref

from app import db, lm
from app.enums import MasteryCalculation
from app.errors import DuplicateException


class Manager(object):
    def create(self, cls, data):
        item = cls(**data)
        db.session.add(item)
        db.session.commit()

        return item

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        pass


class UserType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    usertype_id = db.Column(db.Integer, db.ForeignKey("user_type.id"))
    name = db.Column(db.String(255))

    # Used for OAuth
    token = db.Column(db.String(255))
    expiration = db.Column(db.Integer)
    refresh_token = db.Column(db.String(255))

    user_type = db.relationship('UserType')

    enrollments = db.relationship(
        "Course", 
        secondary="user_courses", 
        backref=backref("enrollments", lazy='dynamic'), 
        lazy='dynamic'
        )
    
    assessments = db.relationship(
        "OutcomeAttempt",
        backref=backref("user", cascade='all,delete,delete-orphan', single_parent=True),
        lazy='dynamic',
        passive_deletes=True
    )

    assignments = db.relationship(
        "UserAssignment",
        backref="user",
        uselist=True,
        lazy="dynamic"
    )

    preferences = db.relationship(
        "UserPreferences",
        backref=backref("user", uselist=False),
        uselist=False
    )
    
    def __repr__(self):
        return self.name

    def enroll(self, course):
        if not self.is_enrolled(course):
            self.enrollments.append(course)
            db.session.commit()
        else:
            raise DuplicateException('{} is already enrolled in {}'.format(self.name, course.name))
    
    def is_enrolled(self, course):
        return self.enrollments.filter(user_courses.c.course_id == course.id).count() > 0

# Manage user logins
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

class Course(db.Model, Manager):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime)

    outcomes = db.relationship("Outcome", secondary="course_outcomes", backref="course", lazy='dynamic')
    assignments = db.relationship("Assignment", cascade='all,delete', secondary="course_assignments", backref="course")

    def __repr__(self):
        return self.name


class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))

    attempts = db.relationship(
        "OutcomeAttempt",
        backref=backref("outcome", cascade='all,delete,delete-orphan', single_parent=True),
        lazy="dynamic",
        passive_deletes=True
    )

    def __repr__(self):
        return self.name

    def __get_scores(self, user_id):
        return [
            item.score for item in self.attempts.filter(OutcomeAttempt.user_canvas_id == user_id).all()
        ]

    # Define all of the math to run on an outcome
    def AVERAGE(self: None, user_id:int) -> float:
        """ Calculate the outcome average

        Args:
            user_id (int): Canvas user ID

        Returns:
            float: average
        """
        from statistics import fmean
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return None
        else:
            return round(fmean(scores), 1)
    
    def DECAYING_AVERAGE(self: None, user_id: int) -> float:
        """ Calulate a decaying average for the outcome.

        The last attempt is weighted higher than the average of all
        previous attempts. Canvas defaults to 35/65 for weights,
        those are matched here for consistency.

        scores = [1, 4, 2, 3, 5, 3, 6]
        float = 4.95

        Args:
            user_id (int): Canvas user ID

        Returns:
            float: decaying average
        """
        from statistics import fmean
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return None
        elif len(scores) == 1:
            # Handle a single attempt, return as a float for aesthetics.
            return float(scores[0])
        else:
            all = round((fmean(scores[:-1]) * 0.35), 2)
            last = round((scores[-1] * 0.65), 2)
            return round(all + last, 1)

    def HIGHEST(self: None, user_id: int) -> float:
        """ Return the highest score attempt

        Args:
            user_id (int): Canvas user ID

        Returns:
            float: highest attempt
        """
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return None
        else:
            return max(scores)

    def HIGH_LAST_AVERAGE(self: None, user_id: int) -> float:
        """ Average the last attemp with the highest attempt.

        Example 1:
        scores = [1, 4, 3, 2]
        Average = 3

        Example 2:
        scores = [1, 2, 3, 4]
        Average = 4

        Args:
            user_id (int): Canvas user ID

        Returns:
            float: average
        """
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return None
        else:
            return round((max(scores) + scores[-1]) / 2, 1)
    
    def MODE(self: None, user_id: int) -> float:
        """ Return the mode for the score sample.

        Canvas limits the mode to the nast 1 < n < 5 attemtps.
        This method will return the mode for all stored attempts.

        Args:
            user_id (int): Canvas user ID

        Returns:
            float: mode
        """
        from statistics import mode
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return None
        else:
            return mode(scores)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))
    points_possible = db.Column(db.Float)

    # Handling watching the Outcome score
    watching = db.relationship(
        "Outcome", 
        secondary="assignment_outcome", 
        backref=backref("alignment", uselist=False),
        uselist=False
    )

    student_attempts = db.relationship(
        "UserAssignment",
        backref="assignment",
    )

    def __repr__(self):
        return self.name
    
    def watch(self, outcome):
        if not self.is_watching(outcome):
            self.watching = outcome
            db.session.commit()
        else:
            raise DuplicateException(f"{self.name} is aleady aligned to Outcome {self.watching.name}.")
        
    def unwatch(self):
        self.watching = None
        db.session.commit()

    def is_watching(self, outcome):
        return self.watching is outcome
    
    def is_aligned(self):
        return self.watching is not None


# One to many
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    source_uri = db.Column(db.String(255))
    method = db.Column(db.String(32))
    json_payload = db.Column(db.String(1000))
    occurred = db.Column(db.DateTime)


# Many to many

class OutcomeAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_canvas_id = db.Column(db.Integer, db.ForeignKey("user.canvas_id", ondelete='CASCADE', onupdate='CASCADE' ))
    outcome_canvas_id = db.Column(db.Integer, db.ForeignKey("outcome.canvas_id", ondelete='CASCADE', onupdate='CASCADE'))
    attempt_canvas_id = db.Column(db.Integer, unique=True, nullable=False)
    success = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    occurred = db.Column(db.DateTime)

    def __repr__(self):
        return "{} - {}".format(self.user, self.occurred)


class UserAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.canvas_id", onupdate="CASCADE", ondelete="CASCADE"))
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.canvas_id", onupdate="CASCADE", ondelete="CASCADE"))
    score = db.Column(db.Integer)
    occurred = db.Column(db.DateTime)

    def __repr__(self):
        return "{} - {}".format(self.user, self.score)


class UserPreferences(Manager, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    score_calculation_method = db.Column(db.Enum(MasteryCalculation))
    mastery_score = db.Column(db.Integer)


user_courses = db.Table(
    "user_courses", 
    db.Column("id", db.Integer, primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id", onupdate="CASCADE", ondelete="CASCADE")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
)

course_outcomes = db.Table(
    "course_outcomes",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id", onupdate="CASCADE", ondelete="CASCADE")),
    db.Column("outcome_id", db.Integer, db.ForeignKey("outcome.id", onupdate="CASCADE", ondelete="CASCADE"))
)

course_assignments = db.Table(
    "course_assignments",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id", onupdate="CASCADE", ondelete="CASCADE")),
    db.Column("assignmend_id", db.Integer, db.ForeignKey("assignment.id", onupdate="CASCADE", ondelete="CASCADE"))
)

assignment_outcome = db.Table(
    "assignment_outcome",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("assignment_id", db.Integer, db.ForeignKey("assignment.id", onupdate="CASCADE", ondelete="CASCADE")),
    db.Column("outcome_id", db.Integer, db.ForeignKey("outcome.id", onupdate="CASCADE", ondelete="CASCADE"))
)

