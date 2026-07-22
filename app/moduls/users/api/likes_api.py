from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
#Importamos schemas
from moduls.users.schemas import ProductLikeResponse
from typing import List
#Importamos base de datos
from core.database import get_db
#Importamos servicios
from moduls.users.services.likes_service import (
    add_like_service,
    get_user_likes_service,
    remove_like_service
)
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User

router = APIRouter(tags=["ProductLikes"]) 

#Endpoint para añadir producto a la lista de me gusta — protegido
@router.post("/{product_id}", response_model=ProductLikeResponse, status_code=201)
def add_like(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_like_service(db, current_user.id, product_id)

#Endpoint para obtener lista de me gusta del usuario — protegido
@router.get("/", response_model=List[ProductLikeResponse])
def get_likes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_likes_service(db, current_user.id)

#Endpoint para eliminar producto de la lista de me gusta — protegido
@router.delete("/{product_id}", status_code=204)
def remove_like(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remove_like_service(db, current_user.id, product_id)