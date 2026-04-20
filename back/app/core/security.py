from passlib.context import CryptContext
from datetime import datetime,timezone,timedelta
#Importamos desde el archivo config para cardar las variables
from core.config import SECRET_KEY
#Importamos las excepciones
from core.exceptions import UnauthorizedException

#Creamos el contexto
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Metodo para hashear contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Metodo para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ----- Parte para JWT
#Importamos jwt
import jwt

#Creamos las variables que necesitamos sacando el valor del archivo .env o en entorno aws
secret_key = SECRET_KEY
algorithm = HS256
acces_token_expire = 30
refresh_token_expire = 7

#Metodo para generar token
def create_access_token(user_id: str,role: str) -> str:
    payload = {
        "sub":user_id,
        "role":role,
        "exp":datetime.now(timezone.utc) + timedelta(minutes=acces_token_expire)
    }
    #Devolvemos el token creado
    return jwt.encode(payload,secret_key,algorithm=algorithm)

#Metodo para generar refresh token
def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub":user_id,
        "exp":datetime.now(timezone.utc) + timedelta(days=refresh_token_expire)
    }
    return jwt.encode(payload,secret_key,algorithm=algorithm)

#Metodo para verificar token
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token expiré")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Token invalide")
