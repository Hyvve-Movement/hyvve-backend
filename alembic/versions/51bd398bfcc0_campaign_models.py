"""campaign models

Revision ID: 51bd398bfcc0
Revises: 
Create Date: 2025-02-22 18:15:57.555761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51bd398bfcc0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('campaign_generated_id', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
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
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_campaign_generated_id'), 'campaigns', ['campaign_generated_id'], unique=False)
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_title'), 'campaigns', ['title'], unique=False)
    op.create_table('contributions',
    sa.Column('contribution_id', sa.String(), nullable=False),
    sa.Column('campaign_id', sa.String(), nullable=False),
    sa.Column('contributor', sa.String(), nullable=True),
    sa.Column('data_url', sa.String(), nullable=True),
    sa.Column('data_hash', sa.String(), nullable=True),
    sa.Column('signature', sa.String(), nullable=True),
    sa.Column('transaction_hash', sa.String(), nullable=True),
    sa.Column('quality_score', sa.Integer(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('reward_claimed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('contribution_id'),
    sa.UniqueConstraint('campaign_id')
    )
    op.create_index(op.f('ix_contributions_contribution_id'), 'contributions', ['contribution_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contributions_contribution_id'), table_name='contributions')
    op.drop_table('contributions')
    op.drop_index(op.f('ix_campaigns_title'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_campaign_generated_id'), table_name='campaigns')
    op.drop_table('campaigns')
    # ### end Alembic commands ###
