from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, Boolean, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
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
        primaryjoin="Product.store_id == Store.id",
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

    # Columna para registrar ultima fecha de modificacion
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relación con imágenes
    images = relationship(
        "ProductImage",
        primaryjoin="Product.id == ProductImage.product_id",
        back_populates="product",
        viewonly=True,
        cascade="all, delete"
    )

    # Relación con variantes
    variants = relationship(
        "ProductVariant",
        primaryjoin="Product.id == ProductVariant.product_id",
        back_populates="product",
        viewonly=True,
        cascade="all, delete"
    )

    # Relación con opciones del producto (Color, Talla, etc)
    options = relationship(
        "ProductOption",
        primaryjoin="Product.id == ProductOption.product_id",
        back_populates="product",
        viewonly=True,
        cascade="all, delete"
    )

# Tabla variante de productos
class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Stock de la variante
    stock = Column(Integer, default=0)

    # Precio por variante
    price = Column(Numeric(10, 2), nullable=True)

    # SKU único de la variante
    sku = Column(String(100), unique=True, nullable=False, index=True)

    # Firma única de la combinación (MUY IMPORTANTE)
    signature = Column(String(255), unique=True, index=True, nullable=False)

    product_id = Column(String(36), nullable=False, index=True)

    product = relationship(
        "Product",
        primaryjoin="ProductVariant.product_id == Product.id",
        back_populates="variants",
        viewonly=True
    )

    # Relación con valores de la variante
    values = relationship(
        "VariantValue",
        primaryjoin="ProductVariant.id == VariantValue.variant_id",
        back_populates="variant",
        viewonly=True,
        cascade="all, delete"
    )

    # Columna para estado de la variante
    is_active = Column(Boolean, default=True)

    # Fecha creación
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Fecha actualización
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

# Clase Opciones de producto (Color, Talla, etc)
class ProductOption(Base):
    __tablename__ = "product_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    product_id = Column(String(36), nullable=False, index=True)

    # Nombre de la opcion
    name = Column(String(50), nullable=False)

    # Relación con producto
    product = relationship(
        "Product",
        primaryjoin="ProductOption.product_id == Product.id",
        back_populates="options",
        viewonly=True
    )

    # Relación con valores
    values = relationship(
        "ProductOptionValue",
        primaryjoin="ProductOption.id == ProductOptionValue.option_id",
        back_populates="option",
        viewonly=True,
        cascade="all, delete"
    )

# Clase Valores de opcion del producto (Rojo, M, etc)
class ProductOptionValue(Base):
    __tablename__ = "product_option_values"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    option_id = Column(String(36), nullable=False, index=True)

    # Valor de la opcion
    value = Column(String(50), nullable=False)

    # Relación con opción
    option = relationship(
        "ProductOption",
        primaryjoin="ProductOptionValue.option_id == ProductOption.id",
        back_populates="values",
        viewonly=True
    )

# Tabla intermedia variante - valores
class VariantValue(Base):
    __tablename__ = "variant_values"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    variant_id = Column(String(36), nullable=False, index=True)
    option_value_id = Column(String(36), nullable=False, index=True)

    # Relación con variante
    variant = relationship(
        "ProductVariant",
        primaryjoin="VariantValue.variant_id == ProductVariant.id",
        back_populates="values",
        viewonly=True
    )

    # Relación con valor de opción
    option_value = relationship(
        "ProductOptionValue",
        primaryjoin="VariantValue.option_value_id == ProductOptionValue.id",
        viewonly=True
    )

    # Evitar duplicados de la misma combinación
    __table_args__ = (
        UniqueConstraint("variant_id", "option_value_id"),
    )

# Tabla de imagenes de productos
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
        primaryjoin="ProductImage.product_id == Product.id",
        back_populates="images",
        viewonly=True
    )