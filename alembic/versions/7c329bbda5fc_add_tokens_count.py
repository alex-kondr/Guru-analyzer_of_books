"""add tokens_count

Revision ID: 7c329bbda5fc
Revises: 558df6998045
Create Date: 2023-09-25 19:55:12.380869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c329bbda5fc'
down_revision = '558df6998045'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('tokens_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documents', 'tokens_count')
    # ### end Alembic commands ###
