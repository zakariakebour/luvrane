from sqlalchemy.orm import Session
from moduls.orders.modules import Order, OrderStatus 
from datetime import datetime, timezone

# Metodo para crear pedido
def create_order(db: Session, order_data: dict) -> Order:
    order = Order(**order_data)
    db.add(order)
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

# Metodo para listar pedidos de una tienda
def get_orders_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 20) -> dict:
    # Filtro directo por store_id, mucho más rápido que los joins anteriores
    query = db.query(Order).filter(Order.store_id == store_id)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "orders": orders}

# Metodo para actualizar estado del pedido con hitos temporales
def update_order_status(db: Session, order: Order, status: OrderStatus, tracking_number: str = None) -> Order:
    order.status = status
    
    # Actualización de hitos para los correos de SES
    now = datetime.now(timezone.utc)
    
    if status == OrderStatus.confirmed:
        order.confirmed_at = now
        
    elif status == OrderStatus.shipped:
        order.shipped_at = now
        if tracking_number:
            order.tracking_number = tracking_number
            
    elif status == OrderStatus.delivered:
        order.delivered_at = now
        
    elif status == OrderStatus.cancelled:
        order.cancelled_at = now

    # El commit lo hará el Service tras disparar SES o gestionar stock
    return order

def get_orders_by_checkout_session(db: Session, session_id: str):
    return db.query(Order).filter(
        Order.checkout_session_id == session_id
    ).all()