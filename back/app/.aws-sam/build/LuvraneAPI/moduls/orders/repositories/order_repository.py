from sqlalchemy.orm import Session
from moduls.orders.modules import Order, OrderStatus 
from datetime import datetime, timezone
# Usamos join con OrderItem y Product para filtrar por store_id de forma eficiente
from moduls.orders.modules import OrderItem
from moduls.products.modules import Product

# Metodo para crear pedido
def create_order(db: Session, order_data: dict) -> Order:
    order = Order(**order_data)
    db.add(order)
    # Eliminamos commit y refresh. El Service hará el commit final.
    return order

# Metodo para obtener pedido por identificador
def get_order_by_id(db: Session, order_id: str) -> Order:
    return db.query(Order).filter(Order.id == order_id).first()

# Metodo para listar pedidos del usuario con paginacion
def get_orders_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> dict:
    query = db.query(Order).filter(Order.user_id == user_id)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "orders": orders}

# Metodo para listar pedidos de una tienda con paginacion (para el owner)
def get_orders_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 20) -> dict:
    query = db.query(Order).join(OrderItem).join(Product).filter(Product.store_id == store_id).distinct()
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "orders": orders}

# Metodo para actualizar estado del pedido
def update_order_status(db: Session, order: Order, status: OrderStatus) -> Order:
    order.status = status

    # Fechas automáticas según el estado
    if status == OrderStatus.delivered:
        order.delivered_at = datetime.now(timezone.utc)
    
    if status == OrderStatus.cancelled:
        order.cancelled_at = datetime.now(timezone.utc)

    # NO hacemos commit aquí. 
    # Lo hará el service después de gestionar el stock en caso de cancelación.
    return order