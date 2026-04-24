import boto3
import urllib.parse
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

#Configuracion de Aurora DSQL
from core.config import (
    DSQL_ENDPOINT,
    DSQL_PORT,
    DSQL_USER,
    DSQL_DATABASE,
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

#En local usamos credenciales del .env
#En Lambda boto3 usa el rol IAM automaticamente
if os.getenv("ENV") == "local":
    boto3.setup_default_session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

#Metodo para generar token IAM temporal para Aurora DSQL
def generate_dsql_token() -> str:
    client = boto3.client("dsql", region_name=AWS_REGION)
    token = client.generate_db_connect_admin_auth_token(
        Hostname=DSQL_ENDPOINT,
        Region=AWS_REGION,
        ExpiresIn=3600
    )
    return token

#Variable global para reutilizar el engine entre invocaciones Lambda
#Lambda reutiliza el contenedor entre peticiones
_engine = None

def get_engine():
    global _engine
    #Si ya existe el engine lo reutilizamos
    if _engine is not None:
        return _engine

    token = generate_dsql_token()
    encoded_token = urllib.parse.quote_plus(token)

    database_url = (
        f"postgresql+psycopg2://{DSQL_USER}:{encoded_token}"
        f"@{DSQL_ENDPOINT}:{DSQL_PORT}/{DSQL_DATABASE}"
        f"?sslmode=require"
    )

    #En Lambda usamos pool pequeño para no agotar conexiones
    _engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=2,                   
        max_overflow=5                
    )
    return _engine

Base = declarative_base()

def get_db():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()