from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
#Importamos schemas
from moduls.products.schemas import ProductCreate, ProductResponse, ProductUpdate, ProductsPageResponse
#Importamos servicios
from moduls.products.services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    get_product_by_name_service,
    update_product_service,
    delete_product_service,
    get_product_status_service,
    update_product_status_service
)
#Importamos base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User
#Importamos ProductStatus
from moduls.products.modules import ProductStatus
#Importamos schema de paginacion
from pydantic import BaseModel

router = APIRouter(tags=["Products"])

#Endpoint para crear producto — protegido solo owners
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_product_service(db, product_data, current_user.id)

#Endpoint para listar productos con paginacion — publico
@router.get("/", response_model=ProductsPageResponse)
def get_products(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return get_products_service(db, skip=skip, limit=limit)

#Endpoint para buscar producto por nombre — publico
@router.get("/search", response_model=ProductResponse)
def get_product_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    return get_product_by_name_service(db, name)

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_product_service(db, product_data, product_id, current_user.id)

#Endpoint para desactivar producto — protegido solo owners
@router.delete("/{product_id}", response_model=ProductResponse)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_product_service(db, product_id, current_user.id)

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