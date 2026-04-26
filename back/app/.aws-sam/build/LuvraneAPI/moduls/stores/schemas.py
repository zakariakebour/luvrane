from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

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
    products: List = []  
    type: str
    is_active: bool
    created_at: Optional[str] = None
    products: List[dict] = []

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