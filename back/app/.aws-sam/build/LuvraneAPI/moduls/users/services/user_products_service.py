#Importamos repositorio del carrito
from moduls.users.repositories.cart_repository import (
    add_cart_item,
    get_cart,
    get_item,
    update_cart_quantity,
    remove_cart_item,
    clear_cart
)
#Importamos repositorio de productos para validar que existe
from moduls.products.repositories import get_product_by_id, get_product_variant_by_id
#Importamos excepciones
from core.exceptions import NotFoundException, ConflictException, ForbiddenException

#Metodo para añadir producto al carrito
def add_item_service(db, user_id: str, product_id: str, variant_id: str = None, quantity: int = 1):
    #Comprobamos que el producto existe y esta activo
    product = get_product_by_id(db, product_id)

    #Si no se encontro el producto
    if not product:
        raise NotFoundException("Produit introuvable")
    
    #Si el producto no esta disponible
    if not product.is_active:
        raise ForbiddenException("Produit non disponible")

    #Si se selecciono variante comprobamos que existe
    if variant_id:
        variant = get_product_variant_by_id(db, variant_id)
        if not variant:
            raise NotFoundException("Variante introuvable")

    #Comprobamos si el producto ya esta en el carrito
    existing_item = get_item(db, user_id, variant_id, product_id)
    if existing_item:
        #Si ya existe simplemente aumentamos la cantidad
        return update_cart_quantity(db, existing_item.id, existing_item.quantity + quantity)

    #Si no existe lo añadimos al carrito
    return add_cart_item(db, user_id, product_id, variant_id, quantity)

#Metodo para obtener carrito del usuario
def get_cart_service(db, user_id: str):
    return get_cart(db, user_id)

#Metodo para actualizar cantidad de un item del carrito
def update_quantity_service(db, user_id: str, item_id: str, quantity: int):
    #Buscamos el item y comprobamos que pertenece al usuario
    item = get_item(db, user_id=user_id, product_id=None)
    if not item:
        raise NotFoundException("Article introuvable")

    #Si la cantidad es 0 eliminamos el item directamente
    if quantity <= 0:
        remove_cart_item(db, item_id)
        return {"detail": "Article supprimé du panier"}

    return update_cart_quantity(db, item_id, quantity)

#Metodo para eliminar producto del carrito
def remove_item_service(db, user_id: str, item_id: str):
    #Comprobamos que el item existe y pertenece al usuario
    item = get_item(db, user_id=user_id, product_id=None)
    if not item:
        raise NotFoundException("Article introuvable")

    #Eliminamos el item
    remove_cart_item(db, item_id)

#Metodo para vaciar carrito completo del usuario
def clear_cart_service(db, user_id: str):
    clear_cart(db, user_id)
    return {"detail": "Panier vidé"}