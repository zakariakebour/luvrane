from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
#Importamos manejador global de excepciones
from core.exceptions import AppException
from fastapi.responses import JSONResponse
#Importamos Mangum para adaptarlo a lambda
from mangum import Mangum
#Importamos routers de usuarios
from moduls.users.api import user_router, address_router, likes_router, cart_router
#Importamos routers de tiendas
from moduls.stores.api.api import router as store_router
from moduls.stores.api.store_logist_api import router as store_logist_router
#Importamos routers de productos
from moduls.products.api.product_route import router as product_router
from moduls.products.api.product_image import router as product_image_router
from moduls.products.api.product_variant import router as product_variant_router
#Importamos los endpoints de gestion de pedidos
from moduls.orders.api.order_api import router as order_router
#Para registro ORM en lambda — orden importa para evitar circular imports
from moduls.users.modules import User, UserAddress, CartItem, ProductLike
from moduls.products.modules import Product, ProductVariant, ProductImage
from moduls.stores.modules import Store, ShippingRate
from moduls.orders.modules import Order, OrderItem, CheckoutSession, OrderStatus

#Creamos la aplicacion
app = FastAPI(
    title="luvrane API",
    version="1.0.0"
)

#Configuramos CORS para que el frontend pueda acceder
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://luvrane.com",
        "https://www.luvrane.com",
        "https://luvrane-front-84kg-git-main-zakariakebour-archs-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Manejador global de excepciones personalizadas
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

#Registramos todos los routers
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(address_router, prefix="/api/v1/users/addresses")
app.include_router(likes_router, prefix="/api/v1/users/likes")
app.include_router(cart_router, prefix="/api/v1/users/cart")
app.include_router(store_router, prefix="/api/v1/stores")
app.include_router(store_logist_router, prefix="/api/v1/stores")
app.include_router(product_router, prefix="/api/v1/products")        
app.include_router(product_image_router, prefix="/api/v1/products/images")  
app.include_router(product_variant_router, prefix="/api/v1/products/variants")
app.include_router(order_router, prefix="/api/v1")

#Endpoint de salud para verificar que la API esta funcionando
@app.get("/health")
def health():
    return {"status": "ok"}

# Adaptador de Mangum interno
asgi_handler = Mangum(app, lifespan="off")

# Nuevo punto de entrada principal
def lambda_handler(event, context):
    # Si el evento NO tiene 'requestContext', es el luvrane-warmup de cada 5 min
    if 'requestContext' not in event:
        return {"statusCode": 200, "body": "Evento"}
    
    # Si es una petición real de un usuario, usamos Mangum
    return asgi_handler(event, context)