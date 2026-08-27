from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

# Importamos esquemas y servicios
from moduls.stores.schemas import ShippingRateResponse, BulkShippingUpdate
from moduls.stores.services.shipping_service import (
    update_store_logistics_service,
    get_all_rates_service,
    remove_wilaya_rate_service
)
from moduls.stores.modules import Store

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
    # Asumimos que el user tiene un store_id asociado
    return get_all_rates_service(db,store.id)

# 2. Actualización Masiva (El botón "Guardar Cambios" del panel)
@router.post("/me/shipping/bulk", response_model=List[ShippingRateResponse])
async def update_shipping_rates(
    data: BulkShippingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    return await update_store_logistics_service(db,store.id, data)

# 3. Eliminar una Wilaya específica
@router.delete("/me/shipping/{wilaya_id}")
async def delete_wilaya_rate(
    wilaya_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()
    return await remove_wilaya_rate_service(db, store.id, wilaya_id)