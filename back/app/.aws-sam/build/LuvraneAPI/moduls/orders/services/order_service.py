from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import BackgroundTasks

# Repositorios de pedidos e items
from moduls.orders.repositories.order_repository import (
    create_order,
    get_order_by_id,
    get_orders_by_user,
    get_orders_by_store,
    update_order_status
)
from moduls.orders.repositories.order_item_repository import create_order_items_bulk

# Repositorios de productos y variantes
from moduls.products.repositories.product_repository import get_product_by_id
from moduls.products.repositories.product_variant import get_product_variant_by_id

# Repositorios de usuario (Carrito, Direcciones, Tienda)
from moduls.users.repositories.cart_repository import clear_cart
from moduls.users.repositories.adress_repository import get_direction_by_id
from moduls.stores.repositories import select_store_by_id

# Excepciones y Estados
from core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
    ConflictException
)
from moduls.orders.modules import OrderStatus

# --- SERVICIOS PRINCIPALES ---

def create_order_service(db: Session, user_id: str, order_data, background_tasks: BackgroundTasks):
    """
    Crea un pedido, gestiona el stock de forma atómica y vacía el carrito.
    """
    try:
        # 1. Validar dirección
        address = get_direction_by_id(db, order_data.address_id)
        if not address:
            raise NotFoundException("Adresse introuvable")
        if address.user_id != user_id:
            raise ForbiddenException("Accès interdit à cette adresse")

        # 2. Validar que vengan items en la petición
        if not order_data.items:
            raise ValidationException("Le panier est vide")

        items_to_process = []
        total_price = 0

        # 3. Validar Stock y Precios (Sin guardar nada aún)
        for item in order_data.items:
            product = get_product_by_id(db, item.product_id)
            if not product or not product.is_active:
                raise NotFoundException(f"Produit non disponible: {item.product_id}")

            unit_price = product.price

            # Gestión de Variantes
            if item.variant_id:
                variant = get_product_variant_by_id(db, item.variant_id)
                if not variant or variant.product_id != product.id:
                    raise ValidationException("Variante invalide pour ce produit")

                if variant.stock < item.quantity:
                    raise ConflictException(f"Stock insuffisant pour la variante du produit {product.name}")

                # Restamos stock del objeto (SQLAlchemy lo detecta automáticamente)
                variant.stock -= item.quantity
                if variant.price:
                    unit_price = variant.price
            else:
                # Gestión de Producto Simple
                if product.stock < item.quantity:
                    raise ConflictException(f"Stock insuffisant para el producto {product.name}")
                
                product.stock -= item.quantity

            item_total = unit_price * item.quantity
            total_price += item_total

            items_to_process.append({
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": item_total
            })

        # 4. Crear la cabecera del pedido
        order_dict = {
            "user_id": user_id,
            "address_id": order_data.address_id,
            "total_price": total_price,
            "notes": order_data.notes,
            "status": OrderStatus.pending
        }
        order = create_order(db, order_dict)
        db.flush() # Sincroniza para obtener order.id

        # 5. Crear los items del pedido en bulk
        for item in items_to_process:
            item["order_id"] = order.id
        create_order_items_bulk(db, items_to_process)

        # 6. Limpiar carrito y confirmar transacción
        clear_cart(db, user_id)
        
        db.commit()
        db.refresh(order)

        # 7. Tarea de Email en segundo plano (Pendiente de implementar función)
        # background_tasks.add_task(send_order_confirmation_email, user_id, order.id)
        return order

    except Exception as e:
        db.rollback()
        raise e

def cancel_order_service(db: Session, order_id: str, user_id: str):
    """
    Cancela un pedido y DEVUELVE el stock a los productos/variantes.
    """
    order = get_order_by_id(db, order_id)
    if not order:
        raise NotFoundException("Commande introuvable")
    
    if order.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    if order.status not in [OrderStatus.pending, OrderStatus.confirmed]:
        raise ConflictException("La commande ne puede ser cancelada en su estado actual")

    try:
        # Devolver stock de cada item
        for item in order.items:
            if item.variant_id:
                variant = get_product_variant_by_id(db, item.variant_id)
                if variant:
                    variant.stock += item.quantity
            else:
                product = get_product_by_id(db, item.product_id)
                if product:
                    product.stock += item.quantity
        
        updated_order = update_order_status(db, order, OrderStatus.cancelled)
        db.commit()
        return updated_order
    except Exception as e:
        db.rollback()
        raise e

#Gestion de estados y listados

def update_order_status_service(db: Session, order_id: str, status: OrderStatus, current_user_id: str):
    """
    Actualiza el estado del pedido validando el rol de owner y las transiciones permitidas.
    """
    order = get_order_by_id(db, order_id)
    if not order or not order.items:
        raise NotFoundException("Commande introuvable ou vide")

    # Validar que el usuario es el dueño de la tienda (del primer producto)
    first_product = order.items[0].product
    store = select_store_by_id(db, first_product.store_id)
    if not store or store.owner_id != current_user_id:
        raise ForbiddenException("Seul le propriétaire de la boutique peut modifier le statut")

    if order.status in [OrderStatus.delivered, OrderStatus.cancelled]:
        raise ConflictException("Impossible de modifier une commande déjà finalisée")

    # Reglas de transiciones
    valid_transitions = {
        OrderStatus.pending:   [OrderStatus.confirmed, OrderStatus.cancelled],
        OrderStatus.confirmed: [OrderStatus.preparing, OrderStatus.cancelled],
        OrderStatus.preparing: [OrderStatus.shipped, OrderStatus.cancelled],
        OrderStatus.shipped:   [OrderStatus.delivered, OrderStatus.returned],
        OrderStatus.returned:  []
    }

    if status not in valid_transitions.get(order.status, []):
        raise ValidationException(f"Transition de {order.status} vers {status} invalide")

    try:
        updated_order = update_order_status(db, order, status)
        db.commit()
        return updated_order
    except Exception as e:
        db.rollback()
        raise e

def get_orders_by_user_service(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    return get_orders_by_user(db, user_id, skip=skip, limit=limit)

# Metodo para obtener pedido por identificador (el que llama el Router)
def get_order_by_store_service(db: Session, order_id: str, user_id: str):
    """
    Busca un pedido por ID y verifica que pertenezca al usuario que lo solicita.
    """
    # 1. Buscamos el pedido en el repositorio
    order = get_order_by_id(db, order_id)
    
    # 2. Si no existe, lanzamos 404
    if not order:
        raise NotFoundException("Commande introuvable")

    # 3. Comprobamos que el pedido pertenece al usuario (Seguridad)
    if order.user_id != user_id:
        raise ForbiddenException("Vous n'avez no tiene permiso para ver este pedido")

    return order