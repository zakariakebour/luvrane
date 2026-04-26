from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
#Importamos schemas
from moduls.products.schemas import (
    ProductImageCreate,
    ProductImageResponse,
    PresignedUrlRequest,
    PresignedUrlResponse,
    UpdatePosition
)
#Importamos servicios
from moduls.products.services.product_images import (
    add_product_image_service,
    update_position_service,
    delete_product_image_service
)
#Importamos S3
from core.s3 import generate_presigned_url, delete_file
#Importamos base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User

router = APIRouter(tags=["ProductImages"])

#Endpoint para generar URL firmada para subir archivo directo a S3 — protegido
@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(
    data: PresignedUrlRequest,
    current_user: User = Depends(get_current_user)
):
    #Generamos la URL firmada
    return generate_presigned_url(data.folder, data.content_type)

#Endpoint para registrar imagen o video en la DB despues de subirlo a S3 — protegido
@router.post("/{product_id}", response_model=ProductImageResponse, status_code=201)
def add_image(
    product_id: str,
    image_data: ProductImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_product_image_service(db, product_id, image_data, current_user.id)

#Endpoint para reordenar imagen en el carrusel — protegido
@router.patch("/{image_id}/position", response_model=ProductImageResponse)
def update_position(
    image_id: str,
    position_data: UpdatePosition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_position_service(db, image_id, position_data.position, current_user.id)

#Endpoint para eliminar imagen o video del producto — protegido
@router.delete("/{image_id}", status_code=204)
def delete_image(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #Buscamos la imagen para obtener su URL antes de eliminarla
    from moduls.products.repositories.product_images import get_image_by_id
    image = get_image_by_id(db, image_id)
    if image:
        #Eliminamos de S3
        delete_file(image.image_url)
    #Eliminamos de la DB
    delete_product_image_service(db, image_id, current_user.id)