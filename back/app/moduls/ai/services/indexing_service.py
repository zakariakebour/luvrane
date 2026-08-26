# Importamos el método para sacar la infórmacion de las tiendas segun el identificador
from moduls.stores.repositories.repositories import select_store_by_id
from core.exceptions import NotFoundException
# Importamos el método para generar embbedings
from core.gemini import generate_embedding
# Importamos el metodo upsert_point 
from core.qdrant import upsert_point

# Método para indexar la tienda
def index_store_services(db,store_id):
    # Antes de cargar los datos comprobamos si exsiste la tienda
    store = select_store_by_id(db, store_id)

    # Si no exsiste
    if not store:
        raise NotFoundException("Store not found")

    