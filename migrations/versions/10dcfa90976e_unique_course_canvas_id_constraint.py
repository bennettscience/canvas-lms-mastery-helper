"""unique course canvas_id constraint

Revision ID: 10dcfa90976e
Revises: 242679cd3bc1
Create Date: 2021-09-24 13:37:26.463833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10dcfa90976e'
down_revision = '242679cd3bc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_course_canvas_id'), ['canvas_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_course_canvas_id'), type_='unique')

    # ### end Alembic commands ###
