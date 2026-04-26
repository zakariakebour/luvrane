from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
#Importamos schemas
from moduls.orders.schemas import OrderCreate, OrderResponse, OrderUpdateStatus, OrdersPageResponse
#Importamos servicios
from moduls.orders.services.order_service import (
    create_order_service,
    get_order_by_id_service,
    get_orders_by_user_service,
    get_orders_by_store_service,
    update_order_status_service,
    cancel_order_service
)
#Importamos base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User

router = APIRouter(tags=["Orders"])

#Endpoint para crear pedido — protegido
@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_order_service(db, current_user.id, order_data)

#Endpoint para listar pedidos del usuario — protegido
@router.get("/me", response_model=OrdersPageResponse)
def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_orders_by_user_service(db, current_user.id, skip=skip, limit=limit)

#Endpoint para obtener pedido por identificador — protegido
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_order_by_id_service(db, order_id, current_user.id)

#Endpoint para listar pedidos de una tienda (owner) — protegido
@router.get("/store/{store_id}", response_model=OrdersPageResponse)
def get_store_orders(
    store_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_orders_by_store_service(db, store_id, current_user.id, skip=skip, limit=limit)

#Endpoint para actualizar estado del pedido (owner) — protegido
@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status_data: OrderUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_order_status_service(db, order_id, status_data.status, current_user.id)

#Endpoint para cancelar pedido (usuario) — protegido
@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cancel_order_service(db, order_id, current_user.id)