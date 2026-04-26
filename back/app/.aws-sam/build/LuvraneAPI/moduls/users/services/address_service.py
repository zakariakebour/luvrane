#Importamos los metodos del repositorio
from moduls.users.repositories.adress_repository import (
    create_directions,
    delete_direction,
    get_directions,
    set_default_direction,
    update_direction,
    get_direction_by_id                                        
)
#Importamos excepciones
from core.exceptions import NotFoundException, ConflictException, ForbiddenException

#Limite maximo de direcciones por usuario
MAX_DIRECTIONS = 5

#Metodo para añadir direccion
def create_directions_service(db, user_id: str, direction_data):
    #Comprobamos que no supere el limite de direcciones
    directions = get_directions(db, user_id)
    if len(directions) >= MAX_DIRECTIONS:
        raise ForbiddenException(f"Maximum {MAX_DIRECTIONS} adresses autorisées")

    #Convertimos a diccionario y añadimos user_id
    direction_dict = direction_data.model_dump()
    direction_dict["user_id"] = user_id

    #Creamos la direccion
    return create_directions(db, direction_dict)

#Metodo para listar direcciones del usuario
def get_directions_service(db, user_id: str):
    return get_directions(db, user_id)

#Metodo para actualizar direccion
def update_direction_service(db, user_id: str, direction_id: str, direction_data):
    #Comprobamos que la direccion existe
    direction = get_direction_by_id(db, direction_id)
    if not direction:
        raise NotFoundException("Adresse introuvable")

    #Comprobamos que la direccion pertenece al usuario
    if direction.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    #Convertimos a diccionario ignorando campos None
    direction_dict = direction_data.model_dump(exclude_none=True)

    return update_direction(db, direction, direction_dict)

#Metodo para eliminar direccion
def delete_direction_service(db, user_id: str, direction_id: str):
    #Comprobamos que la direccion existe
    direction = get_direction_by_id(db, direction_id)
    if not direction:
        raise NotFoundException("Adresse introuvable")

    #Comprobamos que la direccion pertenece al usuario
    if direction.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    #Eliminamos la direccion
    delete_direction(db, direction_id)

#Metodo para asignar direccion por defecto
def set_default_direction_service(db, user_id: str, direction_id: str):
    #Comprobamos que la direccion existe
    direction = get_direction_by_id(db, direction_id)
    if not direction:
        raise NotFoundException("Adresse introuvable")

    #Comprobamos que la direccion pertenece al usuario
    if direction.user_id != user_id:
        raise ForbiddenException("Accès interdit")

    return set_default_direction(db, user_id, direction_id)