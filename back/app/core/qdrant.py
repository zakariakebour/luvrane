from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from core.config import QDRANT_ENDPOINT, QDRANT_API_KEY

#Dimension de embeddings de Gemini (text-embedding-004)
EMBEDDING_DIMENSION = 768

#Nombre de la coleccion global con filtro por store_id
COLLECTION_NAME = "luvrane_stores"

#Cliente singleton reutilizado entre invocaciones Lambda
_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=QDRANT_ENDPOINT,
            api_key=QDRANT_API_KEY
        )
    return _qdrant_client

def ensure_collection_exists():
    """
    Crea la coleccion si no existe todavia.º
    Se llama una vez al arrancar o antes de indexar.
    """
    client = get_qdrant_client()
    existing = client.get_collections().collections
    names = [c.name for c in existing]

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
        print(f"[Qdrant] Coleccion '{COLLECTION_NAME}' creada correctamente")
    else:
        print(f"[Qdrant] Coleccion '{COLLECTION_NAME}' ya existe")