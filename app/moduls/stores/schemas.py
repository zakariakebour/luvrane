from pydantic import BaseModel, Field, field_validator,ConfigDict
from typing import Optional, List
from datetime import datetime
from moduls.products.schemas import ProductResponse
# Importamos el Enum para asegurar compatibilidad con el modelo de SQLAlchemy
from moduls.stores.modules import StoreCategory 
from decimal import Decimal

#Clase completa para validacion de entrada y salida de los datos para la creacion de la tienda
class CreateStore(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    photo_profile: Optional[str] = None
    image: Optional[str] = None
    type: str = Field(...,min_length=2,max_length=100)
    category: Optional[StoreCategory] = None

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
    category: Optional[StoreCategory] = None
    products: List[ProductResponse] = Field(default_factory=list)
    type: str
    is_active: bool
    created_at: Optional[datetime] = None
    logistics_partner: Optional[str] = None
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
    category: Optional[StoreCategory] = None

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
        allowed = ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/quicktime"] 
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
    media_type: str

# Esquema para una tarifa individual
class ShippingRateBase(BaseModel):
    wilaya_id: int = Field(..., ge=1, le=58)
    wilaya_name: str

    delivery_price: Decimal = Field(..., ge=0)
    office_price: Optional[Decimal] = Field(None, ge=0)
    return_price: Optional[Decimal] = Field(None, ge=0)

    estimated_days: int = 3


# Para crear o actualizar una tarifa
class ShippingRateCreate(ShippingRateBase):
    pass


# Respuesta que daremos al Frontend
class ShippingRateResponse(ShippingRateBase):
    id: str
    store_id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# Esquema para actualización masiva
class BulkShippingUpdate(BaseModel):
    logistics_partner: str
    rates: List[ShippingRateCreate]
