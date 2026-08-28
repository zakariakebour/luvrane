from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from moduls.ai.schemas.chat_schemas import ChatRequest, ChatResponse
from moduls.ai.services.chat_service import chat_with_store_service

router = APIRouter(tags=["AI Chat"])

# Endpoint para chatear con el asistente de una tienda
@router.post("/stores/{store_id}/chat", response_model=ChatResponse)
async def chat_with_store(
    store_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    answer = await chat_with_store_service(
        db,
        store_id,
        request.question,
        request.history
    )

    return ChatResponse(answer=answer)