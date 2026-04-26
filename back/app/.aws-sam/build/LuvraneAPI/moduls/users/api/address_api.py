from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
#Importamos schemas
from moduls.users.schemas import AddressCreate, AddressResponse
#Importamos base de datos
from core.database import get_db
#Importamos servicios
from moduls.users.services.address_service import (
    create_directions_service,
    get_directions_service,
    update_direction_service,
    delete_direction_service,
    set_default_direction_service
)
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User

router = APIRouter(tags=["Addresses"])

#Endpoint para añadir direccion — protegido
@router.post("/", response_model=AddressResponse, status_code=201)
def create_address(
    direction_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_directions_service(db, current_user.id, direction_data)

#Endpoint para listar direcciones del usuario — protegido
@router.get("/", response_model=List[AddressResponse])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_directions_service(db, current_user.id)

#Endpoint para actualizar direccion — protegido
@router.put("/{direction_id}", response_model=AddressResponse)
def update_address(
    direction_id: str,
    direction_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_direction_service(db, current_user.id, direction_id, direction_data)

#Endpoint para marcar direccion como principal — protegido
@router.patch("/{direction_id}/default", response_model=AddressResponse)
def set_default(
    direction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return set_default_direction_service(db, current_user.id, direction_id)

#Endpoint para eliminar direccion — protegido
@router.delete("/{direction_id}", status_code=204)
def delete_address(
    direction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_direction_service(db, current_user.id, direction_id)