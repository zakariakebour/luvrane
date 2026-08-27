# Importamos services
from moduls.ai.services.services_store_ai import get_store_by_id_service
# Importamos Session
from sqlalchemy.orm import Session
# Importamos método de base de datos
from core.database import get_db
# Importamos schemas
from moduls.ai.schemas.schemas_store_ai import StoreAIData
from fastapi import APIRouter,Depends

router = APIRouter(tags=["ai"])

# Endpoint para recibir datos de la tienda 
@router.get("/stores/{store_id}", response_model=StoreAIData, status_code=200)
def get_store_endpoint(
        store_id: str,
        db: Session = Depends(get_db)
    ):
    return get_store_by_id_service(db,store_id)