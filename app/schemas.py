from marshmallow import fields, Schema


class UserPrefsSchema(Schema):
    id = fields.Int(dump_only=True)
    score_calculation_method = fields.Str()
    mastery_score = fields.Float()


class UserLoginSchema(Schema):
    id = fields.Int()

    
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    canvas_id = fields.Int(dump_only=True)
    user_type = fields.Str()
    email = fields.Str()
    enrollments = fields.List(fields.Nested("CourseSchema"))
    preferences = fields.Nested(UserPrefsSchema)
    scores = fields.List(fields.Nested("OutcomeScore"))


class OutcomeScore(Schema):
    outcome_canvas_id = fields.Int()
    score = fields.Str()


class CourseSchema(Schema):
    type = fields.Str(dump_default='course')
    id = fields.Int(dump_only=True)
    canvas_id = fields.Int()
    name = fields.Str()
    outcomes = fields.List(fields.Nested("OutcomeListSchema"), dump_only=True)
    assignments = fields.List(fields.Nested(lambda: AssignmentSchema(exclude=('watching',))))
    term_name = fields.Str()
    term_id = fields.Int()

class UserAssignment(Schema):
    id = fields.Int(dump_only=True)
    user = fields.Nested(UserSchema)
    assignment = fields.Nested("AssignmentSchema")
    score = fields.Int()
    occurred = fields.DateTime()


class CreateAssignmentSchema(Schema):
    canvas_id = fields.Int(required=True)
    course_id = fields.Int(required=True)
    name = fields.Str(required=True)
    points_possible = fields.Int(requried=True)


class AssignmentSchema(Schema):
    type = fields.Str(dump_default='assignment')
    id = fields.Int(dump_only=True)
    canvas_id = fields.Int()
    name = fields.Str()
    watching = fields.Nested(lambda: OutcomeListSchema(only=('id', 'name',)), dump_only=True)
    mastery = fields.Nested(UserAssignment(exclude=('assignment','user')))


class CanvasSyncServiceOutcome(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)


class OutcomeListSchema(Schema):
    type = fields.Str(dump_default='outcome')
    id = fields.Int(dump_only=True)
    name = fields.Str()
    canvas_id = fields.Int()
    alignment = fields.Nested(AssignmentSchema(exclude=("watching", "mastery")))
    score = fields.Float(dump_only=True)


class OutcomeSchema(Schema):
    type = fields.Str(dump_default='outcome')
    id = fields.Int(dump_only=True)
    name = fields.Str()
    canvas_id = fields.Int()
    alignment = fields.Nested(AssignmentSchema(exclude=("watching", "mastery")))
    score = fields.Float(dump_only=True)


class OutcomeAttemptSchema(Schema):
    id = fields.Int(dump_only=True)
    success = fields.Bool()
    score = fields.Float()
    occurred = fields.DateTime()
    assignments = fields.List(fields.Nested(lambda: AssignmentSchema(exclude=('watching',))))