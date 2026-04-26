from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt
#Importamos desde el archivo config
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS  
#Importamos las excepciones
from core.exceptions import UnauthorizedException

#Creamos el contexto
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

#Metodo para hashear contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#Metodo para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Variables JWT desde config
secret_key = SECRET_KEY
algorithm = ALGORITHM                          
acces_token_expire = ACCESS_TOKEN_EXPIRE_MINUTES   
refresh_token_expire = REFRESH_TOKEN_EXPIRE_DAYS 

#Metodo para generar token
def create_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=acces_token_expire)
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)

#Metodo para generar refresh token
def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=refresh_token_expire)
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)

#Metodo para verificar token
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token expiré")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Token invalide")