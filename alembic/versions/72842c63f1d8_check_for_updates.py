"""check for updates

Revision ID: 72842c63f1d8
Revises: 55928e04f3d7
Create Date: 2025-02-28 06:05:28.442924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72842c63f1d8'
down_revision: Union[str, None] = '55928e04f3d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('onchain_campaign_id', sa.String(), nullable=True),
    sa.Column('creator_wallet_address', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('campaign_type', sa.String(), nullable=True),
    sa.Column('data_requirements', sa.String(), nullable=True),
    sa.Column('quality_criteria', sa.String(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=True),
    sa.Column('total_budget', sa.Float(), nullable=True),
    sa.Column('min_data_count', sa.Integer(), nullable=True),
    sa.Column('max_data_count', sa.Integer(), nullable=True),
    sa.Column('expiration', sa.Integer(), nullable=True),
    sa.Column('metadata_uri', sa.String(), nullable=True),
    sa.Column('transaction_hash', sa.String(), nullable=True),
    sa.Column('platform_fee', sa.Float(), nullable=True),
    sa.Column('is_premium', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('current_activity_level', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_campaign_type'), 'campaigns', ['campaign_type'], unique=False)
    op.create_index(op.f('ix_campaigns_creator_wallet_address'), 'campaigns', ['creator_wallet_address'], unique=False)
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_is_premium'), 'campaigns', ['is_premium'], unique=False)
    op.create_index(op.f('ix_campaigns_onchain_campaign_id'), 'campaigns', ['onchain_campaign_id'], unique=False)
    op.create_index(op.f('ix_campaigns_title'), 'campaigns', ['title'], unique=False)
    op.create_table('contributions',
    sa.Column('contribution_id', sa.String(), nullable=False),
    sa.Column('onchain_contribution_id', sa.String(), nullable=True),
    sa.Column('campaign_id', sa.String(), nullable=False),
    sa.Column('contributor', sa.String(), nullable=True),
    sa.Column('data_url', sa.String(), nullable=True),
    sa.Column('transaction_hash', sa.String(), nullable=True),
    sa.Column('ai_verification_score', sa.Float(), nullable=True),
    sa.Column('reputation_score', sa.Float(), nullable=True),
    sa.Column('quality_score', sa.Integer(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('reward_claimed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('contribution_id')
    )
    op.create_index(op.f('ix_contributions_contribution_id'), 'contributions', ['contribution_id'], unique=False)
    op.create_index(op.f('ix_contributions_contributor'), 'contributions', ['contributor'], unique=False)
    op.create_index(op.f('ix_contributions_onchain_contribution_id'), 'contributions', ['onchain_contribution_id'], unique=False)
    op.create_table('activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('campaign_id', sa.String(), nullable=False),
    sa.Column('contribution_id', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('activity_level', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.ForeignKeyConstraint(['contribution_id'], ['contributions.contribution_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_id'), 'activity', ['id'], unique=False)
    op.create_index(op.f('ix_activity_timestamp'), 'activity', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_activity_timestamp'), table_name='activity')
    op.drop_index(op.f('ix_activity_id'), table_name='activity')
    op.drop_table('activity')
    op.drop_index(op.f('ix_contributions_onchain_contribution_id'), table_name='contributions')
    op.drop_index(op.f('ix_contributions_contributor'), table_name='contributions')
    op.drop_index(op.f('ix_contributions_contribution_id'), table_name='contributions')
    op.drop_table('contributions')
    op.drop_index(op.f('ix_campaigns_title'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_onchain_campaign_id'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_is_premium'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_creator_wallet_address'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_campaign_type'), table_name='campaigns')
    op.drop_table('campaigns')
    # ### end Alembic commands ###
