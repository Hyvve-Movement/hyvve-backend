from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.campaigns.models import Campaign, Contribution
from app.campaigns.schemas import CampaignCreate, CampaignResponse, ContributionCreate, ContributionResponse, CampaignsActiveResponse, ContributionsListResponse, WalletCampaignsResponse
from app.campaigns.services import serialize_campaign
from app.core.database import get_session



router = APIRouter()

# @router.delete("/campaigns/{campaign_id}", summary="Delete a campaign by its ID", response_model=dict)
# def delete_campaign(campaign_id: str, db: Session = Depends(get_session)):
#     """
#     Delete the campaign with the given campaign_id.
#     """
#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
    
#     db.delete(campaign)
#     db.commit()
#     return {"detail": "Campaign deleted successfully"}


@router.get("/all", response_model=List[CampaignResponse])
def get_all_campaigns(db: Session = Depends(get_session)):
    db_campaigns = (
        db.query(Campaign)
        .options(joinedload(Campaign.contributions))
        .order_by(Campaign.created_at.desc())
        .all()
    )
    result = []
    for campaign in db_campaigns:
        contributions_count = len(campaign.contributions)
        unique_count = db.query(func.count(func.distinct(Contribution.contributor))) \
                         .filter(Contribution.campaign_id == campaign.id).scalar()
        # Extend the serialized campaign with the unique contributions count.
        serialized = serialize_campaign(campaign, contributions_count)
        serialized["unique_contributions_count"] = unique_count
        result.append(serialized)
    return result


@router.get(
    "/{creator_wallet_address}/campaigns/created", 
    response_model=List[CampaignResponse],
    summary="Get all campaigns created by a creator wallet address"
)
def get_campaigns_created_by_wallet(
    creator_wallet_address: str, 
    db: Session = Depends(get_session)
):
    campaigns = (
        db.query(Campaign)
        .filter(Campaign.creator_wallet_address == creator_wallet_address)
        .options(joinedload(Campaign.contributions))
        .order_by(Campaign.created_at.desc())
        .all()
    )
    if not campaigns:
        raise HTTPException(
            status_code=404, 
            detail="No campaigns found for the given creator wallet address."
        )
    
    result = []
    for campaign in campaigns:
        contributions_count = len(campaign.contributions)
        unique_count = db.query(func.count(func.distinct(Contribution.contributor))) \
                         .filter(Contribution.campaign_id == campaign.id).scalar()
        serialized = serialize_campaign(campaign, contributions_count)
        serialized["unique_contributions_count"] = unique_count
        result.append(serialized)
    return result


@router.post("/create-campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_session)):
    db_campaign = Campaign(**campaign.dict())
    db_campaign.is_active = True
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    # New campaign: no contributions, so both counts are 0.
    return {**serialize_campaign(db_campaign, 0), "unique_contributions_count": 0}


@router.get("/active", response_model=List[CampaignsActiveResponse])
def get_active_campaigns(db: Session = Depends(get_session)):
    db_campaigns = (
        db.query(Campaign)
        .options(joinedload(Campaign.contributions))
        .order_by(Campaign.created_at.desc())
        .filter(Campaign.is_active == True)
        .all()
    )
    result = []
    for campaign in db_campaigns:
        unique_count = db.query(func.count(func.distinct(Contribution.contributor))) \
                         .filter(Contribution.campaign_id == campaign.id).scalar()
        result.append({
            "campaign_id": campaign.id,
            "onchain_campaign_id": str(campaign.onchain_campaign_id),
            "creator_wallet_address": str(campaign.creator_wallet_address),
            "unit_price": campaign.unit_price,
            "total_budget": float(campaign.total_budget),
            "max_data_count": int(campaign.max_data_count),
            "current_contributions": len(campaign.contributions),
            "unique_contributions_count": unique_count,
            "title": campaign.title,
            "description": campaign.description,
            "is_active": campaign.is_active,
            "expiration": campaign.expiration
        })
    return result


@router.get("/{onchain_campaign_id}", response_model=CampaignResponse)
def get_campaign(onchain_campaign_id: str, db: Session = Depends(get_session)):
    db_campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    contributions_count = db.query(Contribution).filter(Contribution.campaign_id == db_campaign.id).count()
    unique_count = db.query(func.count(func.distinct(Contribution.contributor))) \
                     .filter(Contribution.campaign_id == db_campaign.id).scalar()
    serialized = serialize_campaign(db_campaign, contributions_count)
    serialized["unique_contributions_count"] = unique_count
    return serialized



@router.post("/submit-contributions", response_model=ContributionResponse)
def submit_contribution(contribution: ContributionCreate, db: Session = Depends(get_session)):
    # Look up the campaign by its onchain_campaign_id
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == contribution.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found for given campaign_id")
    
    # Replace the submitted campaign_id (onchain_campaign_id) with the internal campaign id
    contribution_data = contribution.dict()
    contribution_data["campaign_id"] = campaign.id
    
    # Create and insert the contribution
    db_contribution = Contribution(**contribution_data)
    db.add(db_contribution)
    db.commit()
    db.refresh(db_contribution)
    return db_contribution



@router.get("/get-contributions", response_model=ContributionsListResponse)
def get_contributions(
    campaign_id: Optional[str] = None, 
    contributor: Optional[str] = None, 
    db: Session = Depends(get_session)
):
    query = db.query(Contribution)

    if campaign_id:
        query = query.filter(Contribution.campaign_id == campaign_id)
    if contributor:
        query = query.filter(Contribution.contributor == contributor)
    
    query = query.order_by(Contribution.created_at.desc())
    contributions = query.all()

    # Calculate unique contributions (based on unique contributor)
    unique_contributors = {contrib.contributor for contrib in contributions}
    unique_count = len(unique_contributors)

    return ContributionsListResponse(
        contributions=[ContributionResponse(**contrib.__dict__) for contrib in contributions],
        unique_contributions_count=unique_count
    )


@router.get("/wallet/{wallet_address}/campaign-details", response_model=WalletCampaignsResponse, summary="Get campaigns created and contributed to by a wallet")
def get_wallet_campaigns_details(wallet_address: str, db: Session = Depends(get_session)):
    """
    Returns all campaigns related to the given wallet address. 
    This includes:
      - Campaigns created by the wallet (where the wallet is the creator)
      - Campaigns the wallet has contributed to (where the wallet appears in contributions)
    Each campaign is serialized using serialize_campaign and includes the unique_contributions_count.
    """
    # Campaigns created by the wallet
    created_campaigns = (
        db.query(Campaign)
        .filter(Campaign.creator_wallet_address == wallet_address)
        .options(joinedload(Campaign.contributions))
        .order_by(Campaign.created_at.desc())
        .all()
    )
    created_serialized = []
    for campaign in created_campaigns:
        contributions_count = len(campaign.contributions)
        unique_count = db.query(func.count(func.distinct(Contribution.contributor)))\
                         .filter(Contribution.campaign_id == campaign.id).scalar()
        serialized = serialize_campaign(campaign, contributions_count)
        serialized["unique_contributions_count"] = unique_count
        created_serialized.append(serialized)

    # Campaigns contributed to by the wallet
    contributions = db.query(Contribution).filter(Contribution.contributor == wallet_address).all()
    campaign_ids = list({contribution.campaign_id for contribution in contributions})
    contributed_serialized = []
    if campaign_ids:
        contributed_campaigns = db.query(Campaign).filter(Campaign.id.in_(campaign_ids)).all()
        for campaign in contributed_campaigns:
            contributions_count = len(campaign.contributions)
            unique_count = db.query(func.count(func.distinct(Contribution.contributor)))\
                             .filter(Contribution.campaign_id == campaign.id).scalar()
            serialized = serialize_campaign(campaign, contributions_count)
            serialized["unique_contributions_count"] = unique_count
            contributed_serialized.append(serialized)
    
    return {
        "created": created_serialized,
        "contributed": contributed_serialized
    }





@router.get("/analytics/campaign/{onchain_campaign_id}")
def get_campaign_analytics(onchain_campaign_id: str, db: Session = Depends(get_session)):
    """
    Returns analytics for a given campaign identified by onchain_campaign_id, including:
      - Total contributions
      - Average cost per submission (campaign total_budget / number of contributions)
      - Peak activity hours (hour(s) with highest submission counts)
      - Top 10 contributors for that campaign
      - Unique contributor count
      - Total rewards paid
    """
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Total contributions
    total_contribs = db.query(Contribution).filter(Contribution.campaign_id == campaign.id).count()

    # Average cost per submission (if no contributions, return 0)
    avg_cost = float(campaign.total_budget) / total_contribs if total_contribs > 0 else 0

    # Peak activity hours (group contributions by hour)
    peak_results = (
        db.query(
            func.extract('hour', Contribution.created_at).label("hour"),
            func.count(Contribution.contribution_id).label("count")
        )
        .filter(Contribution.campaign_id == campaign.id)
        .group_by("hour")
        .all()
    )
    if peak_results:
        max_count = max(r.count for r in peak_results)
        peak_hours = [int(r.hour) for r in peak_results if r.count == max_count]
    else:
        max_count = 0
        peak_hours = []

    # Top 10 contributors for this campaign
    top_contributors_q = (
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
    top_contributors = [{"contributor": r.contributor, "submissions": r.submissions} for r in top_contributors_q]

    # Unique contributor count
    unique_contributors = (
        db.query(func.count(func.distinct(Contribution.contributor)))
        .filter(Contribution.campaign_id == campaign.id)
        .scalar()
    )

    # Total rewards paid (reward_claimed == True)
    total_rewards_paid = db.query(Contribution).filter(
        Contribution.campaign_id == campaign.id, Contribution.reward_claimed == True
    ).count()

    return {
        "total_contributions": total_contribs,
        "average_cost_per_submission": avg_cost,
        "peak_activity": {"peak_hours": peak_hours, "max_submissions": max_count},
        "top_contributors": top_contributors,
        "unique_contributor_count": unique_contributors,
        "total_rewards_paid": total_rewards_paid,
    }


@router.get("/analytics/wallet/{wallet_address}")
def get_wallet_analytics(wallet_address: str, db: Session = Depends(get_session)):
    """
    Returns analytics for a given contributor (wallet_address), including:
      - Average reputation (total reputation score divided by number of contributions)
      - Total submissions across all campaigns
      - Campaigns created by the wallet
      - Campaigns contributed to by the wallet
    """
    # Average reputation
    total_rep = db.query(func.sum(Contribution.reputation_score)).filter(
        Contribution.contributor == wallet_address
    ).scalar() or 0

    contrib_count = db.query(func.count(Contribution.contribution_id)).filter(
        Contribution.contributor == wallet_address
    ).scalar() or 0

    average_reputation = total_rep / contrib_count if contrib_count > 0 else 0

    # Total submissions
    total_submissions = contrib_count

    # Campaigns created by the wallet (assuming Campaign.creator_wallet_address)
    created_campaigns = db.query(Campaign).filter(
        Campaign.creator_wallet_address == wallet_address
    ).options(joinedload(Campaign.contributions)).order_by(Campaign.created_at.desc()).all()
    created_campaigns_serialized = [
        serialize_campaign(c, len(c.contributions)) for c in created_campaigns
    ]

    # Campaigns contributed to by the wallet
    contributions = db.query(Contribution).filter(
        Contribution.contributor == wallet_address
    ).all()
    campaign_ids = list({c.campaign_id for c in contributions})
    contributed_campaigns = db.query(Campaign).filter(Campaign.id.in_(campaign_ids)).all()
    contributed_campaigns_serialized = [
        serialize_campaign(c, len(c.contributions)) for c in contributed_campaigns
    ]

    return {
        "average_reputation": average_reputation,
        "total_submissions": total_submissions,
        "campaigns_created": created_campaigns_serialized,
        "campaigns_contributed": contributed_campaigns_serialized,
    }


@router.get("/analytics/leaderboard/global")
def get_global_leaderboard(db: Session = Depends(get_session)):
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


@router.get("/analytics/average-ai-verification/{wallet_address}/{onchain_campaign_id}")
def get_average_ai_verification(
    wallet_address: str, 
    onchain_campaign_id: str, 
    db: Session = Depends(get_session)
):
    campaign = db.query(Campaign).filter(Campaign.onchain_campaign_id == onchain_campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    total_ai_score, contrib_count = db.query(
        func.sum(Contribution.ai_verification_score).label('total_ai_score'),
        func.count(Contribution.contribution_id).label('contrib_count')
    ).filter(
        Contribution.contributor == wallet_address,
        Contribution.campaign_id == campaign.id
    ).first()

    if contrib_count == 0:
        return {"average_ai_verification": 0}

    avg_ai_verification = total_ai_score / contrib_count if total_ai_score is not None else 0
    return {"average_ai_verification": avg_ai_verification}



@router.get("/analytics/leaderboard/global/contributors")
def get_top_global_contributors(db: Session = Depends(get_session)):
    """
    Returns top 5 global contributors across all campaigns.
    For each contributor, returns:
      - address
      - total contributions (count)
      - success rate (average AI verification score)
      - total amount earned (sum of campaign.unit_price for each contribution)
    """
    results = (
        db.query(
            Contribution.contributor.label("address"),
            func.count(Contribution.contribution_id).label("total_contributions"),
            func.avg(Contribution.ai_verification_score).label("success_rate"),
            func.sum(Campaign.unit_price).label("total_amount_earned")
        )
        .join(Campaign, Campaign.id == Contribution.campaign_id)
        .group_by(Contribution.contributor)
        .order_by(func.count(Contribution.contribution_id).desc())  # Order by total contributions (descending)
        .limit(5)
        .all()
    )
    # Use the _mapping attribute to convert each row to a dict.
    return [dict(r._mapping) for r in results]



@router.get("/analytics/leaderboard/global/creators")
def get_top_campaign_creators(db: Session = Depends(get_session)):
    """
    Returns top 5 campaign creators.
    For each creator, returns:
      - creator wallet address
      - total number of campaigns created
      - total amount spent (sum of campaign.total_budget for campaigns they created)
      - reputation score (average reputation_score from contributions on their campaigns)
    """
    # First, build a subquery to compute the average reputation score for each creator.
    creator_reputation_subq = (
        db.query(
            Campaign.creator_wallet_address.label("creator"),
            func.avg(Contribution.reputation_score).label("avg_reputation")
        )
        .join(Contribution, Contribution.campaign_id == Campaign.id)
        .group_by(Campaign.creator_wallet_address)
        .subquery()
    )

    results = (
        db.query(
            Campaign.creator_wallet_address.label("creator"),
            func.count(Campaign.id).label("total_campaigns"),
            func.sum(Campaign.total_budget).label("total_amount_spent"),
            creator_reputation_subq.c.avg_reputation.label("reputation_score")
        )
        .outerjoin(creator_reputation_subq, Campaign.creator_wallet_address == creator_reputation_subq.c.creator)
        .group_by(Campaign.creator_wallet_address, creator_reputation_subq.c.avg_reputation)
        .order_by(func.count(Campaign.id).desc())
        .limit(5)
        .all()
    )
    return [dict(r._mapping) for r in results]


