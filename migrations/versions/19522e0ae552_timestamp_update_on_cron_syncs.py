"""timestamp update on cron syncs

Revision ID: 19522e0ae552
Revises: 14deba3e45c3
Create Date: 2022-02-07 12:49:09.893609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19522e0ae552'
down_revision = '14deba3e45c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_column('updated_at')

    # ### end Alembic commands ###