#Importamos tabla de producto imagenes
from moduls.products.modules import ProductImage
#Importamos sesion
from sqlalchemy.orm import Session

# Añadir imagen a producto
def add_product_image(db: Session, product_id: str, image_data: dict) -> ProductImage:
    image = ProductImage(**image_data, product_id=product_id)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

#Metodo para seleccionar imagen por identificador
def get_image_by_id(db: Session, image_id: str) -> ProductImage:
    return db.query(ProductImage).filter(ProductImage.id == image_id).first()

#Metodo para contar cantidad de imagenes/videos que contiene el producto para estabelecer cantidad maxima
def count_images(db,product_id):
    return db.query(ProductImage).filter(ProductImage.product_id == product_id).count()

# Eliminar imagen concreta
def delete_product_image(db: Session, image_id: str) -> None:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image:
        db.delete(image)
        db.commit()

# Reordenar imagenes del carrusel
def update_image_position(db: Session, image_id: str, position: int) -> ProductImage:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image:
        image.position = position
        db.commit()
        db.refresh(image)
    return image
