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
import asyncio

# Metodo auxiliar para generar embedding con reintento automatico si Gemini da 429
async def generate_embedding_with_retry(text: str, max_retries: int = 3) -> list:
    for attempt in range(max_retries):
        try:
            return await generate_embedding(text)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                # Esperamos exponencialmente: 2s, 4s, 8s
                wait = 2 ** (attempt + 1)
                print(f"[Gemini] Rate limit, reintentando en {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise e

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

    # Generamos el embedding del texto con reintento automatico
    vector = await generate_embedding_with_retry(text)

    # Guardamos el vector en Qdrant con los metadatos de la tienda
    await upsert_point(
        point_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, store.id)),
        vector=vector,
        payload={
            "store_id": store.id,
            "name": store.name,
            "type": store.type,
            "text": text,
            "category": store.category.value if store.category else None,
            "logistics_partner": store.logistics_partner or None
        }
    )

    # Cargamos todas las tarifas de la tienda
    rates = get_all_store_rates(db, store_id)

    # Creamos un chunk separado por cada wilaya
    for i, rate in enumerate(rates):

        # Construimos texto con los datos de la wilaya
        wilaya_text = f"""
            Store: {store.name}
            Wilaya: {rate.wilaya_name} ({rate.wilaya_id})
            Precio domicilio: {rate.delivery_price} DA
            Precio bureau: {rate.office_price or 'No disponible'} DA
            Días estimados: {rate.estimated_days or 'No especificado'}
        """

        # Generamos embedding con reintento automatico
        wilaya_vector = await generate_embedding_with_retry(wilaya_text)

        # Guardamos en Qdrant con un id unico por wilaya usando uuid5
        await upsert_point(
            point_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{store.id}_{rate.wilaya_id}")),
            vector=wilaya_vector,
            payload={
                "store_id": store.id,
                "name": store.name,
                "text": wilaya_text,
                "wilaya_id": rate.wilaya_id,
                "wilaya_name": rate.wilaya_name,
                "delivery_price": float(rate.delivery_price),
                "office_price": float(rate.office_price) if rate.office_price else None,
                "estimated_days": rate.estimated_days
            }
        )

        # Delay entre wilayas para no agotar el rate limit de Gemini
        # Cada 10 wilayas esperamos 1 segundo
        if (i + 1) % 10 == 0:
            await asyncio.sleep(1)

    return {"message": f"Tienda '{store.name}' indexada correctamente con {len(rates)} wilayas"}