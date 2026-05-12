from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    owner = "owner"
    customer = "customer"

#Direccion

# Schema de entrada para crear direccion
class AddressCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    street: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    wilaya: str = Field(..., min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    is_default: bool = False
    phone: str = Field(..., min_length=8, max_length=20)
       
# Schema de respuesta de direccion
class AddressResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    street: str
    city: str
    wilaya: str
    postal_code: Optional[str] = None
    is_default: bool
    created_at: Optional[datetime] = None
    phone: Optional[str] = None
    class Config:
        from_attributes = True

# Carrito

# Schema de entrada para añadir producto al carrito
class CartItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(1, gt=0)

# Schema de respuesta de item del carrito
# Schema de respuesta de item del carrito con información detallada
class CartItemResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    created_at: Optional[datetime] = None
    
    # Información extra para el Frontend
    product_name: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    variant_name: Optional[str] = None 

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        #Obtenemos la instancia base de Pydantic
        instance = super().model_validate(obj)
        
        #Asignamos manualmente los valores desde las relaciones
        # SQLAlchemy ya los tiene cargados gracias al joinedload del repositorio
        if hasattr(obj, 'product') and obj.product:
            instance.product_name = obj.product.name
            if obj.product.images:
                instance.image_url = obj.product.images[0].image_url
        
        if hasattr(obj, 'variant') and obj.variant:
            instance.price = obj.variant.price
            # Formateamos el nombre de la variante
            color = obj.variant.color.name if obj.variant.color else ""
            size = obj.variant.size.name if obj.variant.size else ""
            instance.variant_name = f"{color} {size}".strip() or "Standard"
            
        return instance
    
# Schema de respuesta de like
class ProductLikeResponse(BaseModel):
    id: str
    product_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

#Usuario

# Schema de entrada para crear usuario
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
   
    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return value

# Schema de respuesta de usuario
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None
    addresses: List[AddressResponse] = []
    cart_items: List[CartItemResponse] = []
    likes: List[ProductLikeResponse] = []

    class Config:
        from_attributes = True

# Schema para actualizar usuario
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    wilaya: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if value is not None:
            return value.strip()
        return value

# Schema para cambiar contraseña
class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return value
    
#Schema de login inline
class LoginData(BaseModel):
    email: EmailStr
    password: str

#Schema de refresh token inline
class RefreshTokenData(BaseModel):
    refresh_token: str

#Schema de Google code inline
class GoogleCodeData(BaseModel):
    code: str

    role: Optional[UserRole] = None
