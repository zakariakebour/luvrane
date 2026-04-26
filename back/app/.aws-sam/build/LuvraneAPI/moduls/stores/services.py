from moduls.stores.repositories import (
    create_store,
    select_store_by_id,
    select_stores,
    get_store_by_name,
    delete_store,
    update_store
)

# Metodo para crear tienda
def create_store_service(db, store_data):

    # Validación de nombre aunque Pydantic ya lo hace, reforzamos
    name = store_data.name.strip()

    if len(name) < 2:
        raise ValueError("Le nom du boutique doit contenir au moins 2 caractères")

    if len(name) > 255:
        raise ValueError("Le nom du boutique ne peut pas dépasser 255 caractères")

    #Validar que el nombre no exista
    existing_store = get_store_by_name(db, name)

    if existing_store:
        raise ValueError("Ce nom de magasin est déjà utilisé")

    # Crear la tienda
    store_dict = store_data.dict()
    store_dict["name"] = name  # guardamos limpio

    return create_store(db, store_dict)


# Obtener todas las tiendas, pasamos los parametros necesarios para la paginacion
def get_stores_service(db,skip: int=0,limit: int=20):
    return select_stores(db, skip=skip, limit=limit)

# Obtener tienda por identificador
def get_store_by_id_service(db, store_id: str):
    store = select_store_by_id(db, store_id)

    #Si no se encuentra la tienda seleccionada
    if not store:
        raise ValueError("Boutique introuvable")

    return store

#Metodo para obtener la tienda segun el nombre
def get_store_by_name_service(db,store_name: str):

    #Comprobamos si exsiste la tienda con ese nombre
    name = store_name.strip()
    existing_store = get_store_by_name(db, name)

    if not existing_store:
        raise ValueError("Boutique introuvable")

    #Si exsiste retornamos la tienda
    return existing_store

#Metodo para eliminar tienda del sistema
def delete_store_service(db,store_id: str):
    #Seleccionamos la tienda
    store = select_store_by_id(db,store_id)

    #Si no exsiste
    if not store:
        raise ValueError("Boutique introuvable")
    
    #Si ya esta desactivada lanzamos error
    if not store.is_active:
        raise ValueError("La boutique est déjà désactivée")
    
    return delete_store(db,store)
    
# Metodo para actualizar tienda
def update_store_service(db, store_id: str, store_data):
    # Comprobamos si la tienda seleccionada existe
    store = select_store_by_id(db, store_id)

    # Si no existe
    if not store:
        raise ValueError("Boutique introuvable")   
    
    # Convertimos el schema a diccionario ignorando los campos None
    store_dict = store_data.model_dump(exclude_none=True)  

    # Si existe y todo correcto devolvemos la actualizacion
    return update_store(db, store, store_dict)             
