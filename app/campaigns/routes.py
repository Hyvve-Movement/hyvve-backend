from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.campaigns.models import Campaign, Contribution
from app.campaigns.schemas import CampaignCreate, CampaignResponse, ContributionCreate, ContributionResponse, CampaignsActiveResponse, ContributionsListResponse
from app.campaigns.services import serialize_campaign
from app.core.database import get_session



router = APIRouter()

@router.get("/all", response_model=List[CampaignResponse])
def get_all_campaigns(db: Session = Depends(get_session)):
    db_campaigns = (
        db.query(Campaign)
        .options(joinedload(Campaign.contributions))
        .order_by(Campaign.created_at.desc())
        .all()
    )
    return [
        serialize_campaign(campaign, len(campaign.contributions))
        for campaign in db_campaigns
    ]


@router.get(
    "/{creator_wallet_address}/campaigns/created", 
    response_model=List[CampaignResponse],
    summary="Get all campaigns created by a creator wallet address"
)
def get_campaigns_created_by_wallet(
    creator_wallet_address: str, 
    db: Session = Depends(get_session)
):
    """
    Retrieve all campaigns created by the specified creator_wallet_address.
    Each campaign is serialized using the serialize_campaign function.
    """
    campaigns = db.query(Campaign).filter(
        Campaign.creator_wallet_address == creator_wallet_address
    ).all()

    if not campaigns:
        raise HTTPException(
            status_code=404, 
            detail="No campaigns found for the given creator wallet address."
        )
    
    # Serialize each campaign and include the current contributions count.
    return [
        serialize_campaign(campaign, len(campaign.contributions))
        for campaign in campaigns
    ]


@router.post("/create-campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_session)):
    db_campaign = Campaign(**campaign.dict())
    db_campaign.is_active = True
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    # A new campaign has no contributions yet
    contributions_count = 0
    return serialize_campaign(db_campaign, contributions_count)


@router.get("/active", response_model=List[CampaignsActiveResponse])
def get_active_campaigns(db: Session = Depends(get_session)):
    db_campaigns = (
        db.query(Campaign)
        .options(joinedload(Campaign.contributions))
        .filter(Campaign.is_active == True)
        .all()
    )
    return [
        CampaignsActiveResponse(
            campaign_id=campaign.id,
            onchain_campaign_id=str(campaign.onchain_campaign_id),
            creator_wallet_address=str(campaign.creator_wallet_address),
            unit_price=campaign.unit_price,
            total_budget=float(campaign.total_budget),
            max_data_count=int(campaign.max_data_count),
            current_contributions=int(len(campaign.contributions)),
            title=campaign.title,
            description=campaign.description,
            is_active=campaign.is_active,
            expiration=campaign.expiration
        )
        for campaign in db_campaigns
    ]

@router.get("/{onchain_campaign_id}", response_model=CampaignResponse)
def get_campaign(onchain_campaign_id: str, db: Session = Depends(get_session)):
    db_campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    contributions_count = db.query(Contribution).filter(Contribution.campaign_id == db_campaign.id).count()
    return serialize_campaign(db_campaign, contributions_count)



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
    # Assuming ContributionResponse matches the Contribution model fields.
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


@router.get("/analytics/peak-activity/{onchain_campaign_id}")
def get_peak_activity_hours(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Calculate the peak activity hours for a particular campaign.
    Returns the hour(s) of the day (0-23) with the highest submission counts and the corresponding count.
    """
    # Retrieve the campaign
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Group contributions for the campaign by the hour (using the created_at timestamp)
    results = (
        db.query(
            func.extract('hour', Contribution.created_at).label("hour"),
            func.count(Contribution.contribution_id).label("count")
        )
        .filter(Contribution.campaign_id == campaign.id)
        .group_by("hour")
        .all()
    )

    if not results:
        return {"peak_hours": [], "max_submissions": 0}

    # Determine the maximum submission count
    max_count = max(r.count for r in results)
    # Find all hours that have this maximum count
    peak_hours = [int(r.hour) for r in results if r.count == max_count]

    return {"peak_hours": peak_hours, "max_submissions": max_count}


@router.get("/analytics/top-contributors/{onchain_campaign_id}")
def get_top_contributors(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Retrieve the top contributors for a particular campaign, ordered by number of submissions (top 10).
    """
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    results = (
        db.query(
            Contribution.contributor,
            func.count(Contribution.contribution_id).label("submissions")
        )
        .filter(Contribution.campaign_id == campaign.id)
        .group_by(Contribution.contributor)
        .order_by(func.count(Contribution.contribution_id).desc())
        .limit(10)
        .all()
    )

    return [{"contributor": r.contributor, "submissions": r.submissions} for r in results]


@router.get("/analytics/unique-contributors/{onchain_campaign_id}")
def get_unique_contributor_count(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Get the unique contributor count for a particular campaign.
    """
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    unique_count = (
        db.query(func.count(func.distinct(Contribution.contributor)))
        .filter(Contribution.campaign_id == campaign.id)
        .scalar()
    )
    return {"unique_contributor_count": unique_count}


@router.get("/analytics/average-cost/{onchain_campaign_id}")
def get_average_cost_per_submission(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Calculate the average cost per submission for a particular campaign.
    The calculation is based on the campaign's total budget divided by the total number of contributions.
    If there are no submissions, return 0.
    """
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    submissions_count = (
        db.query(Contribution)
        .filter(Contribution.campaign_id == campaign.id)
        .count()
    )
    
    avg_cost = float(campaign.total_budget) / submissions_count if submissions_count > 0 else 0
    return {"average_cost_per_submission": avg_cost}



@router.get("/analytics/average-reputation/{wallet_address}")
def get_average_reputation(wallet_address: str, db: Session = Depends(get_session)):
    """
    Calculate the average reputation score for a given contributor (by wallet address)
    as the total reputation score divided by the number of contributions made by the user.
    """
    total_rep = (
        db.query(func.sum(Contribution.reputation_score))
        .filter(Contribution.contributor == wallet_address)
        .scalar()
    ) or 0

    contrib_count = (
        db.query(func.count(Contribution.contribution_id))
        .filter(Contribution.contributor == wallet_address)
        .scalar()
    ) or 0

    avg_rep = total_rep / contrib_count if contrib_count > 0 else 0

    return {"average_reputation": avg_rep}



@router.get("/analytics/total-submissions/{wallet_address}")
def get_total_submissions(wallet_address: str, db: Session = Depends(get_session)):
    """
    Get the total number of submissions from a contributor across all campaigns.
    """
    total = (
        db.query(Contribution)
        .filter(Contribution.contributor == wallet_address)
        .count()
    )
    return {"total_submissions": total}


@router.get("/analytics/leaderboard/global")
def get_global_leaderboard(db: Session = Depends(get_session)):
    """
    Get the leader board of top 10 contributors across all campaigns, ranked by number of submissions.
    """
    results = (
        db.query(
            Contribution.contributor,
            func.count(Contribution.contribution_id).label("submissions")
        )
        .group_by(Contribution.contributor)
        .order_by(func.count(Contribution.contribution_id).desc())
        .limit(10)
        .all()
    )
    return [{"contributor": r.contributor, "submissions": r.submissions} for r in results]


@router.get("/analytics/leaderboard/{onchain_campaign_id}")
def get_campaign_leaderboard(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Get the leader board of top 10 contributors for a particular campaign,
    ranked by the number of submissions.
    """
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    results = (
        db.query(
            Contribution.contributor,
            func.count(Contribution.contribution_id).label("submissions")
        )
        .filter(Contribution.campaign_id == campaign.id)
        .group_by(Contribution.contributor)
        .order_by(func.count(Contribution.contribution_id).desc())
        .limit(10)
        .all()
    )
    return [{"contributor": r.contributor, "submissions": r.submissions} for r in results]


# Endpoint: Campaigns Created by a Wallet
@router.get("/wallet/{wallet_address}/campaigns/created", response_model=List[CampaignResponse])
def get_campaigns_created(wallet_address: str, db: Session = Depends(get_session)):
    """
    Returns all campaigns created by the wallet specified by wallet_address.
    Assumes the Campaign model has a 'creator_wallet' field.
    """
    campaigns = db.query(Campaign).filter(Campaign.creator_wallet_address == wallet_address).all()
    if not campaigns:
        raise HTTPException(status_code=404, detail="No campaigns found for this wallet.")
    return campaigns

# Endpoint: Campaigns Contributed to by a Wallet
@router.get("/wallet/{wallet_address}/campaigns/contributed", response_model=List[CampaignResponse])
def get_campaigns_contributed(wallet_address: str, db: Session = Depends(get_session)):
    """
    Returns all campaigns to which the wallet (contributor) has contributed.
    Retrieves contributions made by the wallet, extracts unique campaign IDs,
    and then returns the corresponding campaigns.
    """
    contributions = db.query(Contribution).filter(Contribution.contributor == wallet_address).all()
    campaign_ids = list({contribution.campaign_id for contribution in contributions})
    if not campaign_ids:
        raise HTTPException(status_code=404, detail="No contributions found for this wallet.")
    campaigns = db.query(Campaign).filter(Campaign.id.in_(campaign_ids)).all()
    return campaigns