#Importamos metodos de repositorio de lista de productos de productos favoritos del usuario
from moduls.users.repositories.likes_repository import get_user_likes, add_like, remove_like, get_like
#Importamos excepciones
from core.exceptions import ValidationException, NotFoundException, ConflictException, ForbiddenException

#Metodo para agregar un producto a la lista de me gusta
def add_like_service(db, user_id: str, product_id: str):
    #Comprobamos si ya dio like a ese producto
    existing = get_like(db, user_id, product_id)
    if existing:
        raise ConflictException("Produit déjà ajouté aux favoris")

    #Añadimos producto a la lista
    return add_like(db, user_id, product_id)

#Metodo para seleccionar los productos de la lista de me gusta
def get_user_likes_service(db, user_id: str):
    #Seleccionamos los productos disponibles
    products = get_user_likes(db, user_id)

    #Si no hay productos en la lista devolvemos lista vacia, no error
    return products                                  

#Metodo para eliminar el producto de la lista
def remove_like_service(db, user_id: str, product_id: str):
    #Comprobamos si el like existe
    existing = get_like(db, user_id, product_id)
    if not existing:
        raise NotFoundException("Produit non trouvé dans les favoris")

    #Eliminamos el like
    remove_like(db, user_id, product_id)