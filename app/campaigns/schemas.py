from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CampaignCreate(BaseModel):
    onchain_campaign_id: str
    title: str
    description: str
    data_requirements: str
    quality_criteria: str
    unit_price: float
    campaign_type: str
    total_budget: float
    min_data_count: int
    max_data_count: int
    expiration: int  # Unix timestamp
    metadata_uri: str
    transaction_hash: str
    platform_fee: float

class CampaignResponse(CampaignCreate):
    campaign_id: str
    is_active: bool
    created_at: datetime

class ContributionCreate(BaseModel):
    contribution_id: str
    campaign_id: str
    contributor: str
    data_url: str
    data_hash: str
    signature: str
    transaction_hash: str
    quality_score: int
    ai_verification_score: Optional[float] = None  # New field for AI verification score
    reputation_score: Optional[float] = None         # New field for contributor's reputation

class ContributionResponse(ContributionCreate):
    is_verified: bool
    reward_claimed: bool
    created_at: datetime

class CampaignsActiveResponse(BaseModel):
    campaign_id: str
    title: str
    description: str
    is_active: bool
    expiration: int

class ContributionsListResponse(BaseModel):
    contributions: List[ContributionResponse]
