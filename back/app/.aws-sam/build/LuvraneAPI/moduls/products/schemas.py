from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List
from decimal import Decimal


class ProductImageBase(BaseModel):
    image_url: HttpUrl
    position: int = 0

class ProductImageCreate(ProductImageBase):
    pass

class ProductImageResponse(ProductImageBase):
    id: str

    class Config:
        from_attributes = True


class VariantValueBase(BaseModel):
    option_value_id: str

class VariantValueCreate(VariantValueBase):
    pass

class VariantValueResponse(VariantValueBase):
    id: str

    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    stock: int = 0
    price: Optional[Decimal] = None
    sku: str

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, value):
        if value < 0:
            raise ValueError("Le stock ne peut pas être négatif")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Le prix doit être supérieur à 0")
        return value

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("SKU invalide")
        return value

class ProductVariantCreate(ProductVariantBase):
    option_value_ids: List[str] = []
    attributes: dict = {}

class ProductVariantResponse(ProductVariantBase):
    id: str
    signature: str
    is_active: bool
    values: List[VariantValueResponse] = []

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Le nom du produit doit contenir au moins 2 caractères")
        if len(value) > 255:
            raise ValueError("Le nom du produit ne peut pas dépasser 255 caractères")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Le prix doit être supérieur à 0")
        return value

class ProductCreate(ProductBase):
    store_id: str
    images: Optional[List[ProductImageCreate]] = []
    variants: Optional[List[ProductVariantCreate]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is not None:
            value = value.strip()
            if len(value) < 2:
                raise ValueError("Le nom du produit doit contenir au moins 2 caractères")
            if len(value) > 255:
                raise ValueError("Le nom du produit ne peut pas dépasser 255 caractères")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Le prix doit être supérieur à 0")
        return value

class ProductResponse(ProductBase):
    id: str
    store_id: str
    images: List[ProductImageResponse] = []
    variants: List[ProductVariantResponse] = []
    is_active: bool
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class UpdatePosition(BaseModel):
    position: int = Field(..., ge=0)

class PresignedUrlRequest(BaseModel):
    content_type: str
    folder: str

class PresignedUrlResponse(BaseModel):
    presigned_url: str
    public_url: str
    media_type: str

class ProductsPageResponse(BaseModel):
    total: int
    products: List[ProductResponse]
