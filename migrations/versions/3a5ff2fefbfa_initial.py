"""initial

Revision ID: 3a5ff2fefbfa
Revises: 
Create Date: 2022-02-15 14:05:33.995110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a5ff2fefbfa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canvas_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_assignment')),
    sa.UniqueConstraint('canvas_id', name=op.f('uq_assignment_canvas_id'))
    )
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canvas_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_course')),
    sa.UniqueConstraint('canvas_id', name=op.f('uq_course_canvas_id'))
    )
    op.create_table('outcome',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canvas_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outcome')),
    sa.UniqueConstraint('canvas_id', name=op.f('uq_outcome_canvas_id'))
    )
    op.create_table('user_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_type'))
    )
    op.create_table('assignment_outcome',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('outcome_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], name=op.f('fk_assignment_outcome_assignment_id_assignment'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['outcome_id'], ['outcome.id'], name=op.f('fk_assignment_outcome_outcome_id_outcome'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_assignment_outcome'))
    )
    op.create_table('course_assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('assignmend_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assignmend_id'], ['assignment.id'], name=op.f('fk_course_assignments_assignmend_id_assignment'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], name=op.f('fk_course_assignments_course_id_course'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_course_assignments'))
    )
    op.create_table('course_outcomes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('outcome_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], name=op.f('fk_course_outcomes_course_id_course'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['outcome_id'], ['outcome.id'], name=op.f('fk_course_outcomes_outcome_id_outcome'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_course_outcomes'))
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canvas_id', sa.Integer(), nullable=True),
    sa.Column('usertype_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('token', sa.String(length=255), nullable=True),
    sa.Column('expiration', sa.Integer(), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['usertype_id'], ['user_type.id'], name=op.f('fk_user_usertype_id_user_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('canvas_id', name=op.f('uq_user_canvas_id'))
    )
    op.create_table('log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('source_uri', sa.String(length=255), nullable=True),
    sa.Column('method', sa.String(length=32), nullable=True),
    sa.Column('json_payload', sa.String(length=1000), nullable=True),
    sa.Column('occurred', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_log_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_log'))
    )
    op.create_table('outcome_attempt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_canvas_id', sa.Integer(), nullable=True),
    sa.Column('outcome_canvas_id', sa.Integer(), nullable=True),
    sa.Column('attempt_canvas_id', sa.Integer(), nullable=False),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('occurred', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['outcome_canvas_id'], ['outcome.canvas_id'], name=op.f('fk_outcome_attempt_outcome_canvas_id_outcome'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_canvas_id'], ['user.canvas_id'], name=op.f('fk_outcome_attempt_user_canvas_id_user'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outcome_attempt')),
    sa.UniqueConstraint('attempt_canvas_id', name=op.f('uq_outcome_attempt_attempt_canvas_id'))
    )
    op.create_table('user_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('occurred', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], name=op.f('fk_user_assignment_assignment_id_assignment'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_assignment_user_id_user'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_assignment'))
    )
    op.create_table('user_courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], name=op.f('fk_user_courses_course_id_course'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_courses_user_id_user'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_courses'))
    )
    op.create_table('user_preferences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('score_calculation_method', sa.Enum('AVERAGE', 'DECAYING_AVERAGE', 'HIGHEST', 'HIGH_LAST_AVERAGE', 'MODE', name='masterycalculation'), nullable=True),
    sa.Column('mastery_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_preferences_user_id_user'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_preferences'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_preferences')
    op.drop_table('user_courses')
    op.drop_table('user_assignment')
    op.drop_table('outcome_attempt')
    op.drop_table('log')
    op.drop_table('user')
    op.drop_table('course_outcomes')
    op.drop_table('course_assignments')
    op.drop_table('assignment_outcome')
    op.drop_table('user_type')
    op.drop_table('outcome')
    op.drop_table('course')
    op.drop_table('assignment')
    # ### end Alembic commands ###
