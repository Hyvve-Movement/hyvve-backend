import os
import uuid
import shutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Form, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.campaigns.models import Campaign, Contribution
from app.core.database import get_session
from app.core.constants import OPENAI_API_KEY

from app.ai_verification.services import AIVerificationSystem, SimilarityScore


router = APIRouter()


@router.post("/contributions/verify", summary="Upload a document to verify a contribution")
async def verify_contribution(
    onchain_campaign_id: str = Form(...),
    wallet_address: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session)
):
    """
    Endpoint to upload a document (image, PDF, text, CSV) along with an onchain_campaign_id
    and wallet_address. The campaign description is fetched from the Campaign model.
    The document is then processed to generate a verification score which is saved to a new
    Contribution record.
    """
    # Retrieve the campaign by its onchain_campaign_id.
    campaign = db.query(Campaign).filter(
        Campaign.onchain_campaign_id == onchain_campaign_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Save the uploaded file to a temporary path.
    temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Instantiate the AI verification system.
    openai_api_key = OPENAI_API_KEY
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    verifier = AIVerificationSystem(openai_api_key=openai_api_key)
    
    # Generate the verification score.
    try:
        verification_score = verifier.verify(campaign, temp_file_path)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
    
    # Remove the temporary file.
    os.remove(temp_file_path)
    
    return {
        "verification_score": verification_score,
    }