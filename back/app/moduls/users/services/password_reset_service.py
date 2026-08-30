from sqlalchemy.orm import Session
from moduls.users.repositories.password_reset_repository import (
    create_reset_token,
    get_reset_token,
    delete_reset_token
)
from moduls.users.repositories.user_repository import get_user_by_email, get_user
from core.security import hash_password
from core.exceptions import NotFoundException, ValidationException
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

SES_CLIENT = boto3.client('ses', region_name='eu-west-3')

def request_password_reset_service(db: Session, email: str):
    user = get_user_by_email(db, email)

    # No revelamos si el email existe o no por seguridad
    if not user or not user.is_active or user.auth_provider != "local":
        return {"message": "Si cet email existe, vous recevrez un lien de réinitialisation."}

    token = create_reset_token(db, user.id)

    reset_url = f"https://luvrane.com/reset-password/{token}"

    try:
        SES_CLIENT.send_email(
            Source="Luvrane <noreply@luvrane.com>",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": "Réinitialisation de votre mot de passe - Luvrane"},
                "Body": {
                    "Html": {
                        "Data": f"""
                        <html><body style="font-family:Arial,sans-serif;color:#333;background:#f5f5f5;padding:20px;">
                        <div style="max-width:600px;margin:0 auto;background:white;padding:30px;border-radius:10px;">
                            <h1 style="color:#000;text-align:center;letter-spacing:2px;">LUVRANE</h1>
                            <hr style="border:0;border-top:1px solid #eee;margin:20px 0;">
                            <h2>Réinitialisation du mot de passe</h2>
                            <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
                            <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe. Ce lien expire dans <b>1 heure</b>.</p>
                            <p style="text-align:center;margin-top:30px;">
                                <a href="{reset_url}" style="background:#000;color:white;padding:14px 24px;text-decoration:none;border-radius:6px;font-weight:bold;">
                                    Réinitialiser mon mot de passe
                                </a>
                            </p>
                            <p style="margin-top:20px;color:#86868b;font-size:13px;">Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
                            <hr style="border:0;border-top:1px solid #eee;margin-top:40px;">
                            <p style="font-size:12px;color:#999;text-align:center;">© 2026 Luvrane. Tous droits réservés.</p>
                        </div>
                        </body></html>
                        """
                    },
                    "Text": {"Data": f"Réinitialisez votre mot de passe: {reset_url}"}
                }
            }
        )
    except ClientError as e:
        print(f"[SES] Erreur: {e.response['Error']['Message']}")

    return {"message": "Si cet email existe, vous recevrez un lien de réinitialisation."}


def reset_password_service(db: Session, token: str, new_password: str):
    reset_token = get_reset_token(db, token)

    if not reset_token:
        raise ValidationException("Lien de réinitialisation invalide")

    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        delete_reset_token(db, reset_token.id)
        raise ValidationException("Lien de réinitialisation expiré")

    user = get_user(db, reset_token.user_id)
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    user.hashed_password = hash_password(new_password)
    delete_reset_token(db, reset_token.id)
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès"}