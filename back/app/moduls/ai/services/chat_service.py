from core.gemini import generate_embedding, generate_response
from core.qdrant import search_points
from core.exceptions import NotFoundException
from moduls.stores.repositories.repositories import select_store_by_id
from moduls.stores.repositories.shipping_repository import get_all_store_rates
from moduls.products.repositories.product_repository import get_products_by_store
from moduls.products.repositories.product_images import get_primary_image_by_product_id

WILAYAS = [
    "Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Béjaïa", "Biskra",
    "Béchar", "Blida", "Bouira", "Tamanrasset", "Tébessa", "Tlemcen", "Tiaret",
    "Tizi Ouzou", "Alger", "Djelfa", "Jijel", "Sétif", "Saïda", "Skikda",
    "Sidi Bel Abbès", "Annaba", "Guelma", "Constantine", "Médéa", "Mostaganem",
    "M'Sila", "Mascara", "Ouargla", "Oran", "El Bayadh", "Illizi", "Bordj Bou Arréridj",
    "Boumerdès", "El Tarf", "Tindouf", "Tissemsilt", "El Oued", "Khenchela",
    "Souk Ahras", "Tipaza", "Mila", "Aïn Defla", "Naâma", "Aïn Témouchent",
    "Ghardaïa", "Relizane", "Timimoun", "Bordj Badji Mokhtar", "Ouled Djellal",
    "Béni Abbès", "In Salah", "In Guezzam", "Touggourt", "Djanet", "El M'Ghair",
    "El Meniaa"
]

# Palabras clave para detectar intención de la pregunta
WILAYA_LIST_KEYWORDS = ["wilayas", "wilaya", "livraison", "livrez", "disponible", "zones", "tewsil", "wين", "kayen", "mta3"]
LOGISTICS_KEYWORDS = [
    "logistique", "transporteur", "charika", "ta3 tewsil",
    "société de livraison", "livreur", "yalidine", "zr express",
    "maystro", "procolis", "guepex", "ecotrack", "noest",
    "qui livre", "partenaire", "logis"
]
PRODUCT_KEYWORDS = [
    "produit", "article", "collection", "stock", "disponible", "catalogue",
    "produits", "articles", "mta3", "3andha", "kamel", "wach", "chno",
    "catalogue", "affiche", "montre", "voir", "liste", "bda3", "haja",
    "lweh", "kifah", "afficher", "show", "3andi", "fih", "fiha",
    "prix", "thaman", "bekam", "b9adem", "b7al", "b9ash","منتجات","منتج","Sel3a"
]
DESCRIPTION_KEYWORDS = ["description", "boutique", "magasin", "hanouta", "chno", "c'est quoi", "présente", "parle"]

def detect_wilaya_in_question(question: str) -> str | None:
    question_lower = question.lower()
    for wilaya in WILAYAS:
        if wilaya.lower() in question_lower:
            return wilaya
    return None

def detect_intent(question: str) -> dict:
    question_lower = question.lower()
    return {
        "wants_all_wilayas": any(k in question_lower for k in WILAYA_LIST_KEYWORDS),
        "wants_logistics": any(k in question_lower for k in LOGISTICS_KEYWORDS),
        "wants_products": any(k in question_lower for k in PRODUCT_KEYWORDS),
        "wants_description": any(k in question_lower for k in DESCRIPTION_KEYWORDS),
    }

async def chat_with_store_service(db, store_id: str, question: str, history: list) -> str:

    # Comprobamos que la tienda existe
    store = select_store_by_id(db, store_id)
    if not store:
        raise NotFoundException("Store not found")

    # Detectamos intención de la pregunta
    intent = detect_intent(question)
    wilaya_mentioned = detect_wilaya_in_question(question)

    context_parts = []

    # Siempre añadimos contexto base de la tienda
    store_context = (
        f"Store:{store.name}. "
        f"Description:{store.description or 'N/A'}. "
        f"Type:{store.type}. "
        f"Logistics:{store.logistics_partner or 'N/A'}."
    )
    context_parts.append(store_context)

    # Si pregunta por todas las wilayas disponibles — buscamos directo en Aurora DSQL
    if intent["wants_all_wilayas"] and not wilaya_mentioned:
        rates = get_all_store_rates(db, store_id)
        if rates:
            wilayas_text = f"Store:{store.name}. Wilayas disponibles: "
            wilayas_text += ", ".join([f"{r.wilaya_name}({r.wilaya_id})" for r in rates])
            context_parts.append(wilayas_text)

    # Si pregunta por una wilaya concreta — buscamos directo en Aurora DSQL
    if wilaya_mentioned:
        rates = get_all_store_rates(db, store_id)
        rate = next(
            (r for r in rates if wilaya_mentioned.lower() in r.wilaya_name.lower()),
            None
        )
        if rate:
            wilaya_context = (
                f"Store:{store.name}. "
                f"Wilaya:{rate.wilaya_name}({rate.wilaya_id}). "
                f"Domicile:{rate.delivery_price}DA. "
                f"Bureau:{rate.office_price or 'N/A'}DA. "
                f"Days:{rate.estimated_days or 'N/A'}."
            )
            context_parts.insert(0, wilaya_context)

    # Si pregunta por productos — buscamos directo en Aurora DSQL
    if intent["wants_products"]:
        products_data = get_products_by_store(db, store_id)
        products = products_data.get("products", []) if isinstance(products_data, dict) else products_data
        
        if products:
            products_list_info = []
            for p in products[:10]:
                # Obtener la imagen principal del producto
                p_id = getattr(p, "id", None) or (p.get("id") if isinstance(p, dict) else None)
                p_name = getattr(p, "name", None) or (p.get("name") if isinstance(p, dict) else "Produit")
                p_price = getattr(p, "price", None) or (p.get("price") if isinstance(p, dict) else "")

                img = get_primary_image_by_product_id(db, p_id) if p_id else None
                img_url = "N/A"
                if img:
                    img_url = getattr(img, "image_url", None) or getattr(img, "url", None) or (img.get("image_url") if isinstance(img, dict) else "N/A")
                if not img_url or img_url == "N/A":
                    img_url = getattr(p, "image_url", None) or getattr(p, "image", None) or (p.get("image_url") if isinstance(p, dict) else "N/A")

                products_list_info.append(
                    f"Nom: {p_name} | Prix: {p_price} DA | ImageURL: {img_url}"
                )
            
            products_text = f"Store: {store.name}.\nProduits disponibles:\n" + "\n".join(products_list_info)
            context_parts.append(products_text)

    # Búsqueda semántica en Qdrant para el resto de preguntas
    question_vector = await generate_embedding(question)
    results = await search_points(question_vector, store_id, limit=3)
    for r in results:
        text = r["payload"].get("text", "")
        if text and text not in context_parts:
            context_parts.append(text)

    if not context_parts:
        return "Cette boutique n'a pas encore été indexée. Veuillez réessayer plus tard."

    context = "\n".join(context_parts)

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
Los idiomas permitidos son: francés, árabe clásico y darija argelina.
NUNCA respondas en español bajo ninguna circunstancia.
Si no tienes información suficiente para responder, dilo claramente.
No inventes información que no esté en el contexto.
Si el usuario pregunta por un producto o catálogo y en el contexto dispones de su "ImageURL" válida (diferente de N/A), incluye la imagen del producto en formato Markdown: ![Nombre del Producto](ImageURL) junto a su precio.
No inventes información ni URLs que no estén en el contexto.

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