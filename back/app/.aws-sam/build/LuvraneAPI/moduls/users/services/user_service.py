from moduls.users.repositories.user_repository import (
    get_user,
    get_user_by_email,
    get_user_by_name,                                      
    delete_user,
    update_user,
    create_user
)
from core.security import (
    hash_password,
    verify_password,
    create_access_token,                                           
    decode_token,
    create_refresh_token
)
from core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException
)
#Importamos metodos de Google OAuth
from core.google_auth import exchange_google_code, verify_google_token  

#Metodo para crear usuario
def create_user_service(db, user_data):
    #Comprobamos que el email no exista ya
    if get_user_by_email(db, user_data.email):
        raise ConflictException("Cet email est déjà utilisé")

    #Comprobamos que el username no exista ya
    if get_user_by_name(db, user_data.username):              
        raise ConflictException("Ce nom d'utilisateur est déjà utilisé")

    #Convertimos a diccionario
    user_dict = user_data.model_dump()

    #Hasheamos la contraseña y eliminamos la original del diccionario
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

    return create_user(db, user_dict)

#Metodo para acceso de usuario con email y contraseña
def login_service(db, user_data):
    #Buscamos el usuario por correo
    user = get_user_by_email(db, user_data.email)

    #Si no existe lanzamos error
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    #Si la cuenta esta desactivada
    if not user.is_active:
        raise ForbiddenException("Compte désactivé")

    #Verificamos que la contraseña sea correcta
    if not verify_password(user_data.password, user.hashed_password):
        raise UnauthorizedException("Mot de passe incorrect")

    #Generamos los tokens
    access_token = create_access_token(user.id, user.role.value)  
    refresh_token = create_refresh_token(user.id)

    #Devolvemos los tokens y datos basicos del usuario
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role.value
    }

#Metodo para renovar el access token con el refresh token
def refresh_token_service(refresh_token: str):
    #Verificamos que el refresh token sea valido
    payload = decode_token(refresh_token)

    #Extraemos el user_id del payload
    user_id = payload.get("sub")

    #Si no hay user_id en el token
    if not user_id:
        raise UnauthorizedException("Token invalide")

    #Generamos nuevo access token
    new_access_token = create_access_token(user_id, payload.get("role", "customer"))  

    #Devolvemos el nuevo access token
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

#Metodo para login con Google OAuth completo
async def google_login_service(db, code: str):               
    #Intercambiamos el code por tokens de Google
    google_tokens = await exchange_google_code(code)

    #Verificamos el token y obtenemos datos del usuario de Google
    google_user = verify_google_token(google_tokens["id_token"])

    #Buscamos si el usuario ya existe en nuestra DB por email
    user = get_user_by_email(db, google_user["email"])

    #Si no existe lo creamos automaticamente
    if not user:
        #Generamos username desde el nombre de Google
        base_username = google_user["name"].replace(" ", "_").lower()

        #Comprobamos que el username no exista ya
        existing = get_user_by_name(db, base_username)
        if existing:
            base_username = f"{base_username}_{google_user['sub'][:5]}" 

        user_dict = {
            "email": google_user["email"],
            "username": base_username,
            "hashed_password": "",
            "google_id": google_user["sub"],
            "avatar": google_user.get("picture"),
            "auth_provider": "google",
            "is_active": True
        }
        user = create_user(db, user_dict)

    #Si la cuenta esta desactivada
    if not user.is_active:
        raise ForbiddenException("Compte désactivé")

    #Generamos nuestros propios JWT igual que el login normal
    access_token = create_access_token(user.id, user.role.value)  
    refresh_token = create_refresh_token(user.id)

    #Devolvemos los tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role.value
    }

#Metodo para obtener usuario por identificador
def get_user_service(db, user_id: str):
    #Buscamos el usuario
    user = get_user(db, user_id)

    #Si no existe lanzamos error
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    return user

#Metodo para actualizar datos del usuario
def update_user_service(db, user_id: str, user_data):
    #Buscamos el usuario
    user = get_user(db, user_id)

    #Si no existe lanzamos error
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    #Convertimos a diccionario ignorando campos None
    user_dict = user_data.model_dump(exclude_none=True)

    #Si quiere cambiar email comprobamos que no exista en otro usuario
    if "email" in user_dict:
        existing = get_user_by_email(db, user_dict["email"])
        if existing and existing.id != user_id:
            raise ConflictException("Cet email est déjà utilisé")

    #Si quiere cambiar username comprobamos que no exista en otro usuario
    if "username" in user_dict:
        existing = get_user_by_name(db, user_dict["username"])  
        if existing and existing.id != user_id:
            raise ConflictException("Ce nom d'utilisateur est déjà utilisé")

    return update_user(db, user, user_dict)

#Metodo para desactivar cuenta de usuario
def delete_user_service(db, user_id: str):
    #Buscamos el usuario
    user = get_user(db, user_id)

    #Si no existe lanzamos error
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    #Si ya esta desactivado
    if not user.is_active:
        raise ForbiddenException("Compte déjà désactivé")

    return delete_user(db, user)

#Metodo para cambiar contraseña del usuario
def change_password_service(db, user_id: str, password_data):
    #Buscamos el usuario
    user = get_user(db, user_id)

    #Si no existe lanzamos error
    if not user:
        raise NotFoundException("Utilisateur introuvable")

    #Verificamos que la contraseña antigua sea correcta
    if not verify_password(password_data.old_password, user.hashed_password):
        raise UnauthorizedException("Ancien mot de passe incorrect")

    #Hasheamos la nueva contraseña y la guardamos
    user_dict = {"hashed_password": hash_password(password_data.new_password)}

    return update_user(db, user, user_dict)

