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
    create_product_option_service,
    get_options_by_product_service,
    delete_option_service,
    create_option_value_service,
    get_values_by_option_service,
    delete_option_value_service
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

#Servicios para opciones de productos
@router.post("/{product_id}/options", response_model=ProductOptionResponse, status_code=201)
def create_option(
    product_id: str,
    option_data: ProductOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_product_option_service(db, product_id, option_data.name)

@router.get("/{product_id}/options", response_model=List[ProductOptionResponse])
def get_options(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_options_by_product_service(db, product_id)

@router.delete("/options/{option_id}", status_code=204)
def delete_option(
    option_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_option_service(db, option_id)

# ── ProductOptionValue endpoints ──

@router.post("/options/{option_id}/values", response_model=ProductOptionValueResponse, status_code=201)
def create_option_value(
    option_id: str,
    value_data: ProductOptionValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_option_value_service(db, option_id, value_data.value)

@router.get("/options/{option_id}/values", response_model=List[ProductOptionValueResponse])
def get_option_values(
    option_id: str,
    db: Session = Depends(get_db)
):
    return get_values_by_option_service(db, option_id)

@router.delete("/options/values/{value_id}", status_code=204)
def delete_option_value(
    value_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_option_value_service(db, value_id)
