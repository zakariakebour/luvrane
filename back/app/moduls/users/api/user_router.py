from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
#Importamos servicios
from moduls.users.services.user_service import (
    create_user_service,
    login_service,
    refresh_token_service,
    google_login_service,
    get_user_service,
    update_user_service,
    delete_user_service,
    change_password_service
)
#Importamos conexion a la base de datos
from core.database import get_db
#Importamos dependencia para obtener usuario autenticado
from core.dependencies import get_current_user
#Importamos modulo de usuario
from moduls.users.modules import User
#Importamos schemas
from moduls.users.schemas import  UserCreate,UserResponse,UserUpdate,UserChangePassword,LoginData,RefreshTokenData,GoogleCodeData

router = APIRouter(tags=["Users"])

#Endpoint para registro de usuario — publico
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)

#Endpoint para login con email y contraseña — publico
@router.post("/login")
def login(user_data: LoginData, db: Session = Depends(get_db)):
    return login_service(db, user_data)

#Endpoint para renovar el access token — publico
@router.post("/refresh")
def refresh(data: RefreshTokenData):
    return refresh_token_service(data.refresh_token)

#Endpoint para login con Google — publico
@router.post("/auth/google")
async def google_login(data: GoogleCodeData, db: Session = Depends(get_db)):
    return await google_login_service(db, data.code, data.role)

#Endpoint callback de Google — Google redirige aquí con el code
@router.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    return await google_login_service(db, code)

#Endpoint para obtener perfil del usuario autenticado — protegido
@router.get("/me", response_model=UserResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_service(db, current_user.id)

#Endpoint para actualizar perfil — protegido
@router.put("/me", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_user_service(db, current_user.id, user_data)

#Endpoint para cambiar contraseña — protegido
@router.put("/me/password")
def change_password(
    password_data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return change_password_service(db, current_user.id, password_data)

#Endpoint para desactivar cuenta — protegido
@router.delete("/me", response_model=UserResponse)
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_user_service(db, current_user.id)