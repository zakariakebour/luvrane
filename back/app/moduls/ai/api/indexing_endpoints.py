# Importamos Fastapi
from fastapi import APIRouter,Depends
# Importamos el método en el service
from moduls.ai.services.indexing_service import index_store_service
from sqlalchemy.orm import Session
# Importamos método de la baase de datos
from core.database import get_db

router = APIRouter(tags=["indexing"])

# Creamos el endpoint para el indexing
@router.post("/stores/{store_id}/index",status_code=200)
async def get_index(
        store_id: str,
        db: Session = Depends(get_db)
    ):
    return await index_store_service(db,store_id)
