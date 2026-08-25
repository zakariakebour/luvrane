from fastapi import Depends, Header
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_token
from core.exceptions import UnauthorizedException
from moduls.users.repositories.user_repository import get_user

#Metodo para obtener el usuario actual desde el token JWT
def get_current_user(
    # recibe el header Authorization
    authorization: str = Header(...),                          
    db: Session = Depends(get_db)
):
    #Comprobamos que el header tiene el formato correcto
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Token manquant")

    #Extraemos el token
    token = authorization.split(" ")[1]

    #Decodificamos el token
    payload = decode_token(token)

    #Extraemos el user_id
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token invalide")

    #Buscamos el usuario en la DB
    user = get_user(db, user_id)
    if not user:
        raise UnauthorizedException("Utilisateur introuvable")

    #Si la cuenta esta desactivada
    if not user.is_active:
        raise UnauthorizedException("Compte désactivé")

    return user