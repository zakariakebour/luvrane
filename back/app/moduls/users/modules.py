from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from core.database import Base
from datetime import datetime, timezone
import enum
import uuid
from typing import Optional
from pydantic import BaseModel

class UserRole(enum.Enum):
    admin = "admin"
    owner = "owner"
    customer = "customer"


# Tabla principal de usuarios
class User(Base):
    __tablename__ = "users"

    # ID seguro (no incremental)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Username visible
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Email para login
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Contraseña hasheada
    hashed_password = Column(String(255), nullable=False)

    # Rol del usuario, compatible con Aurora DSQL (no permite Enum)
    role = Column(
        SQLEnum(
            UserRole,
            native_enum=False,
            length=20
        ),
        nullable=False,
        default=UserRole.customer
    )

    # Estado de la cuenta
    is_active = Column(Boolean, default=True)

    # Fecha de creacion de la cuenta
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Fecha de ultima modificacion
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Fecha de desactivacion de la cuenta
    deleted_at = Column(DateTime, nullable=True)

    # Relacion con direcciones del usuario
    addresses = relationship(
        "UserAddress",
        primaryjoin="User.id == foreign(UserAddress.user_id)",
        back_populates="user",
        viewonly=True
    )

    # Relacion con carrito del usuario
    cart_items = relationship(
        "CartItem",
        primaryjoin="User.id == foreign(CartItem.user_id)",
        back_populates="user",
        viewonly=True
    )

    # Relacion con likes del usuario
    likes = relationship(
        "ProductLike",
        primaryjoin="User.id == foreign(ProductLike.user_id)",
        back_populates="user",
        viewonly=True
    )

    #Identificador de Google para OAuth
    google_id = Column(String(255), unique=True, nullable=True)

    #Foto de perfil de Google
    avatar = Column(String(255), nullable=True)

    #Proveedor de autenticacion (local o google)
    auth_provider = Column(String(50), default="local")
    
# Tabla de direcciones del usuario, un usuario puede tener varias direcciones
class UserAddress(Base):
    __tablename__ = "user_addresses"

    # ID de la direccion
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Relacion con usuario
    user_id = Column(String(36), nullable=False, index=True)

    user = relationship(
        "User",
        primaryjoin="foreign(UserAddress.user_id) == User.id",
        back_populates="addresses",
        viewonly=True
    )

    #Columna numero de telefono
    phone = Column(String(20), nullable=False)
    # Calle y numero
    street = Column(String(255), nullable=False)

    # Ciudad
    city = Column(String(100), nullable=False)

    # Wilaya (region)
    wilaya = Column(String(100), nullable=False)

    # Codigo postal
    postal_code = Column(String(20), nullable=True)

    # Indica si es la direccion principal del usuario
    is_default = Column(Boolean, default=False)

    # Fecha de creacion
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Tabla de carrito, cada fila es un producto en el carrito del usuario
class CartItem(Base):
    __tablename__ = "cart_items"

    # ID del item del carrito
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Relacion con usuario
    user_id = Column(String(36), nullable=False, index=True)

    user = relationship(
        "User",
        primaryjoin="foreign(CartItem.user_id) == User.id",
        back_populates="cart_items",
        viewonly=True
    )

    # Relacion con producto
    product_id = Column(String(36), nullable=False, index=True)

    product = relationship(
        "Product",
        primaryjoin="foreign(CartItem.product_id) == Product.id",
        viewonly=True
    )

    # Relacion con variante del producto (talla, color)
    variant_id = Column(String(36), nullable=True, index=True)

    variant = relationship(
        "ProductVariant",
        primaryjoin="foreign(CartItem.variant_id) == ProductVariant.id",
        viewonly=True
    )

    # Cantidad del producto en el carrito
    quantity = Column(Integer, default=1)

    # Fecha en que se añadio al carrito
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Tabla de likes, cada fila es un like de un usuario a un producto
class ProductLike(Base):
    __tablename__ = "product_likes"

    # ID del like
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Relacion con usuario
    user_id = Column(String(36), nullable=False, index=True)

    user = relationship(
        "User",
        primaryjoin="foreign(ProductLike.user_id) == User.id",
        back_populates="likes",
        viewonly=True
    )

    # Relacion con producto
    product_id = Column(String(36), nullable=False, index=True)

    product = relationship(
        "Product",
        primaryjoin="foreign(ProductLike.product_id) == Product.id",
        viewonly=True
    )

    # Fecha en que se dio like
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GoogleCodeData(BaseModel):
    code: str
    role: Optional[UserRole] = None
