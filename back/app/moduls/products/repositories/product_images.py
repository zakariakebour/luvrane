#Importamos tabla de producto imagenes
from moduls.products.modules import ProductImage
#Importamos sesion
from sqlalchemy.orm import Session

# Añadir imagen o video a producto
def add_product_image(db: Session, product_id: str, image_data: dict) -> ProductImage:
    image = ProductImage(**image_data, product_id=product_id)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

#Metodo para seleccionar imagen por identificador
def get_image_by_id(db: Session, image_id: str) -> ProductImage:
    return db.query(ProductImage).filter(ProductImage.id == image_id).first()

#Metodo para contar cantidad de imagenes/videos que contiene el producto para establecer cantidad maxima
def count_images(db: Session, product_id: str) -> int:
    return db.query(ProductImage).filter(ProductImage.product_id == product_id).count()

# Eliminar imagen o video concreto
def delete_product_image(db: Session, image_id: str) -> None:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image:
        db.delete(image)
        db.commit()

# Reordenar imagen o video en el carrusel
def update_image_position(db: Session, image_id: str, position: int) -> ProductImage:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image:
        image.position = position
        db.commit()
        db.refresh(image)
    return image
