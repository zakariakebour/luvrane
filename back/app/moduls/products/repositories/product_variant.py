from sqlalchemy.orm import Session
from moduls.products.modules import ProductVariant, VariantMedia, Color, Size
from core.exceptions import ConflictException
#Metodo para añdir variante
def add_product_variant(db: Session, product_id: str, variant_data: dict) -> ProductVariant:
    variant = ProductVariant(
        **variant_data,
        product_id=product_id
    )
    db.add(variant)
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
    
    try:
        db.delete(variant)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def get_product_variant_by_id(db: Session, variant_id: str) -> ProductVariant:
    return db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

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

#Metodo de creacion de variante
def add_variant_media(db: Session, variant_id: str, media_data: dict) -> VariantMedia:
    media = VariantMedia(
        **media_data,
        variant_id=variant_id
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

def get_media_by_variant(db: Session, variant_id: str):
    return db.query(VariantMedia).filter(VariantMedia.variant_id == variant_id).all()

def get_media_by_id(db: Session, media_id: str) -> VariantMedia:
    return db.query(VariantMedia).filter(VariantMedia.id == media_id).first()

def delete_variant_media(db: Session, media_id: str) -> None:
    media = db.query(VariantMedia).filter(VariantMedia.id == media_id).first()
    if media:
        db.delete(media)
        db.commit()

def update_media_position(db: Session, media_id: str, position: int) -> VariantMedia:
    media = db.query(VariantMedia).filter(VariantMedia.id == media_id).first()
    if media:
        media.position = position
        db.commit()
        db.refresh(media)
    return media

def count_variant_media(db: Session, variant_id: str) -> int:
    return db.query(VariantMedia).filter(VariantMedia.variant_id == variant_id).count()

#Metodo de creacion de color
def create_color(db: Session, color_data: dict) -> Color:
    # Ahora buscamos si el color ya existe asignado a ESTE producto específico
    existing = db.query(Color).filter(
        Color.name == color_data.get("name"),
        Color.product_id == color_data.get("product_id") 
    ).first()

    if existing:
        raise ConflictException("Cette couleur existe déjà pour ce produit")

    color = Color(**color_data)
    db.add(color)
    db.commit()
    db.refresh(color)
    return color

def get_all_colors(db: Session):
    return db.query(Color).all()

def get_color_by_id(db: Session, color_id: str) -> Color:
    return db.query(Color).filter(Color.id == color_id).first()

def delete_color(db: Session, color_id: str) -> None:
    color = db.query(Color).filter(Color.id == color_id).first()
    if color:
        db.delete(color)
        db.commit()
        
#Metodo de creacion de talla
def create_size(db: Session, size_data: dict) -> Size:
    size = Size(**size_data)
    db.add(size)
    db.commit()
    db.refresh(size)
    return size

def get_all_sizes(db: Session):
    return db.query(Size).order_by(Size.sort_order).all()

def get_size_by_id(db: Session, size_id: str) -> Size:
    return db.query(Size).filter(Size.id == size_id).first()


def delete_size(db: Session, size_id: str) -> None:
    size = db.query(Size).filter(Size.id == size_id).first()
    if size:
        db.delete(size)
        db.commit()