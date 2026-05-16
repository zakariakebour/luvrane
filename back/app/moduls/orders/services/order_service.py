from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from datetime import datetime, timezone, timedelta
import secrets
from core.order_email_service import send_order_email

from moduls.orders.repositories.order_repository import (
    create_order,
    get_order_by_id,
    get_orders_by_user,
    update_order_status
)

from moduls.orders.repositories.checkout_session_repository import (
    create_checkout_session
)

from moduls.orders.repositories.order_item_repository import (
    create_order_items_bulk
)
from moduls.products.repositories.product_repository import (
    get_product_by_id
)

from moduls.products.repositories.product_variant import (
    get_product_variant_by_id
)
from moduls.users.repositories.cart_repository import clear_cart

from moduls.users.repositories.address_repository import (
    get_direction_by_id
)
from moduls.stores.repositories.repositories import (
    select_store_by_id
)
from moduls.users.repositories.user_repository import (
    get_user_by_id
)
from core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
    ConflictException
)
# Mover CheckoutSession aquí arriba evita problemas de importación en caliente dentro de AWS Lambda
from moduls.orders.modules import OrderStatus, Order, CheckoutSession
from moduls.stores.repositories.shipping_repository import get_shipping_rate

def create_order_service(
    db: Session,
    user_id: str,
    order_data,
    background_tasks: BackgroundTasks
):
    try:
        # --- CORRECCIÓN 1: Controlar órdenes pendientes reales o limpiar expiradas ---
        existing_pending = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.pending_email_confirmation
        ).first()

        if existing_pending:
            # Comprobamos si la sesión de esa orden ya expiró en lugar de bloquear siempre
            
            session_viejita = db.query(CheckoutSession).filter(CheckoutSession.id == existing_pending.checkout_session_id).first()
            
            if session_viejita:
                # --- SOLUCIÓN SEGURA DE TIMEZONE ---
                old_expires = session_viejita.expires_at
                if old_expires.tzinfo is None:
                    old_expires = old_expires.replace(tzinfo=timezone.utc)
                
                if old_expires < datetime.now(timezone.utc):
                    # Si expiró, cambiamos el estado de la orden vieja a cancelada para liberar al usuario
                    existing_pending.status = OrderStatus.cancelled
                    db.flush()
                else:
                    raise ConflictException("Une commande en attente de confirmation existe déjà")
            else:
                raise ConflictException("Une commande en attente de confirmation existe déjà")

        token = secrets.token_urlsafe(32)

        checkout_session = create_checkout_session(db, {
            "user_id": user_id,
            "confirmation_token": token,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)
        })

        db.flush()

        address = get_direction_by_id(db, order_data.address_id)
        if not address:
            raise NotFoundException("L'adresse n'existe pas")

        if address.user_id != user_id:
            raise ForbiddenException("Accès interdit à cette adresse")

        wilaya_id = address.wilaya_id

        if not address.is_default:
            raise ValidationException(
                "Cette adresse n'est pas activé. Veuillez en choisir une autre."
            )
        
        orders_by_store = {}

        for item in order_data.items:
            product = get_product_by_id(db, item.product_id)

            if not product or not product.is_active:
                raise NotFoundException(
                    f"Producto no disponible: {item.product_id}"
                )

            store_id = product.store_id

            if store_id not in orders_by_store:
                orders_by_store[store_id] = {
                    "items": [],
                    "total_price": 0
                }

            unit_price = product.price

            if item.variant_id:
                variant = get_product_variant_by_id(db, item.variant_id)

                if not variant or variant.stock < item.quantity:
                    raise ConflictException(
                        f"Stock insuffisant en variante de {product.name}"
                    )

                unit_price = variant.price if variant.price else unit_price
                
                # --- CORRECCIÓN 2: Restamos el Stock de la variante ---
                variant.stock -= item.quantity
            else:
                if product.stock < item.quantity:
                    raise ConflictException(
                        f"Stock insuffisant pour {product.name}"
                    )
                
                # --- CORRECCIÓN 2: Restamos el Stock del producto base ---
                product.stock -= item.quantity

            item_total = unit_price * item.quantity
            orders_by_store[store_id]["total_price"] += item_total

            orders_by_store[store_id]["items"].append({
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": item_total
            })

        created_orders = []

        for store_id, store_data in orders_by_store.items():
            shipping_rate = get_shipping_rate(db, store_id, wilaya_id)

            if not shipping_rate:
                raise ValidationException(
                    "Cette boutique ne livre pas dans votre wilaya"
                )

            shipping_cost = shipping_rate.delivery_price

            order = create_order(db, {
                "user_id": user_id,
                "address_id": order_data.address_id,
                "store_id": store_id,
                "checkout_session_id": checkout_session.id,
                "total_price": store_data["total_price"] + shipping_cost,
                "shipping_price": shipping_cost,
                "notes": order_data.notes,
                "status": OrderStatus.pending_email_confirmation
            })

            db.flush()

            items_to_process = []
            for item in store_data["items"]:
                item["order_id"] = order.id
                items_to_process.append(item)

            create_order_items_bulk(db, items_to_process)
            created_orders.append(order)

        db.commit()

        for order in created_orders:
            db.refresh(order)

        customer = get_user_by_id(db, user_id)

        background_tasks.add_task(
            send_order_email,
            customer.email,
            "order_received",
            created_orders,
            getattr(address, "full_name", None) or "Client",
            confirmation_token=token
        )

        for order in created_orders:
            store = select_store_by_id(db, order.store_id)
            owner = get_user_by_id(db, store.owner_id)

            background_tasks.add_task(
                send_order_email,
                owner.email,
                "new_order_admin",
                order
            )

        return created_orders

    except Exception as e:
        db.rollback()
        raise e
    
def update_order_status_service(
    db: Session,
    order_id: str,
    new_status: OrderStatus,
    current_user_id: str,
    background_tasks: BackgroundTasks,
    tracking_number: str = None
):

    order = get_order_by_id(db, order_id)

    if not order:
        raise NotFoundException("Pedido no encontrado")

    store = select_store_by_id(db, order.store_id)

    if store.owner_id != current_user_id:
        raise ForbiddenException("No eres el dueño de esta tienda")

    updated_order = update_order_status(
        db,
        order,
        new_status,
        tracking_number
    )

    db.commit()

    customer = get_user_by_id(db, order.user_id)

    address = get_direction_by_id(db, order.address_id)

    background_tasks.add_task(
        send_order_email,
        customer.email,
        f"order_{new_status.value}",
        updated_order,
        getattr(address, "full_name", None) or "Client",
    )

    return updated_order

#Metodo para obtener todos los pedidos de usuario con sus estados actuales
def get_orders_by_user_service(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20
):
    result = get_orders_by_user(
        db,
        user_id,
        skip,
        limit
    )

    return {
        "orders": result["orders"],
        "total": result["total"]
    }

def get_orders_by_store_service(
    db: Session,
    store_id: str,
    user_id: str,
    skip: int = 0,
    limit: int = 20
):

    store = select_store_by_id(db, store_id)

    if not store or store.owner_id != user_id:
        raise ForbiddenException(
            "Accès interdit a cette boutique"
        )

    from moduls.orders.repositories.order_repository import get_orders_by_store

    orders, total = get_orders_by_store(
        db,
        store_id,
        skip,
        limit
    )

    return {
        "orders": orders,
        "total": total
    }

def get_order_by_id_service(
    db: Session,
    order_id: str,
    user_id: str
):

    order = get_order_by_id(db, order_id)

    if not order:
        raise NotFoundException("Commande non trouvée")

    store = select_store_by_id(db, order.store_id)

    if order.user_id != user_id and store.owner_id != user_id:
        raise ForbiddenException(
            "Pas d'autorisation pour voir cette commande"
        )

    return order


def cancel_order_service(
    db: Session,
    order_id: str,
    user_id: str,
    background_tasks: BackgroundTasks
):

    order = get_order_by_id(db, order_id)

    if not order:
        raise NotFoundException("Commande non trouvée")

    if order.status not in {OrderStatus.pending, OrderStatus.pending_email_confirmation}:
        raise ValidationException(
            "La commande ne peut plus être annulée"
        )

    if order.user_id != user_id:
        raise ForbiddenException("Accès refusé")

    order.status = OrderStatus.cancelled

    for item in order.items:

        product = get_product_by_id(db, item.product_id)

        if item.variant_id:

            variant = get_product_variant_by_id(
                db,
                item.variant_id
            )

            variant.stock += item.quantity

        else:
            product.stock += item.quantity

    db.commit()

    customer = get_user_by_id(db, order.user_id)

    address = get_direction_by_id(db, order.address_id)

    background_tasks.add_task(
        send_order_email,
        customer.email,
        "order_cancelled",
        order,
        getattr(address, "full_name", None) or "Client",
    )

    return order