from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

#Clase completa para validacion de entrada y salida de los datos para la creacion de la tienda
class CreateStore(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    photo_profile: Optional[str] = None
    image: Optional[str] = None
    type: str = Field(...,min_length=2,max_length=100)

    # Validation validacion para el nombre
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        if len(value) > 255:
            raise ValueError("Le nom ne peut pas dépasser 255 caractères")
        return value

    # Validacion para la descripcion
    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if value is not None and len(value) > 1000:
            raise ValueError("La description ne peut pas dépasser 1000 caractères")
        return value

#Clase para respuesta de tiendas en los enpoints
class StoreResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    photo_profile: Optional[str]
    image: Optional[str]
    products: List[dict] = Field(default_factory=list)
    type: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

#Clase para respuesta de paginacion
class StoresPageResponse(BaseModel):
    total: int
    stores: List[StoreResponse]

#Clase schema para actualizacion de la tienda
class UpdateStore(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)  
    description: Optional[str] = Field(None, max_length=1000)         
    photo_profile: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] = Field(None, min_length=2, max_length=100)  

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is not None:
            return value.strip()
        return value

#Schema para solicitar URL firmada para foto de perfil o imagen de portada
class StoreImagePresignedRequest(BaseModel):
    content_type: str = Field(..., description="image/jpeg, image/png, image/webp, video/mp4")
    image_type: str = Field(..., description="profile o cover")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value):
        allowed = ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"]  # ✅ añadir videos
        if value not in allowed:
            raise ValueError("Type de fichier non autorisé")
        return value

    @field_validator("image_type")
    @classmethod
    def validate_image_type(cls, value):
        allowed = ["profile", "cover"]
        if value not in allowed:
            raise ValueError("Type d'image invalide, utilisez 'profile' ou 'cover'")
        return value

#Schema de respuesta de URL firmada
class StoreImagePresignedResponse(BaseModel):
    presigned_url: str
    public_url: str
    image_type: str
    media_type: str        # ✅ añadir para saber si es imagen o video