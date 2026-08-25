# moduls/users/api/__init__.py
from moduls.users.api.user_router import router as user_router
from moduls.users.api.address_api import router as address_router
from moduls.users.api.likes_api import router as likes_router
from moduls.users.api.cart_api import router as cart_router