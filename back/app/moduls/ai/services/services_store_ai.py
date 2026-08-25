# Importamos repositorio
from moduls.stores.repositories.repositories import select_store_by_id
# Importamos schemas
from moduls.ai.schemas.schemas_store_ai import StoreAIData
# Importamos excepciones
from core.exceptions import NotFoundException

# Método para pedir la tienda segun el identificador
def get_store_by_id_service(db,store_id: str):

    # Comprobamos si exsiste la tienda
    store = select_store_by_id(db,store_id)

    if not store:
        raise NotFoundException("Store not found")

    # Si exsiste la tienda devolvemos los datos de la tienda 
    return StoreAIData.model_validate(store)
    