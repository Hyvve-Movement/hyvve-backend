from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

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
    db_campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@router.get("/campaigns/active", response_model=List[CampaignsActiveResponse])
def get_active_campaigns(db: Session = Depends(get_session)):
    db_campaigns = db.query(Campaign).filter(Campaign.is_active == True).all()
    return [CampaignsActiveResponse(
        campaign_id=campaign.campaign_id,
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