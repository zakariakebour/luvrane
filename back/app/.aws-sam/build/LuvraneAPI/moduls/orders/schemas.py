from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

# Enum de estados del pedido para schemas 
class OrderStatusSchema(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"
    pending_email_confirmation = "pending_email_confirmation"
    
class OrderItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0)

class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True

#Pedidos

class OrderCreate(BaseModel):
    address_id: str
    # Eliminamos store_id de aquí porque el sistema lo detectará 
    # automáticamente de los productos del carrito por seguridad.
    notes: Optional[str] = Field(None, max_length=500)
    items: List[OrderItemCreate] = Field(..., min_length=1)

class OrderUpdateStatus(BaseModel):
    status: OrderStatusSchema
    tracking_number: Optional[str] = None 

class OrderResponse(BaseModel):
    id: str
    user_id: str
    store_id: str # Añadido: Vital para el panel del dueño
    address_id: str
    status: OrderStatusSchema
    total_price: Decimal
    shipping_price: Decimal = Decimal("0.00")  # ← coste de envío por wilaya
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    
    # Hitos temporales completos para los correos de SES
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(round(v, 2)),
            datetime: lambda v: v.isoformat()
        }

#Listados
class OrdersPageResponse(BaseModel):
    total: int
    orders: List[OrderResponse]
    skip: int
    limit: int

    class Config:
        from_attributes = True