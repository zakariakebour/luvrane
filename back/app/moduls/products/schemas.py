from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class ProductImageBase(BaseModel):
    image_url: str
    position: int = 0
    # Tipo de media: image o video
    media_type: str = "image"

class ProductImageCreate(ProductImageBase):
    pass

class ProductImageResponse(ProductImageBase):
    id: str

    class Config:
        from_attributes = True

class VariantMediaBase(BaseModel):
    media_url: str
    position: int = 0
    # Tipo de media: image o video
    media_type: str = "image"

class VariantMediaCreate(VariantMediaBase):
    pass

class VariantMediaResponse(VariantMediaBase):
    id: str
    variant_id: str
    media_type : str
    class Config:
        from_attributes = True

class ColorBase(BaseModel):
    name: str
    hex_code: str

    @field_validator("hex_code")
    @classmethod
    def validate_hex_code(cls, value):
        value = value.strip()
        if not value.startswith("#") or len(value) != 7:
            raise ValueError("Le code hex doit être au format #RRGGBB")
        return value

class ColorCreate(ColorBase):
    pass

class ColorResponse(ColorBase):
    id: str

    class Config:
        from_attributes = True

class SizeBase(BaseModel):
    name: str
    sort_order: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if len(value) < 1:
            raise ValueError("Le nom de la taille ne peut pas être vide")
        return value

class SizeCreate(SizeBase):
    pass

class SizeResponse(SizeBase):
    id: str

    class Config:
        from_attributes = True

class ProductVariantBase(BaseModel):
    stock: int = 0
    price: Optional[Decimal] = None
    sku: str
    # Relacion con color y talla
    color_id: Optional[str] = None
    size_id: Optional[str] = None

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
    pass

class ProductVariantResponse(ProductVariantBase):
    id: str
    is_active: bool
    # Relacion con color y talla
    color: Optional[ColorResponse] = None
    size: Optional[SizeResponse] = None
    # Media de la variante
    images: List[VariantMediaResponse] = []

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    # Categoria de genero del producto
    gender_category: str
    
    stock: int = Field(0, ge=0)
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

    @field_validator("gender_category")
    @classmethod
    def validate_gender_category(cls, value):
        allowed = ["men", "women", "kids", "unisex"]
        if value not in allowed:
            raise ValueError(f"Catégorie invalide. Valeurs acceptées: {allowed}")
        return value

class ProductCreate(ProductBase):
    store_id: str
    # Media del producto principal
    images: Optional[List[ProductImageCreate]] = []
    # Variantes del producto
    variants: Optional[List[ProductVariantCreate]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    # Categoria de genero del producto
    gender_category: Optional[str] = None

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

    @field_validator("gender_category")
    @classmethod
    def validate_gender_category(cls, value):
        if value is not None:
            allowed = ["men", "women", "kids", "unisex"]
            if value not in allowed:
                raise ValueError(f"Catégorie invalide. Valeurs acceptées: {allowed}")
        return value

class ProductResponse(ProductBase):
    id: str
    store_id: str
    # Media del producto principal
    images: List[ProductImageResponse] = []
    # Variantes del producto
    variants: List[ProductVariantResponse] = []
    is_active: bool
    status: str
    created_at: Optional[datetime] = None
    store_name: Optional[str] = None
    class Config:
        from_attributes = True

# Schema de paginacion de productos
class ProductsPageResponse(BaseModel):
    total: int
    products: List[ProductResponse]

# Schema para actualizar posicion en carrusel
class UpdatePosition(BaseModel):
    position: int = Field(..., ge=0)

# Schema para solicitar URL firmada
class PresignedUrlRequest(BaseModel):
    content_type: str
    folder: str

# Schema de respuesta de URL firmada
class PresignedUrlResponse(BaseModel):
    presigned_url: str
    public_url: str
    media_type: str
