#Importamos repositorio de producto
from moduls.products.repositories.product_repository import get_product_by_id,get_products,get_product_by_name,create_product,update_product,delete_product,get_product_by_name_and_store,update_product_status,get_product_status
#Importamos el metodo de selccion de la tienda
from moduls.stores.repositories import select_store_by_id
#Importamos excepciones
from core.exceptions import ConflictException,NotFoundException,ForbiddenException,ValidationException
#Importamos la clase de estado del producto
from moduls.products.modules import ProductStatus

#Metodo para crear producto
def create_product_service(db,product_data: dict,current_user_id: str):
    #Comprobamos si la tienda exsiste
    store = select_store_by_id(db,product_data.store_id)

    #Si no exsiste
    if not store:
        raise NotFoundException("Boutique introuvable")

    #Comrobamos si la tienda esta activa
    if not store.is_active:
        raise ForbiddenException("Boutique désactivée")

    #Comprobamos si el usuario es el dueño de la tienda
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accés interdit")
    
    #Comprobamos si en la tienda exsiste un producto con el mismo nombre
    if get_product_by_name_and_store(db, product_data.name, product_data.store_id):
        raise ConflictException("Un produit avec ce nom existe déjà dans cette boutique")

    #Convertimos el producto a diccionario
    product_dict = product_data.model_dump()

    #Creamos el producto
    return create_product(db,product_dict)

#Metodo para obtener producto por identificador
def get_product_by_id_service(db,product_id: str):
    #Comprobamos si el producto exsiste
    product = get_product_by_id(db,product_id)

    #Si el producto no esta disponible
    if not product:
        raise NotFoundException("Le produit est pas disponible")
    
    #Devolvemos el producto
    return product

#Metodo para buscar el producto con el nombre
def get_product_by_name_service(db,product_name):
    #Realizamos la consulta del producto con el nombre recibido y comprobar si exsiste
    product = get_product_by_name(db,product_name)
    if not product:
        raise NotFoundException("Produit non disponible")
    
    #Devolvemos el producto
    return product

#Metodo para listar productos con paginacion
def get_products_service(db,skip,limit):
    #Devolvemos los productos con paginación
    return get_products(db,skip=skip,limit=limit)

#Metodo para actualizar un producto
def update_product_service(db,product_data,product_id: str,current_user_id: str):
    #Comprobamos si el product exsiste
    product = get_product_by_id(db,product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    
    #Comprobamos si el producto esta activo
    if not product.is_active:
        raise ForbiddenException("Produit non disponible")
    
    #Comprobamos si el usuario es el dueño de la tienda
    store = select_store_by_id(db,product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")
    
    #Si cambia el nombre comprobamos que no exista otro con ese nombre en la misma tienda
    if product_data.name and product_data.name != product.name:
        if get_product_by_name_and_store(db, product_data.name, product.store_id):
            raise ConflictException("Un produit avec ce nom existe déjà dans cette boutique")

    #Convertimos a diccionario ignorando campos None
    product_dict = product_data.model_dump(exclude_none=True)

    return update_product(db, product, product_dict)

#Metodo para desactivar producto
def delete_product_service(db, product_id: str, current_user_id: str):
    #Comprobamos si el producto existe
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    #Comprobamos si ya esta desactivado
    if not product.is_active:
        raise ForbiddenException("Produit déjà désactivé")

    #Comprobamos si el usuario es el dueño de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    return delete_product(db, product)

# Metodo para cambiar estado del producto
def update_product_status_service(db, product_id: str, status: ProductStatus, current_user_id: str):
    # Comprobamos si el producto existe
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    # Comprobamos si el usuario es el dueño de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    return update_product_status(db, product, status)

#Metodo para consultar el estado del producto
def get_product_status_service(db,product_id: str):
    #Comprobamos si el producto exsiste
    product = get_product_by_id(db,product_id)
    if not product:
        raise NotFoundException("Produit introuvable")
    
    #Devolvemos el estado del producto
    return {"status":product.status}

