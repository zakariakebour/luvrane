from sqlalchemy.orm import Session, joinedload
from moduls.orders.modules import Order, OrderItem, OrderStatus
from datetime import datetime, timezone
from moduls.products.modules import Product, ProductVariant
from moduls.users.modules import UserAddress

# Metodo para crear pedido
def create_order(db: Session, order_data: dict) -> Order:
    order = Order(**order_data)
    db.add(order)
    return order

# Metodo para obtener pedido por identificador
def get_order_by_id(db: Session, order_id: str) -> Order:
    return (
        db.query(Order)
        .options(
            joinedload(Order.address_rel).joinedload(UserAddress.wilaya),
            # Quitamos el joinedload de address porque ahora es una @property dinámica
            joinedload(Order.items).options(
                joinedload(OrderItem.product).joinedload(Product.images),
                joinedload(OrderItem.variant).options(
                    joinedload(ProductVariant.images),
                    joinedload(ProductVariant.color),
                    joinedload(ProductVariant.size)
                )
            )
        )
        .filter(Order.id == order_id)
        .first()
    )

# Metodo para listar pedidos del usuario con paginacion
def get_orders_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> dict:
    query = db.query(Order).filter(Order.user_id == user_id)
    total = query.count()
    
    orders = (
        query.options(
            joinedload(Order.address_rel).joinedload(UserAddress.wilaya),
            # Quitamos el joinedload de address aquí también
            joinedload(Order.items).options(
                joinedload(OrderItem.product).joinedload(Product.images),
                joinedload(OrderItem.variant).options(
                    joinedload(ProductVariant.images),
                    joinedload(ProductVariant.color),
                    joinedload(ProductVariant.size)
                )
            )
        )
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return {"total": total, "orders": orders}

# Metodo para listar pedidos de una tienda
def get_orders_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 20) -> dict:
    query = db.query(Order).filter(Order.store_id == store_id)
    total = query.count()
    
    orders = (
        query.options(
            joinedload(Order.address_rel).joinedload(UserAddress.wilaya),
            # Quitamos el joinedload de address aquí también
            joinedload(Order.items).options(
                joinedload(OrderItem.product).joinedload(Product.images),
                joinedload(OrderItem.variant).options(
                    joinedload(ProductVariant.images),
                    joinedload(ProductVariant.color),
                    joinedload(ProductVariant.size)
                )
            )
        )
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"total": total, "orders": orders}

# Metodo para actualizar estado del pedido con hitos temporales
def update_order_status(db: Session, order: Order, status: OrderStatus, tracking_number: str = None) -> Order:
    order.status = status
    now = datetime.now(timezone.utc)
    
    if status.value == OrderStatus.confirmed.value:
        order.confirmed_at = now
    elif status.value == OrderStatus.shipped.value:
        order.shipped_at = now
        if tracking_number:
            order.tracking_number = tracking_number
    elif status.value == OrderStatus.delivered.value:
        order.delivered_at = now
    elif status.value == OrderStatus.cancelled.value:
        order.cancelled_at = now

    return order

def get_orders_by_checkout_session(db: Session, session_id: str):
    return db.query(Order).filter(
        Order.checkout_session_id == session_id
    ).all()