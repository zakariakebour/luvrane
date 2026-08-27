import httpx
from core.config import QDRANT_ENDPOINT, QDRANT_API_KEY

#Dimension de embeddings de Gemini (text-embedding-004)
EMBEDDING_DIMENSION = 768

#Nombre de la coleccion global con filtro por store_id
COLLECTION_NAME = "luvrane_stores"

#Headers reutilizados en todas las peticiones a Qdrant
def get_headers() -> dict:
    return {
        "api-key": QDRANT_API_KEY,
        "Content-Type": "application/json"
    }

async def ensure_collection_exists():
    """
    Crea la coleccion si no existe todavia.
    Se llama una vez al arrancar o antes de indexar.
    Async para no bloquear el servidor mientras Qdrant responde.
    """
    #Abrimos cliente HTTP asincrono que se cierra automaticamente
    async with httpx.AsyncClient() as client:

        #Consultamos las colecciones existentes sin bloquear
        response = await client.get(
            f"{QDRANT_ENDPOINT}/collections",
            headers=get_headers()
        )

        response.raise_for_status()
        collections = response.json().get("result", {}).get("collections", [])
        names = [c["name"] for c in collections]

        if COLLECTION_NAME not in names:

            #Creamos la coleccion con configuracion de embeddings
            create_response = await client.put(
                f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}",
                headers=get_headers(),
                json={
                    "vectors": {
                        "size": EMBEDDING_DIMENSION,
                        "distance": "Cosine"
                    }
                }
            )
            create_response.raise_for_status()
            print(f"[Qdrant] Coleccion '{COLLECTION_NAME}' creada correctamente")
        else:
            print(f"[Qdrant] Coleccion '{COLLECTION_NAME}' ya existe")


async def upsert_point(point_id: str, vector: list, payload: dict):
    """
    Inserta o actualiza un punto en la coleccion.
    Async para no bloquear el servidor mientras Qdrant responde.
    Un punto es un vector + sus metadatos (store_id, nombre, etc).
    """
    #Abrimos cliente HTTP asincrono que se cierra automaticamente
    async with httpx.AsyncClient() as client:

        #Insertamos o actualizamos el punto sin bloquear
        response = await client.put(
            f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}/points",
            headers=get_headers(),
            json={
                "points": [
                    {
                        "id": point_id,
                        "vector": vector,
                        "payload": payload
                    }
                ]
            }
        )
        print("[Qdrant] upsert response:", response.status_code, response.text)
        response.raise_for_status()
        return response.json()


async def search_points(vector: list, store_id: str, limit: int = 5) -> list:
    """
    Busca los puntos mas similares al vector dado filtrando por store_id.
    Async para no bloquear el servidor mientras Qdrant responde.
    Devuelve los chunks mas relevantes para construir el contexto del RAG.
    """
    #Abrimos cliente HTTP asincrono que se cierra automaticamente
    async with httpx.AsyncClient() as client:

        #Buscamos los puntos mas similares sin bloquear
        response = await client.post(
            f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}/points/search",
            headers=get_headers(),
            json={
                "vector": vector,
                "limit": limit,
                "filter": {
                    "must": [
                        {
                            "key": "store_id",
                            "match": {
                                "value": store_id
                            }
                        }
                    ]
                },
                "with_payload": True
            }
        )
        response.raise_for_status()
        return response.json().get("result", [])

async def delete_point(point_id: str):
    """
    Elimina un punto de la coleccion de Qdrant.
    Se utiliza cuando se elimina una Wilaya de una tienda.
    """
    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}/points/delete",
            headers=get_headers(),
            json={
                "points": [point_id]
            }
        )

        print("[Qdrant] delete response:", response.status_code, response.text)
        response.raise_for_status()

        return response.json()

async def delete_store_wilaya_points(store_id: str):
    """
    Elimina todos los puntos correspondientes a las Wilayas de una tienda.
    Mantiene el punto general de la tienda.
    """
    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}/points/delete",
            headers=get_headers(),
            json={
                "filter": {
                    "must": [
                        {
                            "key": "store_id",
                            "match": {
                                "value": store_id
                            }
                        },
                        {
                            "key": "wilaya_id",
                            "match": {
                                "is_empty": True
                            }
                        }
                    ]
                }
            }
        )

        print(
            "[Qdrant] delete wilaya points response:",
            response.status_code,
            response.text
        )

        response.raise_for_status()

        return response.json()

async def delete_store_points(store_id: str):
    """
    Elimina todos los puntos de una tienda de Qdrant.
    """
    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{QDRANT_ENDPOINT}/collections/{COLLECTION_NAME}/points/delete",
            headers=get_headers(),
            json={
                "filter": {
                    "must": [
                        {
                            "key": "store_id",
                            "match": {
                                "value": store_id
                            }
                        }
                    ]
                }
            }
        )

        print("[Qdrant] delete store points response:", response.status_code, response.text)
        response.raise_for_status()

        return response.json()