from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from src.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import ContactModel, ContactModelResponse
from src.database.db import get_db
from src.services.contacts import ContactService
from src.services.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_admin_user),
):
    contact_service = ContactService(db)
    return {"message": "This is secret dashboard"}
