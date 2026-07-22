from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

# Importamos schemas
from moduls.orders.schemas import (
    OrderCreate,
    OrderResponse,
    OrderUpdateStatus,
    OrdersPageResponse
)

# Importamos servicios
from moduls.orders.services.order_service import (
    create_order_service,
    get_orders_by_user_service,
    get_orders_by_store_service,
    get_order_by_id_service,
    update_order_status_service,
    cancel_order_service,
)

#Servicio de confirmación checkout
from moduls.orders.services.chek_item_service import (
    confirm_checkout_service
)

# Importamos infraestructura
from core.database import get_db
from core.dependencies import get_current_user

from moduls.users.modules import User
from typing import List

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

#Crear pedido (Cliente)
@router.post(
    "/",
    response_model=List[OrderResponse],
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_order_service(
        db,
        current_user.id,
        order_data,
        background_tasks,
        current_user=current_user
    )

#Para confirmar correo
@router.post("/confirm/{token}")
def confirm_checkout(
    token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return confirm_checkout_service(
        db,
        token,
        background_tasks
    )

# 3. Listar mis compras (Cliente)
@router.get(
    "/me",
    response_model=OrdersPageResponse
)
def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_orders_by_user_service(
        db,
        current_user.id,
        skip=skip,
        limit=limit
    )

    return {
        "total": result["total"],
        "orders": result["orders"],
        "skip": skip,
        "limit": limit
    }

# 4. Listar ventas de mi tienda (Dueño)
@router.get(
    "/store/{store_id}",
    response_model=OrdersPageResponse
)
def get_store_orders(
    store_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_orders_by_store_service(
        db,
        store_id,
        current_user.id,
        skip=skip,
        limit=limit
    )

    return {
        "total": result["total"],
        "orders": result["orders"],
        "skip": skip,
        "limit": limit
    }

# 5. Actualizar estado y enviar emails (Dueño)
@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status(
    order_id: str,
    status_data: OrderUpdateStatus,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Pasamos tracking_number si viene en el body
    return update_order_status_service(
        db,
        order_id,
        status_data.status,
        current_user.id,
        background_tasks,
        tracking_number=status_data.tracking_number
    )

#Cancelar pedido (Cliente/Dueño)
@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
def cancel_order(
    order_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cancel_order_service(
        db,
        order_id,
        current_user.id,
        background_tasks
    )

# 7. Obtener detalle de un pedido (Cliente o Dueño)
@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_order_by_id_service(
        db,
        order_id,
        current_user.id
    )