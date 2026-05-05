from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from moduls.products.repositories.product_variant import (
    add_product_variant,
    get_product_variant_by_id,
    get_variant_by_signature,
    get_variants_by_product,
    update_variant_stock,
    create_product_option,
    get_options_by_product,
    get_option_by_id,
    delete_option,
    create_option_value,
    get_values_by_option,
    get_option_value_by_id,
    delete_option_value,
    get_option_values_by_ids
)
from moduls.products.repositories.product_repository import get_product_by_id
from core.exceptions import NotFoundException, ConflictException, ValidationException

def build_signature(attributes: dict) -> str:
    return "|".join(f"{k}={v}" for k, v in sorted(attributes.items()))


def add_product_variant_service(db: Session, variant_data: dict, option_value_ids: list, attributes: dict, product_id: str):
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    signature = build_signature(attributes)
    variant_data["signature"] = signature

    try:
        variant = add_product_variant(db, product_id, variant_data, option_value_ids)
    except IntegrityError:
        db.rollback()
        raise ConflictException("Cette combinaison de variante existe déjà")

    return variant


def get_variants_by_product_service(db: Session, product_id: str):
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    return get_variants_by_product(db, product_id)


def update_variant_stock_service(db: Session, variant_id: str, stock: int):
    variant = get_product_variant_by_id(db, variant_id)
    if not variant:
        raise NotFoundException("Variante introuvable")
    if stock < 0:
        raise ValidationException("Stock invalide")
    return update_variant_stock(db, variant_id, stock)

#Metodos para opcion y su valor de un atributo
def create_product_option_service(db: Session, product_id: str, name: str):
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    return create_product_option(db, product_id, name)

def get_options_by_product_service(db: Session, product_id: str):
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    return get_options_by_product(db, product_id)

def delete_option_service(db: Session, option_id: str):
    option = get_option_by_id(db, option_id)
    if not option:
        raise NotFoundException("Option introuvable")
    delete_option(db, option_id)

def create_option_value_service(db: Session, option_id: str, value: str):
    option = get_option_by_id(db, option_id)
    if not option:
        raise NotFoundException("Option introuvable")
    return create_option_value(db, option_id, value)

def get_values_by_option_service(db: Session, option_id: str):
    option = get_option_by_id(db, option_id)
    if not option:
        raise NotFoundException("Option introuvable")
    return get_values_by_option(db, option_id)

def delete_option_value_service(db: Session, value_id: str):
    value = get_option_value_by_id(db, value_id)
    if not value:
        raise NotFoundException("Valeur introuvable")
    delete_option_value(db, value_id)

def validate_variant_structure(db: Session, product_id: str, option_value_ids: list[str]):

    values = get_option_values_by_ids(db, option_value_ids)

    if len(values) != len(option_value_ids):
        raise ValidationException("Option values invalides")

    option_map = {}

    for v in values:
        option = get_option_by_id(db, v.option_id)

        if option.product_id != product_id:
            raise ValidationException("Option ne appartient pas au produit")

        if v.option_id in option_map:
            raise ValidationException("Une variante ne peut pas avoir plusieurs valeurs pour la même option")

        option_map[v.option_id] = v.id

    product_options = get_options_by_product(db, product_id)

    if len(option_map) != len(product_options):
        raise ValidationException("La variante doit contenir toutes les options du produit")

    return values