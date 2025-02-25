# import os
# import uuid
# import shutil
# from datetime import datetime
# from fastapi import FastAPI, HTTPException, Depends, APIRouter, Form, UploadFile, File
# from sqlalchemy.orm import Session, joinedload
# from sqlalchemy import func
# from typing import List, Optional

# from app.campaigns.models import Campaign, Contribution
# from app.core.database import get_session
# from app.core.constants import OPENAI_API_KEY

# from app.ai_verification.services import AIVerificationSystem, SimilarityScore


# router = APIRouter()


# @router.post("/contributions/verify", summary="Upload a document to verify a contribution")
# async def verify_contribution(
#     onchain_campaign_id: str = Form(...),
#     wallet_address: str = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_session)
# ):
#     """
#     Endpoint to upload a document (image, PDF, text, CSV) along with an onchain_campaign_id
#     and wallet_address. The campaign description is fetched from the Campaign model.
#     The document is then processed to generate a verification score which is saved to a new
#     Contribution record.
#     """
#     # Retrieve the campaign by its onchain_campaign_id
#     campaign = db.query(Campaign).filter(
#         Campaign.onchain_campaign_id == onchain_campaign_id
#     ).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
    
#     # Save the uploaded file to a temporary path
#     temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
#     with open(temp_file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Determine the file MIME type
#     mime_type, _ = mimetypes.guess_type(file.filename)

#     # Instantiate the AI verification system
#     openai_api_key = OPENAI_API_KEY
#     if not openai_api_key:
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
#     verifier = AIVerificationSystem(openai_api_key=openai_api_key)

#     # Process text, CSV, and PDF files
#     if mime_type and mime_type.startswith("text") or file.filename.endswith(('.pdf', '.csv', '.txt')):
#         try:
#             verification_score = verifier.verify_text_document(campaign, temp_file_path)
#         except Exception as e:
#             os.remove(temp_file_path)
#             raise HTTPException(status_code=500, detail=f"Text document verification failed: {str(e)}")
    
#     # Process image files (PNG, JPG, JPEG, WEBP)
#     elif mime_type and mime_type.startswith("image") or file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
#         try:
#             verification_score = verifier.verify_image(campaign, temp_file_path)
#         except Exception as e:
#             os.remove(temp_file_path)
#             raise HTTPException(status_code=500, detail=f"Image verification failed: {str(e)}")
    
#     else:
#         os.remove(temp_file_path)
#         raise HTTPException(status_code=400, detail="Unsupported file type.")
    
#     # Remove the temporary file
#     os.remove(temp_file_path)
    
#     return {
#         "verification_score": verification_score,
#     }


# @router.post("/contributions/verify-text", summary="Upload a text, CSV, or PDF document to verify a contribution")
# async def verify_text_contribution(
#     onchain_campaign_id: str = Form(...),
#     wallet_address: str = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_session)
# ):
#     """
#     Endpoint to upload a text-based document (PDF, CSV, text file) along with an onchain_campaign_id
#     and wallet_address. The campaign description is fetched from the Campaign model.
#     The document is then processed to generate a verification score which is saved to a new
#     Contribution record.
#     """
#     # Retrieve the campaign by its onchain_campaign_id
#     campaign = db.query(Campaign).filter(
#         Campaign.onchain_campaign_id == onchain_campaign_id
#     ).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
    
#     # Save the uploaded file to a temporary path
#     temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
#     with open(temp_file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Instantiate the AI verification system
#     openai_api_key = OPENAI_API_KEY
#     if not openai_api_key:
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
#     verifier = AIVerificationSystem(openai_api_key=openai_api_key)

#     # Process text, CSV, and PDF files
#     try:
#         verification_score = verifier.verify_text_document(campaign, temp_file_path)
#     except Exception as e:
#         os.remove(temp_file_path)
#         raise HTTPException(status_code=500, detail=f"Text document verification failed: {str(e)}")
    
#     # Remove the temporary file
#     os.remove(temp_file_path)
    
#     return {
#         "verification_score": verification_score,
#     }


# @router.post("/contributions/verify-image", summary="Upload an image (PNG, JPG, JPEG, WEBP) to verify a contribution")
# async def verify_image_contribution(
#     onchain_campaign_id: str = Form(...),
#     wallet_address: str = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_session)
# ):
#     """
#     Endpoint to upload an image (PNG, JPG, JPEG, WEBP) along with an onchain_campaign_id
#     and wallet_address. The campaign description is fetched from the Campaign model.
#     The image is then processed to generate a verification score which is saved to a new
#     Contribution record.
#     """
#     # Retrieve the campaign by its onchain_campaign_id
#     campaign = db.query(Campaign).filter(
#         Campaign.onchain_campaign_id == onchain_campaign_id
#     ).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
    
#     # Save the uploaded image file to a temporary path
#     temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
#     with open(temp_file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Instantiate the AI verification system
#     openai_api_key = OPENAI_API_KEY
#     if not openai_api_key:
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
#     verifier = AIVerificationSystem(openai_api_key=openai_api_key)

#     # Process image files (PNG, JPG, JPEG, WEBP)
#     try:
#         verification_score = verifier.verify_image(campaign, temp_file_path)
#     except Exception as e:
#         os.remove(temp_file_path)
#         raise HTTPException(status_code=500, detail=f"Image verification failed: {str(e)}")
    
#     # Remove the temporary file
#     os.remove(temp_file_path)
    
#     return {
#         "verification_score": verification_score,
#     }


import os
import uuid
import shutil
import mimetypes
import asyncio

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from app.campaigns.models import Campaign
from app.core.database import get_session
from app.core.constants import OPENAI_API_KEY
from redis.asyncio import Redis

from app.ai_verification.services import AIVerificationSystem
from app.core.redis import get_redis_pool  # Your redis dependency

router = APIRouter()


@router.post("/contributions/verify", summary="Upload a document to verify a contribution")
async def verify_contribution(
    onchain_campaign_id: str = Form(...),
    wallet_address: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    redis_pool: Redis = Depends(get_redis_pool)
):
    """
    Endpoint to upload a document (image, PDF, text, CSV, DOC, DOCX) along with an onchain_campaign_id
    and wallet_address. The campaign description is fetched from the Campaign model.
    The document is then processed using the AI verification system with caching.
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
    
    # Instantiate the AI verification system with Redis caching.
    verifier = AIVerificationSystem(redis_pool=redis_pool)
    
    try:
        # Call the asynchronous verify method (which applies caching, fairness adjustment, etc.)
        verification_score = await verifier.verify(campaign, temp_file_path, wallet_address)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    
    # Remove the temporary file.
    os.remove(temp_file_path)
    
    return {"verification_score": verification_score}


@router.post("/contributions/verify-text", summary="Upload a text-based document to verify a contribution")
async def verify_text_contribution(
    onchain_campaign_id: str = Form(...),
    wallet_address: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    redis_pool: Redis = Depends(get_redis_pool)
):
    """
    Endpoint to upload a text-based document (PDF, CSV, TXT, DOC, DOCX) along with an onchain_campaign_id
    and wallet_address. Uses the caching-enabled verification method.
    """
    campaign = db.query(Campaign).filter(
        Campaign.onchain_campaign_id == onchain_campaign_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    verifier = AIVerificationSystem(redis_pool=redis_pool)
    try:
        # Even though this endpoint is intended for text documents,
        # we call the common async verify method so that caching and fairness adjustment apply.
        verification_score = await verifier.verify(campaign, temp_file_path, wallet_address)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Text document verification failed: {str(e)}")
    
    os.remove(temp_file_path)
    return {"verification_score": verification_score}


@router.post("/contributions/verify-image", summary="Upload an image to verify a contribution")
async def verify_image_contribution(
    onchain_campaign_id: str = Form(...),
    wallet_address: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    redis_pool: Redis = Depends(get_redis_pool)
):
    """
    Endpoint to upload an image (PNG, JPG, JPEG, WEBP) along with an onchain_campaign_id
    and wallet_address. Uses the caching-enabled verification method.
    """
    campaign = db.query(Campaign).filter(
        Campaign.onchain_campaign_id == onchain_campaign_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    verifier = AIVerificationSystem(redis_pool=redis_pool)
    try:
        verification_score = await verifier.verify(campaign, temp_file_path, wallet_address)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Image verification failed: {str(e)}")
    
    os.remove(temp_file_path)
    return {"verification_score": verification_score}
