from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, Boolean, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from core.database import Base
import uuid
from datetime import datetime, timezone
import enum

# Clase para controlar estado del producto
class ProductStatus(enum.Enum):
    active = "active"
    pending = "pending"
    out_of_stock = "out_of_stock"
    discontinued = "discontinued"


# Clase para controlar categorias de genero
class GenderCategory(enum.Enum):
    men = "men"
    women = "women"
    kids = "kids"
    unisex = "unisex"


# Tabla completa de productos
class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    price = Column(Numeric(10, 2), nullable=False)

    store_id = Column(String(36), nullable=False, index=True)

    store = relationship(
        "Store",
        primaryjoin="foreign(Product.store_id) == Store.id",
        back_populates="products",
        viewonly=True
    )

    # Columna para activar/desactivar el producto
    is_active = Column(Boolean, default=True)

    # Columna para fecha de eliminacion
    deleted_at = Column(DateTime, nullable=True)

    # Columna relacion con estado del producto, formato soportado por Aurora DSQL
    status = Column(
        SQLEnum(
            ProductStatus,
            native_enum=False,
            length=30
        ),
        nullable=False,
        default=ProductStatus.active
    )

    # Columna para categorias de producto
    gender_category = Column(
        SQLEnum(
            GenderCategory,
            native_enum=False,
            length=30
        ),
        nullable=False
    )

    # Columna para registrar ultima fecha de modificacion
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relación con imágenes/videos del producto principal
    images = relationship(
        "ProductImage",
        primaryjoin="Product.id == foreign(ProductImage.product_id)",
        back_populates="product",
        viewonly=True
    )

    # Relación con variantes
    variants = relationship(
        "ProductVariant",
        primaryjoin="Product.id == foreign(ProductVariant.product_id)",
        back_populates="product",
        viewonly=True
    )

    # Columna de fecha de creacion del producto
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# Tabla de imagenes/videos del producto principal
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    image_url = Column(String(255), nullable=False)

    # Tipo de media
    media_type = Column(String(255), default="image")

    # Orden del carrusel
    position = Column(Integer, default=0)

    product_id = Column(String(36), nullable=False, index=True)

    # Relación con producto
    product = relationship(
        "Product",
        primaryjoin="foreign(ProductImage.product_id) == Product.id",
        back_populates="images",
        viewonly=True
    )

    # Columna de fecha de creacion del media
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

# Tabla variante de productos
class ProductVariant(Base):
    __tablename__ = "product_variants"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "color_id",
            "size_id"
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Stock de la variante
    stock = Column(Integer, default=0)

    # Precio por variante
    price = Column(Numeric(10, 2), nullable=True)

    # SKU único de la variante
    sku = Column(String(100), unique=True, nullable=False, index=True)

    product_id = Column(String(36), nullable=False, index=True)

    product = relationship(
        "Product",
        primaryjoin="foreign(ProductVariant.product_id) == Product.id",
        back_populates="variants",
        viewonly=True
    )

    # Columna relacion con color
    color_id = Column(String(36), nullable=True, index=True)

    # Relación con color
    color = relationship(
        "Color",
        primaryjoin="foreign(ProductVariant.color_id) == Color.id",
        viewonly=True
    )

    # Columna relacion con tabla tamaño
    size_id = Column(String(36), nullable=True, index=True)

    # Relación con talla
    size = relationship(
        "Size",
        primaryjoin="foreign(ProductVariant.size_id) == Size.id",
        viewonly=True
    )

    # Relación con imágenes/videos de variante
    images = relationship(
        "VariantMedia",
        primaryjoin="ProductVariant.id == foreign(VariantMedia.variant_id)",
        back_populates="variant",
        viewonly=True
    )

    # Columna para estado de la variante
    is_active = Column(Boolean, default=True)

    # Fecha creación
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Fecha actualización
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc)
    )

# Tabla de imagenes/videos de variantes
class VariantMedia(Base):
    __tablename__ = "variant_media"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    media_url = Column(String(255), nullable=False)

    # Tipo de media
    media_type = Column(String(255), default="image")

    # Orden del carrusel
    position = Column(Integer, default=0)

    # Columna relacion con variante
    variant_id = Column(String(36), nullable=False, index=True)

    # Relación con variante
    variant = relationship(
        "ProductVariant",
        primaryjoin="foreign(VariantMedia.variant_id) == ProductVariant.id",
        back_populates="images",
        viewonly=True
    )

    # Columna de fecha de creacion del media
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# Tabla colores de variante de un producto
class Color(Base):
    __tablename__ = "colors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Se elimina unique=True para permitir el mismo nombre en diferentes productos
    name = Column(String(50), nullable=False)

    hex_code = Column(String(7), nullable=False)

    # NUEVO: Relación directa con el producto para que sea privado de ese producto
    product_id = Column(String(36), nullable=False, index=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

# Tabla talla de un producto
class Size(Base):
    __tablename__ = "sizes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(20), nullable=False, unique=True)

    sort_order = Column(Integer, default=0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
