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










