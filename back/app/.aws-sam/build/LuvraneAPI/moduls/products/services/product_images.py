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
from core.exceptions import ConflictException, NotFoundException, ForbiddenException, ValidationException
#Importamos metodo para seleccionar tienda desde el repositorio de tienda
from moduls.stores.repositories import select_store_by_id

#Limite maximo de imagenes por producto
MAX_IMAGES = 10                                            

#Metodo para agregar imagenes al producto o video
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

    #Comprobamos el limite de imagenes
    total = count_images(db, product_id)
    if total >= MAX_IMAGES:                          
        raise ValidationException(f"Maximum {MAX_IMAGES} images par produit")

    #Convertimos a diccionario
    image_dict = image_data.model_dump()                  

    #Añadimos la imagen o video
    return add_product_image(db, product_id, image_dict)  

#Metodo para actualizar posicion de imagen en el carrusel
def update_position_service(db, image_id: str, position: int, current_user_id: str):
    #Comprobamos que la imagen existe
    image = get_image_by_id(db, image_id)
    if not image:
        raise NotFoundException("Image introuvable")

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
        raise NotFoundException("Image introuvable")

    #Comprobamos que el producto existe
    product = get_product_by_id(db, image.product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    #Comprobamos que el usuario sea el propietario de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    #Eliminamos la imagen
    delete_product_image(db, image_id)