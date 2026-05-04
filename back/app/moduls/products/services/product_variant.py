from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from moduls.products.repositories.product_variant import (
    add_product_variant,
    get_product_variant_by_id,
    get_variant_by_signature,
    get_variants_by_product,
    update_variant_stock
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
