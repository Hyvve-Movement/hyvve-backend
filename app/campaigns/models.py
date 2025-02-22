import uuid
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    onchain_campaign_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String)
    campaign_type = Column(String, index=True)
    data_requirements = Column(String)
    quality_criteria = Column(String)
    unit_price = Column(Float)
    total_budget = Column(Float)
    min_data_count = Column(Integer)
    max_data_count = Column(Integer)
    expiration = Column(Integer)  # Unix timestamp
    metadata_uri = Column(String)
    transaction_hash = Column(String)
    platform_fee = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contributions = relationship("Contribution", back_populates="campaign")


class Contribution(Base):
    __tablename__ = 'contributions'

    contribution_id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, unique=True)
    contributor = Column(String)
    data_url = Column(String)
    data_hash = Column(String)
    signature = Column(String)
    transaction_hash = Column(String)
    quality_score = Column(Integer)
    is_verified = Column(Boolean, default=False)
    reward_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="contributions")
