# Importamos el método para sacar la infórmacion de las tiendas segun el identificador
from moduls.stores.repositories.repositories import select_store_by_id
from core.exceptions import NotFoundException
# Importamos el método para generar embbedings
from core.gemini import generate_embedding
# Importamos el metodo upsert_point 
from core.qdrant import upsert_point
# Importamos el metodo para obtener todas las tarifas de una tienda
from moduls.stores.repositories.shipping_repository import get_all_store_rates
# Importamos el metodo para seleccionar los productos pertenecientes a la tienda
from moduls.products.repositories.product_repository import get_products_by_store
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


# Indexa solo el chunk principal de la tienda (1 embedding)
# Se llama cuando el dueño actualiza nombre, descripción, tipo, categoría o logística
async def index_store_info(db, store_id: str):

    store = select_store_by_id(db, store_id)

    if not store:
        raise NotFoundException("Store not found")

    # Texto compacto sin indentacion ni saltos innecesarios para reducir tokens
    text = (
        f"Store:{store.name}. "
        f"Description:{store.description or 'N/A'}. "
        f"Type:{store.type}. "
        f"Category:{store.category.value if store.category else 'N/A'}. "
        f"Logistics:{store.logistics_partner or 'N/A'}."
    )

    vector = await generate_embedding_with_retry(text)

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


# Indexa solo una wilaya concreta (1 embedding)
# Se llama cuando el dueño añade o modifica una tarifa de envío
async def index_store_wilaya(db, store_id: str, wilaya_id: int):

    store = select_store_by_id(db, store_id)

    if not store:
        raise NotFoundException("Store not found")

    rates = get_all_store_rates(db, store_id)
    rate = next((r for r in rates if r.wilaya_id == wilaya_id), None)

    if not rate:
        return

    # Texto compacto sin indentacion ni saltos innecesarios para reducir tokens
    wilaya_text = (
        f"Store:{store.name}. "
        f"Wilaya:{rate.wilaya_name}({rate.wilaya_id}). "
        f"Domicile:{rate.delivery_price}DA. "
        f"Bureau:{rate.office_price or 'N/A'}DA. "
        f"Days:{rate.estimated_days or 'N/A'}."
    )

    wilaya_vector = await generate_embedding_with_retry(wilaya_text)

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


# Indexa solo un producto concreto (1 embedding)
# Se llama cuando el dueño crea o actualiza un producto
async def index_store_product(db, store_id: str, product_id: str, product):

    store = select_store_by_id(db, store_id)

    if not store:
        raise NotFoundException("Store not found")

    # Texto compacto sin indentacion ni saltos innecesarios para reducir tokens
    product_text = (
        f"Store:{store.name}. "
        f"Product:{product.name}. "
        f"Description:{product.description or 'N/A'}. "
        f"Price:{product.price}DA. "
        f"Gender:{product.gender_category.value if product.gender_category else 'N/A'}. "
        f"Category:{product.product_category or 'N/A'}. "
        f"Available:{'Yes' if product.is_active else 'No'}."
    )

    product_vector = await generate_embedding_with_retry(product_text)

    await upsert_point(
        point_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{store_id}_product_{product_id}")),
        vector=product_vector,
        payload={
            "store_id": store_id,
            "name": store.name,
            "text": product_text,
            "product_id": product_id,
            "product_name": product.name,
            "price": float(product.price)
        }
    )


# Indexa todo de una tienda — solo se usa la primera vez o para forzar re-indexacion completa
async def index_store_service(db, store_id: str):

    store = select_store_by_id(db, store_id)

    if not store:
        raise NotFoundException("Store not found")

    # Indexamos el chunk principal de la tienda
    await index_store_info(db, store_id)

    # Cargamos todas las tarifas de la tienda
    rates = get_all_store_rates(db, store_id)

    # Creamos un chunk separado por cada wilaya
    for i, rate in enumerate(rates):

        await index_store_wilaya(db, store_id, rate.wilaya_id)

        # Delay entre wilayas para no agotar el rate limit de Gemini
        if (i + 1) % 10 == 0:
            await asyncio.sleep(1)

    # Cargamos los productos activos de la tienda
    products_data = get_products_by_store(db, store_id)
    products = products_data.get("products", [])

    # Creamos un chunk separado por cada producto
    for j, product in enumerate(products):

        await index_store_product(db, store_id, product.id, product)

        # Delay entre productos para no agotar el rate limit de Gemini
        if (j + 1) % 10 == 0:
            await asyncio.sleep(1)

    return {
        "message": f"Tienda '{store.name}' indexada correctamente con {len(rates)} wilayas y {len(products)} productos"
    }