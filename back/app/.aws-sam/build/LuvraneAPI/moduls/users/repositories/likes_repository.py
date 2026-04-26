from sqlalchemy.orm import Session
#Importamos tabla de productos
from moduls.users.modules import ProductLike

#Añadir producto al dar like
def add_like(db: Session, user_id: str, product_id: str) -> ProductLike:  
    #Insertamos producto id y usuario id
    like = ProductLike(user_id=user_id, product_id=product_id)            
    db.add(like)
    db.commit()
    db.refresh(like)
    return like

#Metodo para eliminar producto de la lista de productos deseados
def remove_like(db: Session, user_id: str, product_id: str) -> None:
    like = db.query(ProductLike).filter(
        ProductLike.user_id == user_id,                                    
        ProductLike.product_id == product_id
    ).first()
    if like:
        db.delete(like)
        db.commit()

#Listar productos deseados
def get_user_likes(db: Session, user_id: str) -> list:   
    #Devolvemos la consulta                 
    return db.query(ProductLike).filter(ProductLike.user_id == user_id).all()

#Metodo para buscar un like concreto de un usuario a un producto
def get_like(db: Session, user_id: str, product_id: str) -> ProductLike:
    return db.query(ProductLike).filter(
        ProductLike.user_id == user_id,
        ProductLike.product_id == product_id
    ).first()