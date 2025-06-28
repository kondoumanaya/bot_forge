from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ExchangeApiKey, ExchangeApiKeyRequest, ExchangeApiKeyResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/api-keys", response_model=List[ExchangeApiKeyResponse])
async def get_api_keys(db: Session = Depends(get_db)):
    """Get all exchange API keys"""
    api_keys = db.query(ExchangeApiKey).filter(ExchangeApiKey.is_active == True).all()
    return api_keys

@router.get("/api-keys/{exchange}", response_model=ExchangeApiKeyResponse)
async def get_api_key(exchange: str, db: Session = Depends(get_db)):
    """Get API key for specific exchange"""
    api_key = db.query(ExchangeApiKey).filter(
        ExchangeApiKey.exchange == exchange,
        ExchangeApiKey.is_active == True
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail=f"API key for {exchange} not found")

    return api_key

@router.post("/api-keys", response_model=ExchangeApiKeyResponse)
async def create_api_key(api_key_data: ExchangeApiKeyRequest, db: Session = Depends(get_db)):
    """Create or update API key for exchange"""
    existing_key = db.query(ExchangeApiKey).filter(
        ExchangeApiKey.exchange == api_key_data.exchange
    ).first()

    if existing_key:
        existing_key.api_key = api_key_data.api_key
        existing_key.api_secret = api_key_data.api_secret
        existing_key.passphrase = api_key_data.passphrase
        existing_key.sandbox_mode = api_key_data.sandbox_mode
        existing_key.is_active = api_key_data.is_active
        db.commit()
        db.refresh(existing_key)
        return existing_key
    else:
        new_key = ExchangeApiKey(
            exchange=api_key_data.exchange,
            api_key=api_key_data.api_key,
            api_secret=api_key_data.api_secret,
            passphrase=api_key_data.passphrase,
            sandbox_mode=api_key_data.sandbox_mode,
            is_active=api_key_data.is_active
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        return new_key

@router.put("/api-keys/{exchange}", response_model=ExchangeApiKeyResponse)
async def update_api_key(
    exchange: str, 
    api_key_data: ExchangeApiKeyRequest, 
    db: Session = Depends(get_db)
):
    """Update API key for specific exchange"""
    existing_key = db.query(ExchangeApiKey).filter(
        ExchangeApiKey.exchange == exchange
    ).first()

    if not existing_key:
        raise HTTPException(status_code=404, detail=f"API key for {exchange} not found")

    existing_key.api_key = api_key_data.api_key
    existing_key.api_secret = api_key_data.api_secret
    existing_key.passphrase = api_key_data.passphrase
    existing_key.sandbox_mode = api_key_data.sandbox_mode
    existing_key.is_active = api_key_data.is_active

    db.commit()
    db.refresh(existing_key)
    return existing_key

@router.delete("/api-keys/{exchange}")
async def delete_api_key(exchange: str, db: Session = Depends(get_db)):
    """Deactivate API key for specific exchange"""
    existing_key = db.query(ExchangeApiKey).filter(
        ExchangeApiKey.exchange == exchange
    ).first()

    if not existing_key:
        raise HTTPException(status_code=404, detail=f"API key for {exchange} not found")

    existing_key.is_active = False
    db.commit()

    return {"message": f"API key for {exchange} deactivated successfully"}