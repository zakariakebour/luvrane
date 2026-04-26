from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

#Enum de estados del pedido para schemas
class OrderStatusSchema(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"

#Schema de entrada para crear item del pedido
class OrderItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0)

#Schema de respuesta de item del pedido
class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True

#Schema de entrada para crear pedido
class OrderCreate(BaseModel):
    address_id: str
    notes: Optional[str] = Field(None, max_length=500)
    items: List[OrderItemCreate] = Field(..., min_length=1)

#Schema para actualizar estado del pedido
class OrderUpdateStatus(BaseModel):
    status: OrderStatusSchema

#Schema de respuesta del pedido
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

#Schema de paginacion de pedidos
class OrdersPageResponse(BaseModel):
    total: int
    orders: List[OrderResponse]