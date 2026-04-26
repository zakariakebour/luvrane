from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from moduls.stores.schemas import CreateStore, StoreResponse, StoresPageResponse, UpdateStore
from moduls.stores.services import (
    create_store_service,
    get_store_by_id_service,
    get_store_by_name_service,
    get_stores_service,
    update_store_service,
    delete_store_service
)
from core.database import get_db
from core.dependencies import get_current_user              
from moduls.users.modules import User

router = APIRouter(tags=["Stores"])

#Endpoint para creacion de tienda — solo owners
@router.post("/create", response_model=StoreResponse, status_code=201)
def create_store(
    store: CreateStore,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)     
):
    return create_store_service(db, store, current_user.id)  

#Endpoint que muestra todas las tiendas disponibles — publico
@router.get("/", response_model=StoresPageResponse)
def get_stores(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return get_stores_service(db, skip=skip, limit=limit)

#Endpoint para buscar tienda segun nombre<
@router.get("/search", response_model=StoreResponse)
def get_store_by_name(name: str, db: Session = Depends(get_db)):
    return get_store_by_name_service(db, name)

#Endpoint para recibir datos de la tienda segun el identificador — publico
@router.get("/{store_id}", response_model=StoreResponse)
def get_store_by_id(store_id: str, db: Session = Depends(get_db)):
    return get_store_by_id_service(db, store_id)

#Endpoint para actualizar tienda — solo el owner
@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    store_data: UpdateStore,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)            
):
    return update_store_service(db, store_id, store_data, current_user.id)

#Endpoint para eliminar/desactivar tienda — solo el owner
@router.delete("/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)            
):
    return delete_store_service(db, store_id, current_user.id)