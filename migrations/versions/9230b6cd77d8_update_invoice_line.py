"""update invoice line

Revision ID: 9230b6cd77d8
Revises: 0618a3eea808
Create Date: 2025-04-27 08:37:06.052086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9230b6cd77d8'
down_revision = '0618a3eea808'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice_lines', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice_lines', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###
