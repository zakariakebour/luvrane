#Importamos repositorio del carrito
from moduls.users.repositories.cart_repository import (
    add_cart_item,
    get_cart,
    get_item,
    update_cart_quantity,
    remove_cart_item,
    clear_cart,
    get_cart_item_by_id
)

#Importamos repositorio de productos para validar que existe
from moduls.products.repositories import get_product_by_id, get_product_variant_by_id
#Importamos excepciones
from core.exceptions import NotFoundException, ConflictException, ForbiddenException
from moduls.users.schemas import CartItemResponse
from moduls.stores.repositories.repositories import select_store_by_id

#Metodo para añadir producto al carrito
def add_item_service(db, user_id: str, product_id: str, variant_id: str = None, quantity: int = 1 ,current_user = None):
    #Comprobamos que el producto existe y esta activo
    product = get_product_by_id(db, product_id)
    if not product or not product.is_active:
        raise NotFoundException("Produit introuvable o désactivé")

    #Evitar que el dueño añada sus propios productos al carrito
    if current_user:
        store = select_store_by_id(db, product.store_id)
        if store and store.owner_id == str(current_user.id):
            raise ForbiddenException(
                "Vous ne pouvez pas ajouter les produits de votre propre magasin au panier."
            )

    # Si no viene variant_id, debemos buscar la variante 'DEFAULT' porque ahi es donde vive el stock
    target_variant = None
    if variant_id:
        target_variant = get_product_variant_by_id(db, variant_id)
    else:
        # Buscamos la variante por defecto para productos simples
        target_variant = next((v for v in product.variants if "DEFAULT" in v.sku), None)
        # Actualizamos el variant_id para que se guarde en la tabla cart_items
        variant_id = target_variant.id if target_variant else None

    if not target_variant:
        raise NotFoundException("Cette option du produit n'est pas disponible")

    # Validacion de stock disponible en la variante
    if target_variant.stock < quantity:
        raise ConflictException(f"Stock insuffisant. Disponible: {target_variant.stock}")

    # Comprobamos si el producto con esa variante ya está en el carrito
    existing_item = get_item(db, user_id, variant_id, product_id)
    if existing_item:
        new_quantity = existing_item.quantity + quantity
        # Volver a validar stock con la suma total acumulada
        if target_variant.stock < new_quantity:
            raise ConflictException(f"Stock insuffisant en ajoutant au panier")
        return update_cart_quantity(db, existing_item.id, new_quantity)

    # Si no existe lo añadimos al carrito con la variante detectada
    return add_cart_item(db, user_id, product_id, variant_id, quantity)

#Metodo para obtener carrito del usuario
def get_cart_service(db, user_id: str):
    items = get_cart(db, user_id)

    result = []
    for item in items:
        result.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            created_at=item.created_at,
            product_name=item.product.name if item.product else None,
            image_url=item.product.images[0].image_url if item.product and item.product.images else None,
            price=item.variant.price if item.variant else None,
            variant_name=(
                f"{item.variant.color.name if item.variant and item.variant.color else ''} "
                f"{item.variant.size.name if item.variant and item.variant.size else ''}"
            ).strip()
        ))

    return result

#Metodo para actualizar cantidad de un item del carrito
def update_quantity_service(db, user_id: str, item_id: str, quantity: int):
    #Buscamos el item por su ID directamente para asegurar precision
    item = get_cart_item_by_id(db, item_id)
    
    #Comprobamos que el item existe y pertenece al usuario autenticado
    if not item or item.user_id != user_id:
        raise NotFoundException("Article introuvable")

    #Si la cantidad es 0 o menor eliminamos el item directamente
    if quantity <= 0:
        remove_cart_item(db, item_id)
        return {"detail": "Article supprimé du panier"}

    #Comprobamos si hay stock suficiente en la variante antes de permitir el aumento
    if item.variant and item.variant.stock < quantity:
        raise ConflictException(f"Stock insuffisant. Disponible: {item.variant.stock}")

    #Actualizamos la cantidad del item en la base de datos
    return update_cart_quantity(db, item_id, quantity)

#Metodo para eliminar producto del carrito
def remove_item_service(db, user_id: str, item_id: str):
    #Buscamos el item por su ID y validamos pertenencia al usuario
    item = get_cart_item_by_id(db, item_id)
    
    #Si el item no existe o no es del usuario lanzamos excepcion
    if not item or item.user_id != user_id:
        raise NotFoundException("Article introuvable")

    #Eliminamos el item definitivamente del carrito
    remove_cart_item(db, item_id)

#Metodo para vaciar carrito completo del usuario
def clear_cart_service(db, user_id: str):
    clear_cart(db, user_id)
    return {"detail": "Panier vidé"}