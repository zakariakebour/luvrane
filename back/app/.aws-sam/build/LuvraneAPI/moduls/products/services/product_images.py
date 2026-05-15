#Importamos repositorio de imagenes de producto
from moduls.products.repositories.product_images import (
    add_product_image,
    delete_product_image,
    update_image_position,
    count_images,
    get_image_by_id
)
#Importamos de repositorio de producto
from moduls.products.repositories.product_repository import get_product_by_id
#Importamos excepciones
from core.exceptions import NotFoundException, ForbiddenException, ValidationException
#Importamos metodo para seleccionar tienda desde el repositorio de tienda
from moduls.stores.repositories.repositories import select_store_by_id
#Importamos metodo para eliminar archivo de S3
from core.s3 import delete_file

#Limite maximo de imagenes/videos por producto
MAX_IMAGES = 10

#Metodo para agregar imagen o video al producto
def add_product_image_service(db, product_id: str, image_data, current_user_id: str):
    #Comprobamos que el producto existe
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    #Comprobamos que el producto esta activo
    if not product.is_active:
        raise ForbiddenException("Produit non disponible")
    #Comprobamos que el usuario sea el propietario de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")
    #Comprobamos el limite de imagenes/videos
    total = count_images(db, product_id)
    if total >= MAX_IMAGES:
        raise ValidationException(f"Maximum {MAX_IMAGES} médias par produit")
    #Convertimos a diccionario
    image_dict = image_data.model_dump()
    #Convertimos URL a String
    image_dict["image_url"] = str(image_dict["image_url"])
    #Añadimos la imagen o video
    return add_product_image(db, product_id, image_dict)

#Metodo para actualizar posicion de imagen o video en el carrusel
def update_position_service(db, image_id: str, position: int, current_user_id: str):
    #Comprobamos que la imagen existe
    image = get_image_by_id(db, image_id)
    if not image:
        raise NotFoundException("Média introuvable")
    #Comprobamos que el usuario sea el propietario de la tienda
    product = get_product_by_id(db, image.product_id)
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")
    #Comprobamos que la posicion sea valida
    if position < 0:
        raise ValidationException("La position doit être positive")
    return update_image_position(db, image_id, position)

#Metodo para eliminar imagen o video del producto
def delete_product_image_service(db, image_id: str, current_user_id: str):
    #Comprobamos que la imagen existe
    image = get_image_by_id(db, image_id)
    if not image:
        raise NotFoundException("Média introuvable")
    #Comprobamos que el producto existe
    product = get_product_by_id(db, image.product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    #Comprobamos que el usuario sea el propietario de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")
    #Eliminamos el archivo del bucket S3
    try:
        delete_file(image.image_url)
    except Exception:
        pass  # si falla no bloqueamos la eliminacion de la DB
    #Eliminamos de la DB
    delete_product_image(db, image_id)
