from pydantic import BaseModel
from typing import List, Optional

# Mensaje individual del historial
class ChatMessage(BaseModel):
    role: str  # "user" o "model"
    content: str

# Peticion del usuario al chat
class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = []

# Respuesta del modelo al usuario
class ChatResponse(BaseModel):
    answer: str