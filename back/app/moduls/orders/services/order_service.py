from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from datetime import datetime, timezone

# Importamos tu futura utilidad de SES (la definimos abajo)
from core.email_service import send_order_email

from moduls.orders.repositories.order_repository import (
    create_order, get_order_by_id, get_orders_by_user, update_order_status
)
from moduls.orders.repositories.order_item_repository import create_order_items_bulk
from moduls.products.repositories.product_repository import get_product_by_id
from moduls.products.repositories.product_variant import get_product_variant_by_id
from moduls.users.repositories.cart_repository import clear_cart
from moduls.users.repositories.adress_repository import get_direction_by_id
from moduls.stores.repositories import select_store_by_id
#Importamos el id del usuario porque es necesario para email
from moduls.users.repositories.user_repository import get_user_by_id 

from core.exceptions import NotFoundException, ForbiddenException, ValidationException, ConflictException
from moduls.orders.modules import OrderStatus

def create_order_service(db: Session, user_id: str, order_data, background_tasks: BackgroundTasks):
    try:
        #Validar dirección
        address = get_direction_by_id(db, order_data.address_id)
        if not address or address.user_id != user_id:
            raise ForbiddenException("Dirección no válida")

        items_to_process = []
        total_price = 0
        store_id = None

        #Validar Stock, Precios y obtener el store_id
        for item in order_data.items:
            product = get_product_by_id(db, item.product_id)
            if not product or not product.is_active:
                raise NotFoundException(f"Producto no disponible: {item.product_id}")
            
            # Guardamos el store_id del primer producto (asumiendo 1 tienda por pedido)
            if not store_id:
                store_id = product.store_id

            unit_price = product.price
            if item.variant_id:
                variant = get_product_variant_by_id(db, item.variant_id)
                if not variant or variant.stock < item.quantity:
                    raise ConflictException(f"Stock insuficiente en variante de {product.name}")
                variant.stock -= item.quantity
                unit_price = variant.price if variant.price else unit_price
            else:
                if product.stock < item.quantity:
                    raise ConflictException(f"Stock insuficiente para {product.name}")
                product.stock -= item.quantity

            item_total = unit_price * item.quantity
            total_price += item_total
            items_to_process.append({
                "product_id": item.product_id, "variant_id": item.variant_id,
                "quantity": item.quantity, "unit_price": unit_price, "total_price": item_total
            })

        #Crear cabecera con el store_id directo (para el panel del dueño)
        order = create_order(db, {
            "user_id": user_id, "address_id": order_data.address_id,
            "store_id": store_id, "total_price": total_price,
            "notes": order_data.notes, "status": OrderStatus.pending
        })
        db.flush()

        #Crear items y limpiar carrito
        for item in items_to_process: item["order_id"] = order.id
        create_order_items_bulk(db, items_to_process)
        clear_cart(db, user_id)
        
        db.commit()
        db.refresh(order)

        #Norificaciones SES
        customer = get_user_by_id(db, user_id)
        store = select_store_by_id(db, store_id)
        owner = get_user_by_id(db, store.owner_id)

        # Al Cliente: "Hemos recibido tu pedido, espera confirmación"
        background_tasks.add_task(send_order_email, customer.email, "order_received", order)
        # Al Dueño: "Tienes un nuevo pedido pendiente de confirmar"
        background_tasks.add_task(send_order_email, owner.email, "new_order_admin", order)

        return order
    except Exception as e:
        db.rollback()
        raise e

def update_order_status_service(db: Session, order_id: str, new_status: OrderStatus, current_user_id: str, background_tasks: BackgroundTasks, tracking_number: str = None):
    order = get_order_by_id(db, order_id)
    if not order: raise NotFoundException("Pedido no encontrado")

    store = select_store_by_id(db, order.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("No eres el dueño de esta tienda")

    # Lógica de actualización (incluyendo tracking si es 'shipped')
    updated_order = update_order_status(db, order, new_status, tracking_number)
    db.commit()

    #Notificacion de cambio de estado
    customer = get_user_by_id(db, order.user_id)
    # Enviamos correo al cliente informando del nuevo estado (confirmed, shipped, etc.)
    background_tasks.add_task(send_order_email, customer.email, f"order_{new_status.value}", updated_order)

    return updated_order
