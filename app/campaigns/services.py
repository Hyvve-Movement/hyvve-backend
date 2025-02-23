from app.campaigns.models import Campaign, Contribution



def serialize_campaign(campaign: Campaign) -> dict:
    return {
        "campaign_id": campaign.id,  # Map model's 'id' to schema's 'campaign_id'
        "onchain_campaign_id": campaign.onchain_campaign_id,
        "title": campaign.title,
        "description": campaign.description,
        "campaign_type": campaign.campaign_type,
        "data_requirements": campaign.data_requirements,
        "quality_criteria": campaign.quality_criteria,
        "unit_price": campaign.unit_price,
        "total_budget": campaign.total_budget,
        "min_data_count": campaign.min_data_count,
        "max_data_count": campaign.max_data_count,
        "expiration": campaign.expiration,
        "metadata_uri": campaign.metadata_uri,
        "transaction_hash": campaign.transaction_hash,
        "platform_fee": campaign.platform_fee,
        "is_active": campaign.is_active,
        "created_at": campaign.created_at,
    }