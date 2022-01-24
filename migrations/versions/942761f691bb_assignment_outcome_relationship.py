"""assignment - outcome relationship

Revision ID: 942761f691bb
Revises: 914892f357c3
Create Date: 2021-09-16 13:13:16.648256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '942761f691bb'
down_revision = '914892f357c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assignment_outcome',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('outcome_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], name=op.f('fk_assignment_outcome_assignment_id_assignment'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['outcome_id'], ['outcome.id'], name=op.f('fk_assignment_outcome_outcome_id_outcome'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_assignment_outcome'))
    )
    with op.batch_alter_table('outcome', schema=None) as batch_op:
        batch_op.drop_constraint('fk_outcome_assignment_id_assignment', type_='foreignkey')
        batch_op.drop_column('assignment_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('outcome', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assignment_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_outcome_assignment_id_assignment', 'assignment', ['assignment_id'], ['id'])

    op.drop_table('assignment_outcome')
    # ### end Alembic commands ###
