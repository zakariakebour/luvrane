from sqlalchemy.orm import Session
#Importamos clases de tablas
from moduls.products.modules import ProductVariant, VariantValue, ProductOptionValue

# Añadir variante a producto 
def add_product_variant(db: Session,product_id: str,variant_data: dict,option_value_ids: list[str]) -> ProductVariant:
    # Crear variante
    variant = ProductVariant(
        **variant_data,
        product_id=product_id
    )

    db.add(variant)
    #Obtenemos el id sin commit
    db.flush()  

    # Crear relaciones con valores
    for value_id in option_value_ids:
        db.add(VariantValue(
            variant_id=variant.id,
            option_value_id=value_id
        ))

    db.commit()
    db.refresh(variant)
    return variant

# Actualizar stock de variante
def update_variant_stock(db: Session, variant_id: str, stock: int) -> ProductVariant:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    variant.stock = stock
    db.commit()
    db.refresh(variant)

    return variant

# Metodo para actualizar datos de la variante
def update_variant(db: Session, variant_id: str, variant_data: dict) -> ProductVariant:
    # Obtenemos la variante
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id
    ).first()

    #Si no exsiste la variante
    if not variant:
        return None

    # Actualizamos solo los campos enviados
    for field, value in variant_data.items():
        # Ignoramos valores None
        if value is None:
            continue

        # Evitamos modificar campos críticos
        if field in ["id", "product_id"]:
            continue
        setattr(variant, field, value)

    db.commit()
    db.refresh(variant)

    return variant

# Eliminar variante (soft delete recomendado)
def delete_product_variant(db: Session, variant_id: str) -> None:
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

    if variant:
        variant.is_active = False
        db.commit()

# Obtener variante por id
def get_product_variant_by_id(db: Session, variant_id: str) -> ProductVariant:
    return db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

# Obtener variante por signature 
def get_variant_by_signature(db: Session, signature: str) -> ProductVariant:
    return db.query(ProductVariant).filter(
        ProductVariant.signature == signature
    ).first()

# Obtener variantes de un producto
def get_variants_by_product(db: Session, product_id: str):
    return db.query(ProductVariant).filter(
        ProductVariant.product_id == product_id
    ).all()

# Metodo para actualizar datos de la variante
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