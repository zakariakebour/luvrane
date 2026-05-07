from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from moduls.products.schemas import (
    ProductVariantCreate,
    ProductVariantResponse,
    VariantMediaCreate,
    VariantMediaResponse,
    ColorCreate,
    ColorResponse,
    SizeCreate,
    SizeResponse,
    UpdatePosition
)
from moduls.products.services.product_variant import (
    add_product_variant_service,
    get_variants_by_product_service,
    get_variant_by_id_service,
    update_variant_stock_service,
    update_variant_service,
    delete_variant_service,
    add_variant_media_service,
    get_media_by_variant_service,
    delete_variant_media_service,
    update_media_position_service,
    create_color_service,
    get_all_colors_service,
    delete_color_service,
    create_size_service,
    get_all_sizes_service,
    delete_size_service
)
from core.database import get_db
from core.dependencies import get_current_user
from moduls.users.modules import User

# Schema para actualizar stock
class UpdateStock(BaseModel):
    stock: int

router = APIRouter(tags=["ProductVariants"])


#Endpoints de colo

# Crear color — protegido
@router.post("/colors", response_model=ColorResponse, status_code=201)
def create_color(
    color_data: ColorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_color_service(db, color_data.model_dump())

# Obtener todos los colores — publico
@router.get("/colors", response_model=List[ColorResponse])
def get_colors(
    db: Session = Depends(get_db)
):
    return get_all_colors_service(db)

# Eliminar color — protegido
@router.delete("/colors/{color_id}", status_code=204)
def delete_color(
    color_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_color_service(db, color_id)


#Enpoitns de talla

# Crear talla — protegido
@router.post("/sizes", response_model=SizeResponse, status_code=201)
def create_size(
    size_data: SizeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_size_service(db, size_data.model_dump())

# Obtener todas las tallas — publico
@router.get("/sizes", response_model=List[SizeResponse])
def get_sizes(
    db: Session = Depends(get_db)
):
    return get_all_sizes_service(db)

# Eliminar talla — protegido
@router.delete("/sizes/{size_id}", status_code=204)
def delete_size(
    size_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_size_service(db, size_id)


# Endpoints de variante

# Obtener todas las variantes de un producto — publico
# IMPORTANTE: Esta ruta va antes que las de ID para evitar conflictos
@router.get("/{product_id}/all", response_model=List[ProductVariantResponse])
def get_variants(
    product_id: str,
    db: Session = Depends(get_db)
):
    return get_variants_by_product_service(db, product_id)

# Actualizar stock de variante — protegido
@router.patch("/{variant_id}/stock", response_model=ProductVariantResponse)
def update_stock(
    variant_id: str,
    stock_data: UpdateStock,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_variant_stock_service(db, variant_id, stock_data.stock)

# Obtener media de variante — publico
@router.get("/{variant_id}/media", response_model=List[VariantMediaResponse])
def get_media(
    variant_id: str,
    db: Session = Depends(get_db)
):
    return get_media_by_variant_service(db, variant_id)

# Añadir media a variante — protegido
@router.post("/{variant_id}/media", response_model=VariantMediaResponse, status_code=201)
def add_media(
    variant_id: str,
    media_data: VariantMediaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = media_data.model_dump()
    return add_variant_media_service(db, variant_id, data, current_user.id)

# Crear variante de producto — protegido
@router.post("/{product_id}", response_model=ProductVariantResponse, status_code=201)
def add_variant(
    product_id: str,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = variant_data.model_dump()
    return add_product_variant_service(db, data, product_id)

# Obtener variante por id — publico
@router.get("/detail/{variant_id}", response_model=ProductVariantResponse)
def get_variant(
    variant_id: str,
    db: Session = Depends(get_db)
):
    return get_variant_by_id_service(db, variant_id)

# Actualizar datos de variante — protegido
@router.put("/{variant_id}", response_model=ProductVariantResponse)
def update_variant(
    variant_id: str,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = variant_data.model_dump(exclude_none=True)
    return update_variant_service(db, variant_id, data)

# Desactivar variante — protegido
@router.delete("/{variant_id}", status_code=204)
def delete_variant(
    variant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_variant_service(db, variant_id)


#Endpoints de media de variante (específicos)

# Actualizar posicion de media en carrusel — protegido
@router.patch("/media/{media_id}/position", response_model=VariantMediaResponse)
def update_position(
    media_id: str,
    position_data: UpdatePosition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_media_position_service(db, media_id, position_data.position)

# Eliminar media de variante — protegido
@router.delete("/media/{media_id}", status_code=204)
def delete_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_variant_media_service(db, media_id, current_user.id)