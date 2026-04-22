from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

#Importamos repositorios de pedidos
from moduls.orders.repositories.order_repository import (
    create_order,
    get_order_by_id,
    get_orders_by_user,
    get_orders_by_store,
    update_order_status
)
#Importamos repositorio de items
from moduls.orders.repositories.order_item_repository import create_order_items_bulk
#Importamos repositorio de productos para verificar precio y stock
from moduls.products.repositories.product_repository import get_product_by_id, update_product
#Importamos repositorio de variantes para verificar stock
from moduls.products.repositories.product_variant import get_product_variant_by_id, update_product_variant
#Importamos repositorio de carrito para vaciarlo al finalizar pedido
from moduls.users.repositories.cart_repository import clear_cart
#Importamos repositorio de direcciones para verificar que existe
from moduls.users.repositories.adress_repository import get_direction_by_id
#Importamos repositorio de tienda para verificar owner
from moduls.stores.repositories import select_store_by_id
#Importamos excepciones
from core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
    ConflictException
)
#Importamos estados del pedido
from moduls.orders.modules import OrderStatus


#Metodo para crear pedido desde el carrito del usuario
def create_order_service(db: Session, user_id: str, order_data):
    try:
        #Comprobamos que la direccion existe y pertenece al usuario
        address = get_direction_by_id(db, order_data.address_id)
        if not address:
            raise NotFoundException("Adresse introuvable")
        if address.user_id != user_id:
            raise ForbiddenException("Accès interdit")

        #Comprobamos que hay items en el pedido
        if not order_data.items:
            raise ValidationException("Le panier est vide")

        #Procesamos cada item del pedido
        items_data = []
        total_price = 0

        for item in order_data.items:
            #Comprobamos que el producto existe y esta activo
            product = get_product_by_id(db, item.product_id)
            if not product:
                raise NotFoundException(f"Produit introuvable")
            if not product.is_active:
                raise ForbiddenException(f"Produit non disponible")

            #Calculamos el precio unitario
            unit_price = product.price

            #Si tiene variante comprobamos que existe y tiene stock
            if item.variant_id:
                variant = get_product_variant_by_id(db, item.variant_id)
                if not variant:
                    raise NotFoundException("Variante introuvable")

                #Validamos que la variante pertenece al producto
                if variant.product_id != product.id:
                    raise ValidationException("Variante invalide pour ce produit")

                if variant.stock < item.quantity:
                    raise ValidationException("Stock insuffisant")

                #Descontamos stock de la variante
                variant.stock -= item.quantity
                update_product_variant(db, variant)

                #Si la variante tiene precio propio lo usamos
                if variant.price:
                    unit_price = variant.price
            else:
                #Validamos stock en producto sin variante
                if product.stock < item.quantity:
                    raise ValidationException("Stock insuffisant")

                #Descontamos stock del producto
                product.stock -= item.quantity
                update_product(db, product)

            #Calculamos precio total del item
            item_total = unit_price * item.quantity
            total_price += item_total

            #Preparamos datos del item
            items_data.append({
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": item_total
            })

        #Creamos el pedido
        order_dict = {
            "user_id": user_id,
            "address_id": order_data.address_id,
            "total_price": total_price,
            "notes": order_data.notes,
            "status": OrderStatus.pending
        }
        order = create_order(db, order_dict)

        #Añadimos el order_id a cada item y los creamos en bulk
        for item in items_data:
            item["order_id"] = order.id
        create_order_items_bulk(db, items_data)

        #Vaciamos el carrito del usuario
        clear_cart(db, user_id)

        db.commit()
        return order

    except Exception as e:
        db.rollback()
        raise e


#Metodo para obtener pedido por identificador
def get_order_by_id_service(db: Session, order_id: str, user_id: str):
    #Buscamos el pedido
    order = get_order_by_id(db, order_id)
    if not order:
        raise NotFoundException("Commande introuvable")

    #Comprobamos que el pedido pertenece al usuario
    if order.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    return order


#Metodo para listar pedidos del usuario
def get_orders_by_user_service(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    return get_orders_by_user(db, user_id, skip=skip, limit=limit)


#Metodo para listar pedidos de una tienda (para el owner)
def get_orders_by_store_service(db: Session, store_id: str, current_user_id: str, skip: int = 0, limit: int = 20):
    #Comprobamos que el usuario es el owner de la tienda
    store = select_store_by_id(db, store_id)
    if not store:
        raise NotFoundException("Boutique introuvable")
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    return get_orders_by_store(db, store_id, skip=skip, limit=limit)

#Metodo para actualizar estado del pedido
def update_order_status_service(db: Session, order_id: str, status: OrderStatus, current_user_id: str):
    #Buscamos el pedido
    order = get_order_by_id(db, order_id)
    if not order:
        raise NotFoundException("Commande introuvable")

    #Comprobamos que el usuario es owner de la tienda del pedido
    if not order.items:
        raise ValidationException("Commande sans articles")

    #Obtenemos el store del primer producto (asumimos que todos son de la misma tienda)
    first_product = order.items[0].product

    if not first_product:
        raise NotFoundException("Produit introuvable")

    store = select_store_by_id(db, first_product.store_id)
    if not store:
        raise NotFoundException("Boutique introuvable")

    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    #Comprobamos que el pedido no esta ya entregado o cancelado
    if order.status in [OrderStatus.delivered, OrderStatus.cancelled]:
        raise ConflictException("Commande déjà finalisée")

    #Comprobamos transiciones de estado validas
    valid_transitions = {
        OrderStatus.pending:    [OrderStatus.confirmed, OrderStatus.cancelled],
        OrderStatus.confirmed:  [OrderStatus.preparing, OrderStatus.cancelled],
        OrderStatus.preparing:  [OrderStatus.shipped, OrderStatus.cancelled],
        OrderStatus.shipped:    [OrderStatus.delivered, OrderStatus.returned],
        OrderStatus.returned:   []
    }

    if status not in valid_transitions.get(order.status, []):
        raise ValidationException(f"Transition de statut invalide")

    return update_order_status(db, order, status)
    
#Metodo para cancelar pedido (para el usuario)
def cancel_order_service(db: Session, order_id: str, user_id: str):
    #Buscamos el pedido
    order = get_order_by_id(db, order_id)
    if not order:
        raise NotFoundException("Commande introuvable")

    #Comprobamos que el pedido pertenece al usuario
    if order.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    #Solo se puede cancelar si esta pendiente o confirmado
    if order.status not in [OrderStatus.pending, OrderStatus.confirmed]:
        raise ConflictException("Commande ne peut pas être annulée")

    updated_order = update_order_status(db, order, OrderStatus.cancelled)
    db.commit()
    return updated_order
