"""add points possible to assignment

Revision ID: 03fb465c701d
Revises: 3a5ff2fefbfa
Create Date: 2022-02-25 14:19:28.977428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03fb465c701d'
down_revision = '3a5ff2fefbfa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('points_possible', sa.Float(), nullable=True))

    with op.batch_alter_table('user_assignment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_assignment_assignment_id_assignment', type_='foreignkey')
        batch_op.drop_constraint('fk_user_assignment_user_id_user', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_user_assignment_assignment_id_assignment'), 'assignment', ['assignment_id'], ['canvas_id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_user_assignment_user_id_user'), 'user', ['user_id'], ['canvas_id'], onupdate='CASCADE', ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_assignment', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_user_assignment_user_id_user'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_user_assignment_assignment_id_assignment'), type_='foreignkey')
        batch_op.create_foreign_key('fk_user_assignment_user_id_user', 'user', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.create_foreign_key('fk_user_assignment_assignment_id_assignment', 'assignment', ['assignment_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.drop_column('points_possible')

    # ### end Alembic commands ###
