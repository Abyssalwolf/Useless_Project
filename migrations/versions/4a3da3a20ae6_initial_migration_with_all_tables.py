"""Initial migration with all tables

Revision ID: 4a3da3a20ae6
Revises: 
Create Date: 2024-10-26 01:38:53.713340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a3da3a20ae6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=150), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.String(length=150), nullable=False),
    sa.Column('approver_id', sa.String(length=150), nullable=True),
    sa.Column('approved_by_user_2', sa.Boolean(), nullable=True),
    sa.Column('approved_by_user_3', sa.Boolean(), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('document')
    # ### end Alembic commands ###