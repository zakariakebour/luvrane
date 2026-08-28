from core.gemini import generate_embedding, generate_response
from core.qdrant import search_points
from core.exceptions import NotFoundException
from moduls.stores.repositories.repositories import select_store_by_id

async def chat_with_store_service(db, store_id: str, question: str, history: list) -> str:

    # Comprobamos que la tienda existe
    store = select_store_by_id(db, store_id)
    if not store:
        raise NotFoundException("Store not found")

    # Convertimos la pregunta en vector para buscar en Qdrant
    question_vector = await generate_embedding(question)

    # Buscamos los chunks mas relevantes de esta tienda en Qdrant
    results = await search_points(question_vector, store_id, limit=5)

    # Si no hay contexto en Qdrant la tienda no esta indexada
    if not results:
        return "Cette boutique n'a pas encore été indexée. Veuillez réessayer plus tard."

    # Construimos el contexto con los chunks recuperados
    context = "\n\n".join([r["payload"].get("text", "") for r in results])

    # Construimos el historial para Gemini
    history_text = ""
    for msg in history:
        role = "Usuario" if msg.role == "user" else "Asistente"
        history_text += f"{role}: {msg.content}\n"

    # Construimos el prompt completo
    prompt = f"""
Eres el asistente virtual de la tienda "{store.name}".
Responde SOLO con información de la tienda basándote en el contexto proporcionado.
Detecta el idioma de la pregunta y responde en ese mismo idioma.
Si no tienes información suficiente para responder, dilo claramente.
No inventes información que no esté en el contexto.

CONTEXTO DE LA TIENDA:
{context}

HISTORIAL DE CONVERSACIÓN:
{history_text}

PREGUNTA ACTUAL:
{question}

RESPUESTA:
"""

    # Gemini genera la respuesta
    answer = await generate_response(prompt)

    return answer