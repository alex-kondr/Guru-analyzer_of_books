"""add tokens=0

Revision ID: 7a7d9e5e0dee
Revises: 541f9646698e
Create Date: 2023-09-26 14:33:22.867025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a7d9e5e0dee'
down_revision = '541f9646698e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('tokens_count', sa.Integer(), server_default=sa.text('0'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documents', 'tokens_count')
    # ### end Alembic commands ###
