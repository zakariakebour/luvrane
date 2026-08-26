import httpx
from core.exceptions import UnauthorizedException
#Importamos variables desde config
from core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

from google.oauth2 import id_token
from google.auth.transport import requests

#Metodo para intercambiar el code de google por un token
async def exchange_google_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        print("FULL REQUEST DATA:", {
            "code": code[:20],  # solo primeros 20 caracteres por seguridad
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        #Mandamos el code a Google para obtener el token
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        print("GOOGLE TOKEN ERROR:", response.status_code, response.text)
        print("REDIRECT USED:", repr(GOOGLE_REDIRECT_URI))
        print("CLIENT ID:", GOOGLE_CLIENT_ID)
        
        if response.status_code != 200:
            raise UnauthorizedException("Code Google invalide")

        return response.json()

#Metodo para verificar el token de google y obtener datos del usuario

def verify_google_token(id_token_str: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        if idinfo.get("aud") != GOOGLE_CLIENT_ID:
            raise UnauthorizedException("Token Google invalide")

        if idinfo.get("iss") not in [
            "accounts.google.com",
            "https://accounts.google.com"
        ]:
            raise UnauthorizedException("Token Google invalide")

        if not idinfo.get("email_verified"):
            raise UnauthorizedException(
                "Email Google non vérifié"
            )

        return idinfo

    except Exception:
        raise UnauthorizedException("Token Google invalide")
