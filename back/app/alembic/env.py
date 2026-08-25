from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import sys
import os

#Añadimos el proyecto al path para poder importar modulos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

#Importamos el engine y Base desde database
from core.database import get_engine, Base

#Importamos TODOS los modelos para que Alembic los detecte
from moduls.users.modules import User, UserAddress, CartItem, ProductLike
from moduls.stores.modules import Store
from moduls.products.modules import (
    Product,
    ProductImage,
    ProductVariant,
    ProductOption,
    ProductOptionValue,
    VariantValue,
    ProductStatus
)
from moduls.orders.modules import Order, OrderItem

#Configuracion de Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

#Metadatos de todos los modelos
target_metadata = Base.metadata

#Metodo para ejecutar migraciones
def run_migrations_online():
    engine = get_engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transactional_ddl=False
        )

        context.run_migrations()

run_migrations_online()