import httpx
from core.config import GEMINI_API_KEY

#Modelo de Gemini encargado de generar embeddings
EMBEDDING_MODEL = "gemini-embedding-001"

#Modelo de Gemini encargado de generar respuestas para los usuarios
GENERATION_MODEL = "gemini-3.6-flash"

#Dimension de los embeddings que utilizaremos en Qdrant
EMBEDDING_DIMENSION = 768

#URL base de la API REST de Gemini
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"


#Headers reutilizados en todas las peticiones a Gemini
def get_headers() -> dict:
    return {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

# Método para generar embbedings
async def generate_embedding(text: str) -> list:
    """
    Genera el embedding de un texto utilizando Gemini.
    Async porque FastAPI es asincrono y asi no bloqueamos
    el servidor mientras esperamos la respuesta de Gemini.
    """
    #Abrimos un cliente HTTP asincrono que se cierra automaticamente al terminar
    async with httpx.AsyncClient() as client:

        #Mandamos el texto a Gemini y esperamos sin bloquear
        response = await client.post(
            f"{GEMINI_ENDPOINT}/models/{EMBEDDING_MODEL}:embedContent",
            headers=get_headers(),
            json={
                "model": f"models/{EMBEDDING_MODEL}",
                "content": {
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                },
                "outputDimensionality": EMBEDDING_DIMENSION
            }
        )

        response.raise_for_status()

        result = response.json()

        #Devolvemos la lista de numeros que representa el texto
        return result["embedding"]["values"]

# Método para generar respuesta al usuario
async def generate_response(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{GEMINI_ENDPOINT}/models/{GENERATION_MODEL}:generateContent",
            headers=get_headers(),
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )

        # Si Gemini falla devolvemos mensaje amigable en vez de crash
        if response.status_code == 503:
            return "Le service est temporairement indisponible. Veuillez réessayer dans quelques instants."
        
        if response.status_code == 429:
            return "Trop de requêtes. Veuillez réessayer dans quelques instants."

        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]