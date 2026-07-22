from fastapi import APIRouter, Depends, HTTPException
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

#Metodo para obtener direccion
@router.post("/", response_model=AddressResponse, status_code=201)
def create_address(
    direction_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_directions_service(db, current_user.id, direction_data)

# 2. SE QUEDA IGUAL: Ahora sí funciona porque ya no se pisa con el de arriba
@router.get("/", response_model=List[AddressResponse])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_directions_service(db, current_user.id)

#Recibir una direccion en especifico
@router.get("/{direction_id}", response_model=AddressResponse)
def get_address_by_id(
    direction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Buscamos todas las direcciones del usuario
    addresses = get_directions_service(db, current_user.id)
    # Filtramos en memoria la que coincide con la ID solicitada
    address = next((addr for addr in addresses if addr.id == direction_id), None)
    
    if not address:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return address

# 4. SE QUEDA IGUAL: Endpoint para actualizar direccion
@router.put("/{direction_id}", response_model=AddressResponse)
def update_address(
    direction_id: str,
    direction_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_direction_service(db, current_user.id, direction_id, direction_data)

# 5. SE QUEDA IGUAL: Endpoint para marcar direccion como principal
@router.patch("/{direction_id}/default", response_model=AddressResponse)
def set_default(
    direction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return set_default_direction_service(db, current_user.id, direction_id)

# 6. SE QUEDA IGUAL: Endpoint para eliminar direccion
@router.delete("/{direction_id}", status_code=204)
def delete_address(
    direction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_direction_service(db, current_user.id, direction_id)