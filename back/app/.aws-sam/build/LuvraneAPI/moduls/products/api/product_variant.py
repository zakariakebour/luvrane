from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from moduls.products.schemas import ProductVariantCreate, ProductVariantResponse,ProductOptionCreate,ProductOptionResponse,ProductOptionValueResponse,ProductOptionValueCreate,UpdateStock
from moduls.products.services.product_variant import (
    add_product_variant_service,
    get_variants_by_product_service,
    update_variant_stock_service,    
    create_product_option_service,
    get_options_by_product_service,
    delete_option_service,
    create_option_value_service,
    get_values_by_option_service,
    delete_option_value_service,
)
from core.database import get_db
from core.dependencies import get_current_user
from moduls.users.modules import User

router = APIRouter(tags=["ProductVariants"])

@router.post("/{product_id}", response_model=ProductVariantResponse, status_code=201)
def add_variant(
    product_id: str,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = variant_data.model_dump(exclude={"option_value_ids", "attributes"})
    return add_product_variant_service(
        db,
        data,
        variant_data.option_value_ids,
        variant_data.attributes,
        product_id
    )

@router.get("/{product_id}", response_model=List[ProductVariantResponse])
def get_variants(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_variants_by_product_service(db, product_id)

@router.patch("/{variant_id}/stock", response_model=ProductVariantResponse)
def update_stock(
    variant_id: str,
    stock_data: UpdateStock,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_variant_stock_service(db, variant_id, stock_data.stock)


#Servicios para opciones de productos
@router.post("/{product_id}/options", response_model=ProductOptionResponse, status_code=201)
def create_option(
    product_id: str,
    option_data: ProductOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_product_option_service(db, product_id, option_data.name)

@router.get("/{product_id}/options", response_model=List[ProductOptionResponse])
def get_options(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_options_by_product_service(db, product_id)

@router.delete("/options/{option_id}", status_code=204)
def delete_option(
    option_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_option_service(db, option_id)

#Endpoints de opciones
@router.post("/options/{option_id}/values", response_model=ProductOptionValueResponse, status_code=201)
def create_option_value(
    option_id: str,
    value_data: ProductOptionValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_option_value_service(db, option_id, value_data.value)

@router.get("/options/{option_id}/values", response_model=List[ProductOptionValueResponse])
def get_option_values(
    option_id: str,
    db: Session = Depends(get_db)
):
    return get_values_by_option_service(db, option_id)

@router.delete("/options/values/{value_id}", status_code=204)
def delete_option_value(
    value_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_option_value_service(db, value_id)
