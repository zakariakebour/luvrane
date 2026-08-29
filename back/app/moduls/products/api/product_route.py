from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

#Importamos schemas
from moduls.products.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductsPageResponse
)
#Importamos servicios
from moduls.products.services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    get_product_by_name_service,
    update_product_service,
    delete_product_service,
    get_product_status_service,
    update_product_status_service,
    get_products_by_store_service,
)
#Importamos base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User
#Importamos ProductStatus, GenderCategory y ProductCategory
from moduls.products.modules import ProductStatus, GenderCategory, ProductCategory
#Importamos metodos de indexacion de productos
from moduls.ai.services.indexing_service import index_store_product
from core.qdrant import delete_point
import uuid

router = APIRouter(tags=["Products"])


#Endpoint para crear producto — protegido solo owners
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = create_product_service(db, product_data, current_user.id)

    # Indexamos el producto nuevo en background
    background_tasks.add_task(
        index_store_product,
        db,
        result.store_id,
        result.id,
        result
    )

    return result

#Endpoint para listar todos los productos con paginacion — publico
@router.get("/", response_model=ProductsPageResponse)
def get_products(
    skip: int = 0,
    limit: int = 20,
    #Filtro opcional por categoria de genero
    gender_category: Optional[GenderCategory] = Query(None),
    #Filtro opcional por categoria de producto
    product_category: Optional[ProductCategory] = Query(None),
    db: Session = Depends(get_db)
):
    return get_products_service(db, skip=skip, limit=limit, gender_category=gender_category, product_category=product_category)

#Endpoint para buscar producto por nombre — publico
@router.get("/search", response_model=List[ProductResponse])
def get_product_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    return get_product_by_name_service(db, name)

#Endpoint para listar productos de una tienda concreta — publico
@router.get("/store/{store_id}", response_model=ProductsPageResponse)
def get_products_by_store(
    store_id: str,
    skip: int = 0,
    limit: int = 20,
    #Filtro opcional por categoria de genero
    gender_category: Optional[GenderCategory] = Query(None),
    #Filtro opcional por categoria de producto
    product_category: Optional[ProductCategory] = Query(None),
    db: Session = Depends(get_db)
):
    return get_products_by_store_service(db, store_id, skip=skip, limit=limit, gender_category=gender_category, product_category=product_category)

#Endpoint para consultar estado del producto — protegido
@router.get("/{product_id}/status")
def get_product_status(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_product_status_service(db, product_id)


#Endpoint para actualizar estado del producto — protegido solo owners
@router.patch("/{product_id}/status")
def update_product_status(
    product_id: str,
    status: ProductStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_product_status_service(db, product_id, status, current_user.id)


#Endpoint para obtener producto por ID — publico
@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_product_by_id_service(db, product_id)


#Endpoint para actualizar producto — protegido solo owners
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_data: ProductUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = update_product_service(db, product_data, product_id, current_user.id)

    # Re-indexamos el producto actualizado en background
    background_tasks.add_task(
        index_store_product,
        db,
        result.store_id,
        result.id,
        result
    )

    return result


#Endpoint para desactivar producto — protegido solo owners
@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(
    product_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = delete_product_service(db, product_id, current_user.id)

    # Eliminamos el punto del producto en Qdrant en background
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{result.store_id}_product_{product_id}"))
    background_tasks.add_task(delete_point, point_id)

    return result