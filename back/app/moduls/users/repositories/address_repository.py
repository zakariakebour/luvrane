# Importamos sesión y joinedload para las consultas cruzadas
from sqlalchemy.orm import Session, joinedload
# Importamos las clases de tus tablas
from moduls.users.modules import UserAddress, Wilaya

# Método para guardar direcciones de usuario 
def create_directions(db: Session, direction_data: dict) -> UserAddress:
    direction = UserAddress(**direction_data)
    db.add(direction)
    db.commit()
    
    # incluyendo la relación de la wilaya para que Pydantic no reciba un null
    return db.query(UserAddress)\
        .options(joinedload(UserAddress.wilaya))\
        .filter(UserAddress.id == direction.id)\
        .first()

# Método para listar direcciones del usuario
def get_directions(db: Session, user_id: str) -> list:
    # Agregamos joinedload para que traiga los nombres de las Wilayas automáticamente
    return db.query(UserAddress)\
        .options(joinedload(UserAddress.wilaya))\
        .filter(UserAddress.user_id == user_id)\
        .all()

# Método para seleccionar la dirección con el id
def get_direction_by_id(db: Session, direction_id: str):
    # Agregamos joinedload aquí también por si el endpoint de ver un pedido usa este método
    return db.query(UserAddress)\
        .options(joinedload(UserAddress.wilaya))\
        .filter(UserAddress.id == direction_id)\
        .first()

# Creamos método para modificar dirección
def update_direction(db: Session, user_address: UserAddress, direction_data: dict) -> UserAddress:
    for field, value in direction_data.items():
        if value is not None:
            setattr(user_address, field, value)
    
    db.commit()
    
    # Hacemos un refresh forzado cargando la relación para actualizar el esquema de salida
    return db.query(UserAddress)\
        .options(joinedload(UserAddress.wilaya))\
        .filter(UserAddress.id == user_address.id)\
        .first()

# Método eliminar dirección
def delete_direction(db: Session, direction_id: str) -> None:
    direction = db.query(UserAddress).filter(UserAddress.id == direction_id).first()
    if direction:
        db.delete(direction)
        db.commit()

# Método para asignar dirección por defecto
def set_default_direction(db: Session, user_id: str, direction_id: str) -> UserAddress:  
    # Quitamos default a todas las direcciones del usuario
    db.query(UserAddress).filter(UserAddress.user_id == user_id).update({"is_default": False})
    
    # Marcamos la seleccionada como default y cargamos su relación de Wilaya
    address = db.query(UserAddress)\
        .options(joinedload(UserAddress.wilaya))\
        .filter(UserAddress.id == direction_id)\
        .first()
        
    if address:
        address.is_default = True
        db.commit()
        db.refresh(address)
    return address