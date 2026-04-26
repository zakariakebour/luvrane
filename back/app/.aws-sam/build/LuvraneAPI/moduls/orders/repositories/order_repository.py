from sqlalchemy.orm import Session
from moduls.orders.modules import Order, OrderStatus
from datetime import datetime, timezone

#Metodo para crear pedido
def create_order(db: Session, order_data: dict) -> Order:
    order = Order(**order_data)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

#Metodo para obtener pedido por identificador
def get_order_by_id(db: Session, order_id: str) -> Order:
    return db.query(Order).filter(Order.id == order_id).first()

#Metodo para listar pedidos del usuario con paginacion
def get_orders_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> dict:
    #Total de pedidos del usuario
    total = db.query(Order).filter(Order.user_id == user_id).count()

    #Pedidos del usuario con paginacion
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).offset(skip).limit(limit).all()

    return {"total": total, "orders": orders}

#Metodo para listar pedidos de una tienda con paginacion (para el owner)
def get_orders_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 20) -> dict:
    #Total de pedidos de la tienda
    total = db.query(Order).join(Order.items).filter(
        Order.items.any(product_id=store_id)
    ).count()

    #Pedidos de la tienda con paginacion
    orders = db.query(Order).join(Order.items).filter(
        Order.items.any(product_id=store_id)
    ).offset(skip).limit(limit).all()

    return {"total": total, "orders": orders}

#Metodo para actualizar estado del pedido
def update_order_status(db: Session, order: Order, status: OrderStatus) -> Order:
    order.status = status

    #Si el pedido fue entregado guardamos la fecha
    if status == OrderStatus.delivered:
        order.delivered_at = datetime.now(timezone.utc)

    #Si el pedido fue cancelado guardamos la fecha
    if status == OrderStatus.cancelled:
        order.cancelled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order)
    return order