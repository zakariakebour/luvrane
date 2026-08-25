import boto3
import uuid
from core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET, AWS_S3_REGION
from core.exceptions import ValidationException
from botocore.config import Config 

#Creamos el cliente de S3
s3_client = boto3.client(
    "s3",
    region_name=AWS_S3_REGION,    
)

#Tipos de archivos permitidos
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime"]
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES

#Metodo para generar URL firmada para subir archivo directamente desde el frontend
def generate_presigned_url(folder: str, content_type: str, expires_in: int = 300) -> dict:
    #Comprobamos el tipo de archivo
    if content_type not in ALLOWED_TYPES:
        raise ValidationException("Type de fichier non autorisé")

    #Determinamos el tipo de media
    media_type = "image" if content_type in ALLOWED_IMAGE_TYPES else "video"

    #Generamos extension segun el content_type
    extensions = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "video/mp4": "mp4",
        "video/quicktime": "mov"
    }
    extension = extensions[content_type]

    #Generamos nombre unico para el archivo
    filename = f"{folder}/{uuid.uuid4()}.{extension}"

    #Generamos la URL firmada valida 5 minutos
    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": AWS_S3_BUCKET,
            "Key": filename,
        },
        ExpiresIn=expires_in
    )

    #URL publica del archivo una vez subido
    public_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{filename}"

    return {
        "presigned_url": presigned_url, 
        "public_url": public_url,       
        "media_type": media_type
    }

#Metodo para eliminar archivo de S3
def delete_file(file_url: str) -> None:
    if not file_url:
        return
    try:
        # Intentamos extraer el key de cualquier formato de URL de S3
        if ".amazonaws.com/" in file_url:
            key = file_url.split(".amazonaws.com/")[1]
        else:
            print(f"[S3] Formato de URL no reconocido: {file_url}")
            return
        s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=key)
        print(f"[S3] Archivo eliminado: {key}")
    except IndexError:
        print(f"[S3] No se pudo extraer el key de: {file_url}")
    except Exception as e:
        print(f"[S3] Error al eliminar: {e}")
