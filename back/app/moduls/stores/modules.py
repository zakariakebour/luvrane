from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from core.database import Base
import uuid
from datetime import datetime, timezone
from moduls.products.modules import Product
from moduls.users.modules import User
import enum

# Categorias disponibles para la tienda
class StoreCategory(enum.Enum):
    ropa_mujer = "ropa_mujer"
    ropa_hombre = "ropa_hombre"
    accesorios = "accesorios"
    zapatos = "zapatos"
    ropa_deportiva = "ropa_deportiva"
    bolsos = "bolsos"
    cosmetica = "cosmetica"

class Store(Base):
    __tablename__ = "stores"

    #Identificador de la tienda
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    #Relacion con el usuario propietario de la tienda
    owner_id = Column(String(36), nullable=False, index=True)
    owner = relationship(
        "User",
        primaryjoin=foreign(owner_id) == User.id,
        viewonly=True
    )

    #Nombre de la tienda
    name = Column(String(255), nullable=False)

    #Descripcion de la tienda
    description = Column(Text, nullable=True)

    #Tipo de tienda, no puede ser nulo
    type = Column(String(100), nullable=False)

    #Categoria de la tienda
    category = Column(
        SQLEnum(
            StoreCategory,
            native_enum=False,
            length=30
        ),
        nullable=True
    )

    #foto de perfil de la tienda
    photo_profile = Column(String(255), nullable=True)

    #Foto rectangular extra de la tienda
    image = Column(String(255), nullable=True)

    #Relacion con la tabla productos
    products = relationship(
        "Product",
        primaryjoin=id == foreign(Product.store_id),
        viewonly=True
    )

    #Fecha de creacion de la tienda
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #Columna para guardar fecha de ultima de modificacion de la tienda
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    #Columna para guardar la fecha en la que fue desactiva la cuenta de la tienda
    deleted_at = Column(DateTime, nullable=True)

    #Columna para eliminar la tienda pero no de la base de datos completamente y poder recuperarla
    is_active = Column(Boolean, default=True)
