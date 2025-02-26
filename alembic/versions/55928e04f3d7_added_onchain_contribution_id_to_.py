"""added onchain contribution id to contribution model

Revision ID: 55928e04f3d7
Revises: c9a8b8123913
Create Date: 2025-02-26 19:44:00.088624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55928e04f3d7'
down_revision: Union[str, None] = 'c9a8b8123913'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contributions', sa.Column('onchain_contribution_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_contributions_onchain_contribution_id'), 'contributions', ['onchain_contribution_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contributions_onchain_contribution_id'), table_name='contributions')
    op.drop_column('contributions', 'onchain_contribution_id')
    # ### end Alembic commands ###
