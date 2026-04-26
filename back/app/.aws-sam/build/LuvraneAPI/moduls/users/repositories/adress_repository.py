#Importamos sesion
from sqlalchemy.orm import Session
#Importamos la clase de la tabla de direccion de usuario
from moduls.users.modules import UserAddress

#Metodo para guardar direcciones de usuario 
def create_directions(db: Session,direction_data: dict) -> UserAddress:
    direction = UserAddress(
        **direction_data
    )
    db.add(direction)
    db.commit()
    db.refresh(direction)
    return direction

#Metodo para listar direcciones del usuario
def get_directions(db: Session,user_id: str) -> list:
    #Realizamos la consulta
    return db.query(UserAddress).filter(UserAddress.user_id == user_id).all()

#Metodo para seleccionar la direccion con el id
def get_direction_by_id(db: Session,direction_id: str):
    #Devolvemos la consulta
    return db.query(UserAddress).filter(UserAddress.id == direction_id).first()

#Creamos metodo para modificar direccion
def update_direction(db: Session,user_adress: UserAddress,direction_data: dict) -> UserAddress:
    for field,value in direction_data.items():
       if value is not None:
           setattr(user_adress,field,value)
    
    db.commit()
    db.refresh(user_adress)

    return user_adress

#Metodo eliminar direccion
def delete_direction(db: Session,direction_id: str) -> None:
    #Hacemos una consulta a la base de datos para la direccion exacta segun el identificador
    direction = db.query(UserAddress).filter(UserAddress.id == direction_id).first()

    #Comprueba
    if direction:
        db.delete(direction)
        db.commit()

#Metodo para asignar direccion por defecto
def set_default_direction(db: Session, user_id: str, direction_id: str) -> UserAddress:  
    # Quitamos default a todas las direcciones del usuario
    db.query(UserAddress).filter(UserAddress.user_id == user_id).update({"is_default": False})
    
    # Marcamos la seleccionada como default
    address = db.query(UserAddress).filter(UserAddress.id == direction_id).first()
    if address:
        address.is_default = True
        db.commit()
        db.refresh(address)
    return address      
