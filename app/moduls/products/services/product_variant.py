from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from moduls.products.repositories.product_variant import (
    add_product_variant,
    get_product_variant_by_id,
    get_variants_by_product,
    update_variant_stock,
    update_product_variant,
    delete_product_variant,
    add_variant_media,
    get_media_by_variant,
    get_media_by_id,
    delete_variant_media,
    update_media_position,
    count_variant_media,
    get_color_by_id,
    get_size_by_id,
    create_color,
    get_all_colors,
    delete_color,
    create_size,
    get_all_sizes,
    delete_size
)
from moduls.products.repositories.product_repository import get_product_by_id
from core.exceptions import NotFoundException, ConflictException, ValidationException
from core.s3 import delete_file

# Limite maximo de media por variante
MAX_MEDIA = 10

def add_product_variant_service(db: Session, variant_data: dict, product_id: str):
    # Comprobamos si existe el producto
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    # Validamos color si se envia
    if variant_data.get("color_id"):
        color = get_color_by_id(db, variant_data["color_id"])
        if not color:
            raise NotFoundException("Couleur introuvable")

    # Validamos talla si se envia
    if variant_data.get("size_id"):
        size = get_size_by_id(db, variant_data["size_id"])
        if not size:
            raise NotFoundException("Taille introuvable")

    # Creamos la variante y manejamos duplicados
    try:
        variant = add_product_variant(db, product_id, variant_data)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Cette combinaison couleur/taille existe déjà pour ce produit")

    return variant

def get_variants_by_product_service(db: Session, product_id: str):
    # Comprobamos si existe el producto
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    return get_variants_by_product(db, product_id)

def get_variant_by_id_service(db: Session, variant_id: str):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")
    return variant

def update_variant_stock_service(db: Session, variant_id: str, stock: int):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")
    # Validamos el numero de stock
    if stock < 0:
        raise ValidationException("Stock invalide")
    return update_variant_stock(db, variant_id, stock)


def update_variant_service(db: Session, variant_id: str, variant_data: dict):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")

    # Validamos color si se envia
    if variant_data.get("color_id"):
        color = get_color_by_id(db, variant_data["color_id"])
        if not color:
            raise NotFoundException("Couleur introuvable")

    # Validamos talla si se envia
    if variant_data.get("size_id"):
        size = get_size_by_id(db, variant_data["size_id"])
        if not size:
            raise NotFoundException("Taille introuvable")

    try:
        return update_product_variant(db, variant_id, variant_data)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Cette combinaison couleur/taille existe déjà pour ce produit")

def delete_variant_service(db: Session, variant_id: str):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")
    delete_product_variant(db, variant_id)

def add_variant_media_service(db: Session, variant_id: str, media_data: dict, current_user_id: str):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")

    # Comprobamos el limite de media
    total = count_variant_media(db, variant_id)
    if total >= MAX_MEDIA:
        raise ValidationException(f"Maximum {MAX_MEDIA} médias par variante")

    # Convertimos la URL a string
    media_data["media_url"] = str(media_data["media_url"])

    return add_variant_media(db, variant_id, media_data)


def get_media_by_variant_service(db: Session, variant_id: str):
    # Comprobamos si existe la variante
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")
    return get_media_by_variant(db, variant_id)

#Metodo para eliminar media de la variante
def delete_variant_media_service(db: Session, media_id: str, current_user_id: str):
    # Comprobamos si existe el media
    media = get_media_by_id(db, media_id)
    if not media:
        raise NotFoundException("Média introuvable")

    # Eliminamos el archivo del bucket S3
    delete_file(media.media_url)

    # Eliminamos de la DB
    delete_variant_media(db, media_id)

#Metodo para actualizar posicion
def update_media_position_service(db: Session, media_id: str, position: int):
    # Comprobamos si existe el media
    media = get_media_by_id(db, media_id)
    if not media:
        raise NotFoundException("Média introuvable")
    # Validamos la posicion
    if position < 0:
        raise ValidationException("La position doit être positive")
    return update_media_position(db, media_id, position)

#Metodo para creacion de colores de variante
def create_color_service(db: Session, color_data: dict):
    try:
        return create_color(db, color_data)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Cette couleur existe déjà")


def get_all_colors_service(db: Session):
    return get_all_colors(db)


def delete_color_service(db: Session, color_id: str):
    # Comprobamos si existe el color
    color = get_color_by_id(db, color_id)
    if not color:
        raise NotFoundException("Couleur introuvable")
    delete_color(db, color_id)

#Metodo para crear talla
def create_size_service(db: Session, size_data: dict):
    try:
        return create_size(db, size_data)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Cette taille existe déjà")


def get_all_sizes_service(db: Session):
    return get_all_sizes(db)


def delete_size_service(db: Session, size_id: str):
    # Comprobamos si existe la talla
    size = get_size_by_id(db, size_id)
    if not size:
        raise NotFoundException("Taille introuvable")
    delete_size(db, size_id)
