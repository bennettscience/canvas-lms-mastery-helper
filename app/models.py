
from flask_login import UserMixin
from sqlalchemy.orm import backref

from app import db, lm
from app.enums import MasteryCalculation
from app.errors import AlignmentExistsException


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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    usertype_id = db.Column(db.Integer, db.ForeignKey("user_type.id"))
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))

    enrollments = db.relationship(
        "Course", 
        secondary="user_courses", 
        backref=backref("enrollments", lazy='dynamic'), 
        lazy='dynamic'
        )
    
    assessments = db.relationship(
        "OutcomeAttempt",
        backref="users",
        lazy='dynamic'
    )

    assignments = db.relationship(
        "UserAssignment"
    )

    preferences = db.relationship(
        "UserPreferences",
        backref=backref("user", uselist=False),
        uselist=False
    )

    def enroll(self, course):
        if not self.is_enrolled(course):
            self.enrollments.append(course)
            db.session.commit()
        else:
            return f"User is already enrolled in {course.name}"
    
    def is_enrolled(self, course):
        return self.enrollments.filter(user_courses.c.course_id == course.id).count() > 0

    def set_preferences(self):
        print(self.preferences)


class Course(db.Model, Manager):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))

    outcomes = db.relationship("Outcome", secondary="course_outcomes", backref="course", lazy='dynamic')
    assignments = db.relationship("Assignment", secondary="course_assignments", backref="course")


class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))

    attempts = db.relationship(
        "OutcomeAttempt",
        backref="outcome",
        lazy="dynamic"
    )

    def __get_scores(self, user_id):
        return [
            item.score for item in self.attempts.filter(OutcomeAttempt.user_canvas_id == user_id).all()
        ]

    def AVERAGE(self, user_id):
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return 'No attempts'
        else:
            return round(sum(scores) / len(scores), 1)

    def HIGHEST(self, user_id):
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return 'No attempts'
        else:
            return max(scores)

    def HIGH_LAST_AVERAGE(self, user_id):
        scores = self.__get_scores(user_id)
        if len(scores) == 0:
            return 'No attempts'
        else:
            return round((max(scores) + scores[-1]) / 2, 1)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(255))

    # Handling watching the Outcome score
    watching = db.relationship(
        "Outcome", 
        secondary="assignment_outcome", 
        backref=backref("alignment", uselist=False),
        uselist=False
    )

    # mastery = db.relationship(
    #     "UserAssignment",
    #     backref="assignment",
    # )
    
    def watch(self, outcome):
        if not self.is_watching(outcome):
            self.watching = outcome
            db.session.commit()
        else:
            raise AlignmentExistsException(f"Assignment {self.name} is aleady aligned to Outcome {outcome.name}.")
        
    def unwatch(self):
        self.watching = None
        db.session.commit()

    def is_watching(self, outcome):
        return self.watching is outcome


# One to many
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    source_uri = db.Column(db.String(255))
    method = db.Column(db.String(32))
    json_payload = db.Column(db.String(1000))
    occurred = db.Column(db.DateTime)


# Many to many

# TODO: Add attempt ID for a student?
class OutcomeAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_canvas_id = db.Column(db.Integer, db.ForeignKey("user.canvas_id", onupdate="CASCADE", ondelete="CASCADE"))
    outcome_canvas_id = db.Column(db.Integer, db.ForeignKey("outcome.canvas_id", onupdate="CASCADE", ondelete="CASCADE"))
    attempt_canvas_id = db.Column(db.Integer, unique=True, nullable=False)
    success = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    occurred = db.Column(db.DateTime)


class UserAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id", onupdate="CASCADE", ondelete="CASCADE"))
    score = db.Column(db.Integer)
    occurred = db.Column(db.DateTime)


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

