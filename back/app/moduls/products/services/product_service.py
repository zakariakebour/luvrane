#Importamos repositorio de producto
from moduls.products.repositories.product_repository import (
    get_product_by_id,
    get_products,
    get_product_by_name,
    create_product,
    update_product,
    delete_product,
    get_product_by_name_and_store,
    update_product_status,
    get_product_status,
    get_products_by_store,
)
#Importamos el metodo de seleccion de la tienda
from moduls.stores.repositories import select_store_by_id
#Importamos excepciones
from core.exceptions import ConflictException, NotFoundException, ForbiddenException, ValidationException
#Importamos la clase de estado del producto
from moduls.products.modules import ProductStatus, GenderCategory
#Metodo de repositorio de variantes para añadri por defecto e insertar una variante vacia para producto sin variante y tener el stock
from moduls.products.repositories.product_variant import add_product_variant
from moduls.products.schemas import ProductResponse
#Importamos el metodo de update para variante
from moduls.products.repositories.product_variant import update_variant
from core.s3 import delete_file

#Metodo para crear producto
def create_product_service(db, product_data, current_user_id: str):
    #Comprobamos si la tienda existe
    store = select_store_by_id(db, product_data.store_id)
    if not store:
        raise NotFoundException("Boutique introuvable")

    #Comprobamos si la tienda esta activa
    if not store.is_active:
        raise ForbiddenException("Boutique désactivée")

    #Comprobamos si el usuario es el dueño de la tienda
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    #Comprobamos si en la tienda existe un producto con el mismo nombre
    if get_product_by_name_and_store(db, product_data.name, product_data.store_id):
        raise ConflictException("Un produit avec ce nom existe déjà dans cette boutique")

    #Convertimos el producto a diccionario excluyendo relaciones que se crean por separado
    product_dict = product_data.model_dump(exclude={"images", "variants","stock"})
  
  
    product = create_product(db, product_dict)
    if not product_data.variants:
        add_product_variant(db, product.id, {
            "sku": f"DEFAULT-{product.id[:8]}",
            "stock": getattr(product_data, 'stock', 0),
            "price": product_data.price,
            "color_id": None,
            "size_id": None,
            "is_active": True
        })
    # Si hay variantes las guardamos una en una
    else:
        for variant in product_data.variants:
            # Aquí llamamos a tu repositorio de variantes para cada una
            variant_dict = variant.model_dump()
            add_product_variant(db, product.id, variant_dict)

    return product

#Metodo para obtener producto por identificador
def get_product_by_id_service(db, product_id: str):
    #Comprobamos si el producto existe
    product = get_product_by_id(db, product_id)

    #Si el producto no esta disponible
    if not product:
        raise NotFoundException("Le produit n'est pas disponible")

    #Devolvemos el producto
    return product


#Metodo para buscar el producto con el nombre
def get_product_by_name_service(db, product_name: str):
    products = get_product_by_name(db, product_name.strip())
    if not products:
        raise NotFoundException("Produit non disponible")
    return products


def get_products_service(db, skip, limit, gender_category=None):
    data = get_products(db, skip=skip, limit=limit, gender_category=gender_category)

    products_with_store = []

    for product in data["products"]:
        product_dict = ProductResponse.model_validate(product).model_dump()

        product_dict["store_name"] = product.store.name if product.store else None

        products_with_store.append(product_dict)

    return {
        "total": data["total"],
        "products": products_with_store
    }


def update_product_service(db, product_data, product_id: str, current_user_id: str):
    # 1. Comprobaciones de existencia y permisos (ya las tienes)
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    # 2. Gestionar el Stock si viene en el product_data
    # Solo si el producto es "simple" (tiene una sola variante y es la DEFAULT)
    if hasattr(product_data, 'stock') and product_data.stock is not None:
        # Buscamos si existe la variante por defecto
        default_variant = next((v for v in product.variants if "DEFAULT" in v.sku), None)
        
        if default_variant:
            # Actualizamos el stock en la tabla de variantes
            update_variant(db, default_variant.id, {"stock": product_data.stock})

    # 3. Actualizar los datos básicos del producto (nombre, descripción, precio base)
    product_dict = product_data.model_dump(exclude_none=True, exclude={"variants", "stock"})
    
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
    
    #Eliminar imágenes de la galería del producto
    if product.images:
        for image in product.images:
            try:
                delete_file(image.image_url)
            except Exception:
                pass # Evitamos bloquear si un archivo ya no existe

    # 2. Eliminar imágenes de las variantes
    if product.variants:
        for variant in product.variants:
            if hasattr(variant, 'image_url') and variant.image_url:
                try:
                    delete_file(variant.image_url)
                except Exception:
                    pass
    # --- FIN LÓGICA S3 ---

    return delete_product(db, product)

    return delete_product(db, product)


#Metodo para cambiar estado del producto
def update_product_status_service(db, product_id: str, status: ProductStatus, current_user_id: str):
    #Comprobamos si el producto existe
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    #Comprobamos si el usuario es el dueño de la tienda
    store = select_store_by_id(db, product.store_id)
    if store.owner_id != current_user_id:
        raise ForbiddenException("Accès interdit")

    return update_product_status(db, product, status)


#Metodo para consultar el estado del producto
def get_product_status_service(db, product_id: str):
    #Comprobamos si el producto existe
    product = get_product_by_id(db, product_id)
    if not product:
        raise NotFoundException("Produit introuvable")

    #Devolvemos el estado del producto
    return {"status": product.status}


#Metodo para listar productos de una tienda concreta
def get_products_by_store_service(db, store_id: str, skip: int = 0, limit: int = 20, gender_category=None):
    store = select_store_by_id(db, store_id)
    if not store:
        raise NotFoundException("Boutique introuvable")
        
#Devolvemos productos activos de la tienda con paginacion y filtro
    return get_products_by_store(db, store_id, skip=skip, limit=limit, gender_category=gender_category)

