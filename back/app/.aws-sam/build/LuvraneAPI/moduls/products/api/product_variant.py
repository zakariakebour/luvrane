from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
#Importamos schemas
from moduls.products.schemas import ProductVariantCreate, ProductVariantResponse
#Importamos servicios
from moduls.products.services.product_variant import (
    add_product_variant_service,
    get_variants_by_product_service,
    update_variant_stock_service
)
#Importamos base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User
#Importamos schema para actualizar stock
from pydantic import BaseModel

#Schema para actualizar stock
class UpdateStock(BaseModel):
    stock: int

router = APIRouter(tags=["ProductVariants"])

#Endpoint para añadir variante al producto — protegido solo owners
@router.post("/{product_id}", response_model=ProductVariantResponse, status_code=201)
def add_variant(
    product_id: str,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_product_variant_service(
        db,
        variant_data.model_dump(exclude={"option_value_ids"}),
        variant_data.option_value_ids,
        variant_data.model_dump(exclude={"stock", "price", "sku", "option_value_ids"}),
        product_id
    )

#Endpoint para obtener todas las variantes de un producto — publico
@router.get("/{product_id}", response_model=List[ProductVariantResponse])
def get_variants(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_variants_by_product_service(db, product_id)

#Endpoint para actualizar stock de una variante — protegido solo owners
@router.patch("/{variant_id}/stock", response_model=ProductVariantResponse)
def update_stock(
    variant_id: str,
    stock_data: UpdateStock,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_variant_stock_service(db, variant_id, stock_data.stock)