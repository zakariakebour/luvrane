from sqlalchemy.orm import Session
from moduls.products.modules import ProductVariant, VariantValue

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
