#Importamos sesion
from sqlalchemy.orm import Session
#Importamos la clase de la tabla de usuario
from moduls.users.modules import User
from datetime import datetime,timezone

#Metodo que crea un usuario que nos entra un diccionario como parametro
def create_user(db: Session,user_data: dict) -> User:
    user = User(
        **user_data
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

#Metodo para cargar informacion del usuario
def get_user(db: Session,user_id: str) -> User:
    #Devolvemos los datos del usuario seleccionados
    return db.query(User).filter(User.id == user_id).first()

#Metodo para obtener usuario por correo, metodo para login
def get_user_by_email(db: Session,user_email: str) -> User:
    #Devolvemos la consulta con el correo recibido
    return db.query(User).filter(User.email == user_email).first()

#Metodo para modificar datos de el usuario
def update_user(db: Session,user: User,user_data: dict,user_id: str) -> User:
    for field,value in user_data.items():
        if value is not None:
            setattr(user_data,field,value)

    db.commit()
    db.refresh(user_data)
    return user_data

#Metodo para eliminar/desactivar usuario
def delete_user(db: Session,user: User) -> User:
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user

#Metodo para seleccionar usuario segun nombre
def get_user_by_name(db: Session,user_name: str) -> User:
    #Devolvemos la consulta con el nombre de usuario buscado
    return db.query(User).filter(User.username == user_name).first()