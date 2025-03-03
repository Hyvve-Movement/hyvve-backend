"""updated the model

Revision ID: 11935ef26e38
Revises: fe269c6a3c1d
Create Date: 2025-02-23 00:51:09.390574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11935ef26e38'
down_revision: Union[str, None] = 'fe269c6a3c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campaigns', sa.Column('onchain_campaign_id', sa.String(), nullable=True))
    op.drop_index('ix_campaigns_campaign_generated_id', table_name='campaigns')
    op.create_index(op.f('ix_campaigns_onchain_campaign_id'), 'campaigns', ['onchain_campaign_id'], unique=False)
    op.drop_column('campaigns', 'campaign_generated_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campaigns', sa.Column('campaign_generated_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_campaigns_onchain_campaign_id'), table_name='campaigns')
    op.create_index('ix_campaigns_campaign_generated_id', 'campaigns', ['campaign_generated_id'], unique=False)
    op.drop_column('campaigns', 'onchain_campaign_id')
    # ### end Alembic commands ###
