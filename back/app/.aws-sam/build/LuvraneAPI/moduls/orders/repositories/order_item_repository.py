from sqlalchemy.orm import Session
from moduls.orders.modules import OrderItem

#Metodo para crear item del pedido
def create_order_item(db: Session, item_data: dict) -> OrderItem:
    item = OrderItem(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

#Metodo para obtener items de un pedido
def get_items_by_order(db: Session, order_id: str) -> list:
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

#Metodo para crear multiples items de un pedido en una sola operacion
def create_order_items_bulk(db: Session, items_data: list) -> list:
    items = [OrderItem(**item) for item in items_data]
    db.add_all(items)
    db.commit()
    return items