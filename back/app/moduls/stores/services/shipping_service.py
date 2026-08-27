from sqlalchemy.orm import Session
from moduls.stores.repositories import shipping_repository
from moduls.stores.schemas import ShippingRateCreate, BulkShippingUpdate
from core.exceptions import NotFoundException
from moduls.stores.modules import Store
# Importamos el método para re-indexar información cambiada y estar actualizado con los datos
from moduls.ai.services.indexing_service import index_store_service
from core.qdrant import delete_point,delete_store_wilaya_points
import uuid

async def update_store_logistics_service(db: Session, store_id: str, data: BulkShippingUpdate):

    # 1. actualizar partner logístico de la tienda
    store = db.query(Store).filter(Store.id == store_id).first()

    if store:
        store.logistics_partner = data.logistics_partner

    #actualizar tarifas
    updated_rates = []

    for rate_data in data.rates:
        rate = shipping_repository.save_or_update_rate(db, store_id, rate_data)
        updated_rates.append(rate)

    db.commit()

    # Indexamos despues de guardar los nuevos valores en la base de datos
    await index_store_service(db,store_id)

    return updated_rates

def get_all_rates_service(db: Session, store_id: str):
    """Retorna todas las tarifas configuradas por la tienda"""
    return shipping_repository.get_all_store_rates(db, store_id)

async def remove_wilaya_rate_service(db: Session, store_id: str, wilaya_id: int):
    """Elimina la posibilidad de enviar a una Wilaya específica"""
    shipping_repository.delete_shipping_rate(db, store_id, wilaya_id)
    db.commit()
    
    point_id = str(uuid.uuid5(
        uuid.NAMESPACE_DNS,
        f"{store_id}_{wilaya_id}"
    ))

    await delete_point(point_id)

    return {"message": f"Livraison vers la Wilaya {wilaya_id} supprimée"}

async def reset_all_rates_service(db: Session, store_id: str):
    """Borra toda la configuración logística de la tienda"""
    shipping_repository.clear_all_store_rates(db, store_id)
    db.commit()

    # Indexamos despues de realizar los cambios
    await delete_store_wilaya_points(store_id)
    
    return {"message": "Toutes les configurations de livraison ont été réinitialisées"}