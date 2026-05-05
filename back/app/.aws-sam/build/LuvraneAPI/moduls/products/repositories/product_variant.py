from sqlalchemy.orm import Session
from moduls.products.modules import ProductVariant, VariantValue
from moduls.products.modules import ProductOption, ProductOptionValue

def add_product_variant(db: Session, product_id: str, variant_data: dict, option_value_ids: list[str]) -> ProductVariant:
    variant = ProductVariant(
        **variant_data,
        product_id=product_id
    )
    db.add(variant)
    db.flush()

    for value_id in option_value_ids:
        db.add(VariantValue(
            variant_id=variant.id,
            option_value_id=value_id
        ))

    db.commit()
    db.refresh(variant)
    return variant

def update_variant_stock(db: Session, variant_id: str, stock: int) -> ProductVariant:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    variant.stock = stock
    db.commit()
    db.refresh(variant)
    return variant

def update_variant(db: Session, variant_id: str, variant_data: dict) -> ProductVariant:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        return None
    for field, value in variant_data.items():
        if value is None:
            continue
        if field in ["id", "product_id"]:
            continue
        setattr(variant, field, value)
    db.commit()
    db.refresh(variant)
    return variant

def delete_product_variant(db: Session, variant_id: str) -> None:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if variant:
        variant.is_active = False
        db.commit()

def get_product_variant_by_id(db: Session, variant_id: str) -> ProductVariant:
    return db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

def get_variant_by_signature(db: Session, signature: str) -> ProductVariant:
    return db.query(ProductVariant).filter(ProductVariant.signature == signature).first()

def get_variants_by_product(db: Session, product_id: str):
    return db.query(ProductVariant).filter(ProductVariant.product_id == product_id).all()

def update_product_variant(db: Session, variant_id: str, variant_data: dict) -> ProductVariant:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        return None
    for field, value in variant_data.items():
        if value is not None and field not in ["id", "product_id"]:
            setattr(variant, field, value)
    db.commit()
    db.refresh(variant)
    return variant

#Metodos para Opciones y sus valores en las variantes de un producto
def create_product_option(db: Session, product_id: str, name: str) -> ProductOption:
    option = ProductOption(
        product_id=product_id,
        name=name.strip()
    )
    db.add(option)
    db.commit()
    db.refresh(option)
    return option

def get_options_by_product(db: Session, product_id: str):
    return db.query(ProductOption).filter(ProductOption.product_id == product_id).all()

def get_option_by_id(db: Session, option_id: str) -> ProductOption:
    return db.query(ProductOption).filter(ProductOption.id == option_id).first()

def delete_option(db: Session, option_id: str) -> None:
    option = db.query(ProductOption).filter(ProductOption.id == option_id).first()
    if option:
        db.delete(option)
        db.commit()

def create_option_value(db: Session, option_id: str, value: str) -> ProductOptionValue:
    option_value = ProductOptionValue(
        option_id=option_id,
        value=value.strip()
    )
    db.add(option_value)
    db.commit()
    db.refresh(option_value)
    return option_value

def get_values_by_option(db: Session, option_id: str):
    return db.query(ProductOptionValue).filter(ProductOptionValue.option_id == option_id).all()

def get_option_value_by_id(db: Session, value_id: str) -> ProductOptionValue:
    return db.query(ProductOptionValue).filter(ProductOptionValue.id == value_id).first()

def delete_option_value(db: Session, value_id: str) -> None:
    value = db.query(ProductOptionValue).filter(ProductOptionValue.id == value_id).first()
    if value:
        db.delete(value)
        db.commit()

def get_option_values_by_ids(db: Session, ids: list[str]):
    return db.query(ProductOptionValue).filter(
        ProductOptionValue.id.in_(ids)
    ).all()


def get_option_by_id(db: Session, option_id: str):
    return db.query(ProductOption).filter(
        ProductOption.id == option_id
    ).first()


def get_options_by_product(db: Session, product_id: str):
    return db.query(ProductOption).filter(
        ProductOption.product_id == product_id
    ).all()