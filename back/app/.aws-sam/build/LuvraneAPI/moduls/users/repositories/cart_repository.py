from sqlalchemy.orm import Session
from moduls.users.modules import CartItem

# Añadir producto al carrito
def add_cart_item(db: Session, user_id: str, product_id: str, variant_id: str = None, quantity: int = 1) -> CartItem:
    item = CartItem(
        user_id=user_id,
        product_id=product_id,
        variant_id=variant_id,
        quantity=quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Obtener carrito del usuario
def get_cart(db: Session, user_id: str) -> list:
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

#Metodo para seleccionar producto dentro de el carrito
def get_item(db: Session,user_id:str,variant_id: str = None,product_id: str = None):
    #Buscamos segun identificador del producto
    query = db.query(CartItem).filter(CartItem.user_id == user_id,CartItem.product_id == product_id)

    if variant_id:
        query = query.filter(CartItem.variant_id == variant_id)

    return query.first()

# Actualizar cantidad de un item
def update_cart_quantity(db: Session, item_id: str, quantity: int) -> CartItem:
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if item:
        item.quantity = quantity
        db.commit()
        db.refresh(item)
    return item

# Eliminar item del carrito
def remove_cart_item(db: Session, item_id: str) -> None:
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()

# Vaciar carrito completo del usuario
def clear_cart(db: Session, user_id: str) -> None:
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()