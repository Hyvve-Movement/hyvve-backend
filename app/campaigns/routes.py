from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.campaigns.models import Campaign, Contribution
from app.campaigns.schemas import CampaignCreate, CampaignResponse, ContributionCreate, ContributionResponse, CampaignsActiveResponse, ContributionsListResponse

from app.core.database import get_session



router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_session)):
    db_campaign = Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_session)):
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@router.get("/campaigns/active", response_model=List[CampaignsActiveResponse])
def get_active_campaigns(db: Session = Depends(get_session)):
    db_campaigns = db.query(Campaign).filter(Campaign.is_active == True).all()
    return [CampaignsActiveResponse(
        campaign_id=campaign.id,
        title=campaign.title,
        description=campaign.description,
        is_active=campaign.is_active,
        expiration=campaign.expiration
    ) for campaign in db_campaigns]

@router.post("/contributions", response_model=ContributionResponse)
def submit_contribution(contribution: ContributionCreate, db: Session = Depends(get_session)):
    db_contribution = Contribution(**contribution.dict())
    db.add(db_contribution)
    db.commit()
    db.refresh(db_contribution)
    return db_contribution

@router.get("/contributions", response_model=ContributionsListResponse)
def get_contributions(campaign_id: Optional[str] = None, contributor: Optional[str] = None, db: Session = Depends(get_session)):
    query = db.query(Contribution)
    if campaign_id:
        query = query.filter(Contribution.campaign_id == campaign_id)
    if contributor:
        query = query.filter(Contribution.contributor == contributor)
    
    contributions = query.all()
    return ContributionsListResponse(contributions=[ContributionResponse(**contrib.__dict__) for contrib in contributions])


@router.get("/analytics/total-contributions")
def get_total_contributions(db: Session = Depends(get_session)):
    """
    Returns the total number of contributions.
    """
    total = db.query(Contribution).count()
    return {"total_contributions": total}

# Endpoint: Average Reputation Score
@router.get("/analytics/average-reputation")
def get_average_reputation(db: Session = Depends(get_session)):
    """
    Returns the average reputation score of contributors.
    Assumes the Contribution model has a 'reputation_score' field.
    """
    avg_rep = db.query(func.avg(Contribution.reputation_score)).scalar()
    return {"average_reputation": avg_rep}

# Endpoint: Average AI Verification Score
@router.get("/analytics/average-ai-verification")
def get_average_ai_verification(db: Session = Depends(get_session)):
    """
    Returns the average AI verification score.
    Assumes the Contribution model has an 'ai_verification_score' field.
    """
    avg_ai = db.query(func.avg(Contribution.ai_verification_score)).scalar()
    return {"average_ai_verification": avg_ai}

# Endpoint: Total Rewards Paid
@router.get("/analytics/total-rewards-paid")
def get_total_rewards_paid(db: Session = Depends(get_session)):
    """
    Returns the total number of rewards paid.
    It is assumed that a reward is considered paid when 'reward_claimed' is True.
    """
    total_paid = db.query(Contribution).filter(Contribution.reward_claimed == True).count()
    return {"total_rewards_paid": total_paid}

# Endpoint: Campaigns Created by a Wallet
@router.get("/wallet/{wallet_id}/campaigns/created", response_model=List[CampaignResponse])
def get_campaigns_created(wallet_id: str, db: Session = Depends(get_session)):
    """
    Returns all campaigns created by the wallet specified by wallet_id.
    Assumes the Campaign model has a 'creator_wallet' field.
    """
    campaigns = db.query(Campaign).filter(Campaign.creator_wallet == wallet_id).all()
    if not campaigns:
        raise HTTPException(status_code=404, detail="No campaigns found for this wallet.")
    return campaigns

# Endpoint: Campaigns Contributed to by a Wallet
@router.get("/wallet/{wallet_id}/campaigns/contributed", response_model=List[CampaignResponse])
def get_campaigns_contributed(wallet_id: str, db: Session = Depends(get_session)):
    """
    Returns all campaigns to which the wallet (contributor) has contributed.
    Retrieves contributions made by the wallet, extracts unique campaign IDs,
    and then returns the corresponding campaigns.
    """
    contributions = db.query(Contribution).filter(Contribution.contributor == wallet_id).all()
    campaign_ids = list({contribution.campaign_id for contribution in contributions})
    if not campaign_ids:
        raise HTTPException(status_code=404, detail="No contributions found for this wallet.")
    campaigns = db.query(Campaign).filter(Campaign.id.in_(campaign_ids)).all()
    return campaigns