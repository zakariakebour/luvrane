from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from core.database import get_db
from moduls.users.services.password_reset_service import (
    request_password_reset_service,
    reset_password_service
)

password_reset_router = APIRouter(tags=["Password Reset"])

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@password_reset_router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    return request_password_reset_service(db, data.email)

@password_reset_router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    return reset_password_service(db, data.token, data.new_password)