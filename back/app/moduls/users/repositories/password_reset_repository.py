from sqlalchemy.orm import Session
from moduls.users.modules import PasswordResetToken
from datetime import datetime, timezone
import uuid
import secrets

def create_reset_token(db: Session, user_id: str) -> str:
    # Borramos tokens anteriores del usuario
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id
    ).delete()

    token = secrets.token_urlsafe(32)
    from datetime import timedelta
    reset_token = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(reset_token)
    db.commit()
    return token

def get_reset_token(db: Session, token: str):
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

def delete_reset_token(db: Session, token_id: str):
    db.query(PasswordResetToken).filter(
        PasswordResetToken.id == token_id
    ).delete()
    db.commit()