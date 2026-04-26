from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
#Importamos schemas
from moduls.users.schemas import CartItemCreate, CartItemResponse
#Importamos base de datos
from core.database import get_db
#Importamos servicios
from moduls.users.services.user_products_service import (
    add_item_service,
    get_cart_service,
    update_quantity_service,
    remove_item_service,
    clear_cart_service
)
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User
#Importamos schema para actualizar cantidad
from pydantic import BaseModel

router = APIRouter(tags=["Cart"])

#Endpoint para añadir producto al carrito — protegido
@router.post("/", response_model=CartItemResponse, status_code=201)
def add_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_item_service(
        db,
        current_user.id,
        item_data.product_id,
        item_data.variant_id,
        item_data.quantity
    )

#Endpoint para obtener carrito del usuario — protegido
@router.get("/", response_model=List[CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_cart_service(db, current_user.id)

#Endpoint para actualizar cantidad de un item — protegido
@router.patch("/{item_id}", response_model=CartItemResponse)
def update_quantity(
    item_id: str,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_quantity_service(db, current_user.id, item_id, quantity)

#Endpoint para eliminar item del carrito — protegido
@router.delete("/{item_id}", status_code=204)
def remove_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remove_item_service(db, current_user.id, item_id)

#Endpoint para vaciar carrito completo — protegido
@router.delete("/", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    clear_cart_service(db, current_user.id)