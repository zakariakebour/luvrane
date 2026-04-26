import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_secrets():
    #En local usamos .env directamente
    if os.getenv("ENV") == "local":
        return {
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
            "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
            "REFRESH_TOKEN_EXPIRE_DAYS": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)),
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
            "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
            "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_REGION": os.getenv("AWS_REGION"),
            "AWS_S3_REGION": os.getenv("AWS_S3_REGION"),
            "DSQL_ENDPOINT": os.getenv("DSQL_ENDPOINT"),
            "DSQL_PORT": os.getenv("DSQL_PORT", "5432"),
            "DSQL_USER": os.getenv("DSQL_USER"),
            "DSQL_DATABASE": os.getenv("DSQL_DATABASE"),
        }

    #En produccion (Lambda) leemos desde variables de entorno directamente
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
        "REFRESH_TOKEN_EXPIRE_DAYS": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)),
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
        "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),   # Lambda lo gestiona
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),  # Lambda lo gestiona
        "AWS_REGION": os.getenv("AWS_REGION", "eu-west-3"),
        "AWS_S3_REGION": os.getenv("AWS_S3_REGION", "eu-west-3"),
        "DSQL_ENDPOINT": os.getenv("DSQL_ENDPOINT"),
        "DSQL_PORT": os.getenv("DSQL_PORT", "5432"),
        "DSQL_USER": os.getenv("DSQL_USER"),
        "DSQL_DATABASE": os.getenv("DSQL_DATABASE"),
    }

#Cargamos los secrets
secrets = get_secrets()

SECRET_KEY = secrets["SECRET_KEY"]
ALGORITHM = secrets["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(secrets["ACCESS_TOKEN_EXPIRE_MINUTES"])
REFRESH_TOKEN_EXPIRE_DAYS = int(secrets["REFRESH_TOKEN_EXPIRE_DAYS"])

GOOGLE_CLIENT_ID = secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = secrets["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = secrets["GOOGLE_REDIRECT_URI"]

AWS_ACCESS_KEY_ID = secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = secrets["AWS_SECRET_ACCESS_KEY"]
AWS_S3_BUCKET = secrets["AWS_S3_BUCKET"]
AWS_S3_REGION = secrets["AWS_S3_REGION"]
AWS_REGION = secrets["AWS_REGION"]

DSQL_ENDPOINT = secrets["DSQL_ENDPOINT"]
DSQL_PORT = int(secrets["DSQL_PORT"])
DSQL_USER = secrets["DSQL_USER"]
DSQL_DATABASE = secrets["DSQL_DATABASE"]