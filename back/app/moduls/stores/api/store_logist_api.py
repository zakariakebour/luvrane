from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
from core.qdrant import delete_point
# Importamos esquemas y servicios
from moduls.stores.schemas import ShippingRateResponse, BulkShippingUpdate
from moduls.stores.services.shipping_service import (
    update_store_logistics_service,
    get_all_rates_service,
    remove_wilaya_rate_service
)
from moduls.stores.modules import Store
from moduls.ai.services.indexing_service import index_store_service

# Infraestructura
from core.database import get_db
from core.dependencies import get_current_user
from moduls.users.modules import User

router = APIRouter(tags=["Store Logistics"])

# 1. Obtener todas las tarifas (Para cargar la tabla en el panel)
@router.get("/me/shipping", response_model=List[ShippingRateResponse])
def get_my_shipping_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    return get_all_rates_service(db, store.id)

# 2. Actualización Masiva (El botón "Guardar Cambios" del panel)
@router.post("/me/shipping/bulk", response_model=List[ShippingRateResponse])
def update_shipping_rates(
    data: BulkShippingUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    # Guardamos los cambios en la base de datos
    result = update_store_logistics_service(db, store.id, data)

    # Re-indexamos en background sin bloquear la respuesta
    background_tasks.add_task(
        index_store_service,
        db,
        store.id
    )

    return result

# 3. Eliminar una Wilaya específica
@router.delete("/me/shipping/{wilaya_id}")
async def delete_wilaya_rate(
    wilaya_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    # Borramos la tarifa de la base de datos
    result = remove_wilaya_rate_service(db, store.id, wilaya_id)

    # Calculamos el point_id y borramos de Qdrant en background
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{store.id}_{wilaya_id}"))
    background_tasks.add_task(delete_point, point_id)

    return result