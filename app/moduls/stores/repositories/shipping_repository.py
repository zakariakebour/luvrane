from sqlalchemy.orm import Session
from moduls.stores.modules import ShippingRate
from core.exceptions import NotFoundException
import uuid

#
def save_or_update_rate(db: Session, store_id: str, rate_data):
    """
    Busca si ya existe una tarifa para esa Wilaya. 
    Si existe, la actualiza. Si no, la crea.
    """
    existing_rate = db.query(ShippingRate).filter(
        ShippingRate.store_id == store_id,
        ShippingRate.wilaya_id == rate_data.wilaya_id
    ).first()

    if existing_rate:
        existing_rate.delivery_price = rate_data.delivery_price
        existing_rate.office_price = rate_data.office_price
        existing_rate.estimated_days = rate_data.estimated_days
        existing_rate.return_price = rate_data.return_price
        existing_rate.is_active = True
        return existing_rate
    else:
        #Nueva entrada
        new_rate = ShippingRate(
            id=str(uuid.uuid4()),
            store_id=store_id,
            wilaya_id=rate_data.wilaya_id,
            wilaya_name=rate_data.wilaya_name,
            delivery_price=rate_data.delivery_price,
            office_price=rate_data.office_price,
            estimated_days=rate_data.estimated_days,
            return_price=rate_data.return_price
        )
        db.add(new_rate)
        return new_rate

# Eliminar (Fisico como logico)
def delete_shipping_rate(db: Session, store_id: str, wilaya_id: int):
    """
    Elimina la tarifa de una Wilaya específica para esa tienda.
    """
    rate = db.query(ShippingRate).filter(
        ShippingRate.store_id == store_id,
        ShippingRate.wilaya_id == wilaya_id
    ).first()
    
    if not rate:
        raise NotFoundException("Tarif non trouvé pour cette Wilaya")
    
    db.delete(rate)
    return True

#Eliminar todo
def clear_all_store_rates(db: Session, store_id: str):
    """
    Borra todas las tarifas de la tienda (útil si el dueño quiere resetear todo).
    """
    db.query(ShippingRate).filter(ShippingRate.store_id == store_id).delete()
    return True

#Listar todos los precios de wilayas de las tiendas
def get_all_store_rates(db: Session, store_id: str):
    """
    Devuelve todas las tarifas de una tienda
    """
    return db.query(ShippingRate).filter(
        ShippingRate.store_id == store_id
    ).all()

#Metodo para obtener precio de envio
def get_shipping_rate(
    db: Session,
    store_id: str,
    wilaya_id: int
):
    return (
        db.query(ShippingRate)
        .filter(
            ShippingRate.store_id == store_id,
            ShippingRate.wilaya_id == wilaya_id,
            ShippingRate.is_active == True
        )
        .first()
    )