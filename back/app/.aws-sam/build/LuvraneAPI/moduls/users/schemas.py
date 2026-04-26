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
    street: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    wilaya: str = Field(..., min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    is_default: bool = False

# Schema de respuesta de direccion
class AddressResponse(BaseModel):
    id: str
    street: str
    city: str
    wilaya: str
    postal_code: Optional[str] = None
    is_default: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Carrito

# Schema de entrada para añadir producto al carrito
class CartItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(1, gt=0)

# Schema de respuesta de item del carrito
class CartItemResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

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
    wilaya: str = Field(..., min_length=2, max_length=100)

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