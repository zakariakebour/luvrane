# Importamos el método para sacar la infórmacion de las tiendas segun el identificador
from moduls.stores.repositories.repositories import select_store_by_id
from core.exceptions import NotFoundException
# Importamos el método para generar embbedings
from core.gemini import generate_embedding
# Importamos el metodo upsert_point 
from core.qdrant import upsert_point
# Importamos el metodo para obtener todas las tarifas de una tienda
from moduls.stores.repositories.shipping_repository import get_all_store_rates
# Importamos uuid para generar identificadores unicos para cada punto
import uuid

# Método para indexar la tienda
async def index_store_service(db, store_id: str):
    # Antes de cargar los datos comprobamos si exsiste la tienda
    store = select_store_by_id(db, store_id)

    # Si no exsiste
    if not store:
        raise NotFoundException("Store not found")

    # Construyimos texto con los datos de la tienda
    text = f"""
        Store: {store.name}
        Description: {store.description or 'Without description'}
        Type: {store.type}
        Category: {store.category.value if store.category else 'Without category'}
        Logistics: {store.logistics_partner or 'Without logistics'}
    """

    # Generamos el embedding del texto
    vector = await generate_embedding(text)

    # Guardamos el vector en Qdrant con los metadatos de la tienda
    await upsert_point(
        point_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, store.id)),
        vector=vector,
        payload={
            "store_id": store.id,
            "name": store.name,
            "type": store.type,
            "Description": store.description,
            "category": store.category.value if store.category else None,
            "logistics_partner": store.logistics_partner or None
        }
    )

    # Cargamos todas las tarifas de la tienda
    rates = get_all_store_rates(db, store_id)

    # Creamos un chunk separado por cada wilaya
    for rate in rates:

        # Construimos texto con los datos de la wilaya
        wilaya_text = f"""
            Store: {store.name}
            Wilaya: {rate.wilaya_name} ({rate.wilaya_id})
            Precio domicilio: {rate.delivery_price} DA
            Precio bureau: {rate.office_price or 'No disponible'} DA
            Días estimados: {rate.estimated_days or 'No especificado'}
        """

        # Generamos embedding del chunk de wilaya
        wilaya_vector = await generate_embedding(wilaya_text)

        # Guardamos en Qdrant con un id unico por wilaya usando uuid5
        # uuid5 genera siempre el mismo UUID para la misma combinacion de store_id + wilaya_id
        # esto permite actualizar el punto si se re-indexa sin duplicar
        await upsert_point(
            point_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{store.id}_{rate.wilaya_id}")),
            vector=wilaya_vector,
            payload={
                "store_id": store.id,
                "name": store.name,
                "wilaya_id": rate.wilaya_id,
                "wilaya_name": rate.wilaya_name,
                "delivery_price": float(rate.delivery_price),
                "office_price": float(rate.office_price) if rate.office_price else None,
                "estimated_days": rate.estimated_days
            }
        )

    return {"message": f"Tienda '{store.name}' indexada correctamente con {len(rates)} wilayas"}