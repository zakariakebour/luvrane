# Importamos repositorio de variante
from moduls.products.repositories.product_variant import (
    add_product_variant,
    get_product_variant_by_id,
    get_variant_by_signature,
    get_variants_by_product,
    update_variant_stock
)
# Importamos metodo que selecciona el producto desde el repositorio de producto principal
from moduls.products.repositories.product_repository import get_product_by_id
# Importamos excepciones
from core.exceptions import NotFoundException, ConflictException, ValidationException
from sqlalchemy.exc import IntegrityError

#Metodo que se encarga de crear la combinación de la variante del producto
def build_signature(attributes: dict) -> str:
    return "|".join(f"{k}={v}" for k, v in sorted(attributes.items()))

# Metodo para crear la variante del producto con combinaciones dinamicas
def add_product_variant_service(db, variant_data, option_value_ids, attributes, product_id):
    # Comprobamos si exsiste el producto
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    #Creamos la signtatura de las combinaciones de la variante del producto
    signature = build_signature(attributes)

    # Añadimos signature a los datos
    variant_data["signature"] = signature

    # Creamos variante, manejamos error si el stock exsiste y hacemos rollback a nivel base de datos
    try:
        variant = add_product_variant(db, product_id, variant_data, option_value_ids)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Variant already exists")

    return variant

# Metodo para obtener todas las variantes del mismo producto
def get_variants_by_product_service(db, product_id):
    # Comprobamos si exsiste el producto
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    # Devolvemos todas las variantes del producto
    variants = get_variants_by_product(db, product_id)

    return variants

# Metodo para actualizar stock de la variante
def update_variant_stock_service(db, variant_id, stock):
    #Comprobamos si la variante exsiste
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variant introuvable")

    # Validamos el numero de stock
    if stock < 0:
        raise ValidationException("Stock invalide")

    # Actualizamos stock
    return update_variant_stock(db,variant_id,stock)