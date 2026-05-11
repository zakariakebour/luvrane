from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

# Enum de estados del pedido para schemas (Sincronizado con el modelo)
class OrderStatusSchema(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"

#Items del perdido

# Schema de entrada para los items dentro de un pedido
class OrderItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0)

# Schema de respuesta de item del pedido con info útil para el cliente
class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    # Campo extra: Muy útil para no tener que hacer joins constantes en el front
    # product_name: Optional[str] = None 

    class Config:
        from_attributes = True

#Pedidos

# Schema de entrada para crear pedido (Desde el carrito o compra directa)
class OrderCreate(BaseModel):
    address_id: str
    notes: Optional[str] = Field(None, max_length=500)
    items: List[OrderItemCreate] = Field(..., min_length=1)

# Schema para que el Admin actualice el estado
class OrderUpdateStatus(BaseModel):
    status: OrderStatusSchema

# Schema de respuesta principal del pedido
class OrderResponse(BaseModel):
    id: str
    user_id: str
    address_id: str
    status: OrderStatusSchema
    total_price: Decimal
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # Esto permite que Pydantic maneje correctamente los objetos Decimal y Datetime
        json_encoders = {
            Decimal: lambda v: float(round(v, 2))
        }

# Listados

# Schema de paginación para el historial del usuario o panel de tienda
class OrdersPageResponse(BaseModel):
    total: int
    orders: List[OrderResponse]
    skip: int
    limit: int

    class Config:
        from_attributes = True