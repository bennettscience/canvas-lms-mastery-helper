"""add oauth login

Revision ID: 14deba3e45c3
Revises: 7848d1d48dbb
Create Date: 2022-02-04 11:08:11.167779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14deba3e45c3'
down_revision = '7848d1d48dbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_outcome_attempt')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('expiration', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('refresh_token', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('refresh_token')
        batch_op.drop_column('expiration')
        batch_op.drop_column('token')

    op.create_table('_alembic_tmp_outcome_attempt',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('success', sa.BOOLEAN(), nullable=True),
    sa.Column('score', sa.INTEGER(), nullable=True),
    sa.Column('occurred', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('attempt_id', sa.INTEGER(), nullable=False),
    sa.Column('outcome_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['outcome_id'], ['outcome.canvas_id'], name='fk_outcome_attempt_outcome_id_outcome', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.canvas_id'], name='fk_outcome_attempt_user_id_user', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='pk_outcome_attempt'),
    sa.UniqueConstraint('attempt_id', name='uq_outcome_attempt_attempt_id')
    )
    # ### end Alembic commands ###