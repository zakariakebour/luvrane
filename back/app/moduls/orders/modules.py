from sqlalchemy import Column, String, Numeric, Integer, DateTime, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, foreign
from core.database import Base
from datetime import datetime, timezone
import enum
import uuid

#Estados del pedido
class OrderStatus(enum.Enum):
    pending = "pending"           
    confirmed = "confirmed"       
    preparing = "preparing"      
    shipped = "shipped"           
    delivered = "delivered"       
    cancelled = "cancelled"       
    returned = "returned"  
           
#Tabla principal de pedidos
class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    address_id = Column(String(36), nullable=False, index=True)
    
    status = Column(SQLEnum(OrderStatus, native_enum=False, length=20), 
                    nullable=False, default=OrderStatus.pending)
    
    total_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Cambiamos: Eliminamos viewonly para poder GUARDAR items al crear el pedido
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), Column(String(36), nullable=False, index=True))
    product_id = Column(String(36), nullable=False, index=True)
    variant_id = Column(String(36), nullable=True, index=True)

    order = relationship("Order", back_populates="items")
    
    # Estas pueden seguir siendo viewonly si prefieres
    product = relationship("Product", viewonly=True, 
                           primaryjoin="foreign(OrderItem.product_id) == Product.id")
    variant = relationship("ProductVariant", viewonly=True, 
                           primaryjoin="foreign(OrderItem.variant_id) == ProductVariant.id")

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False) 
    total_price = Column(Numeric(10, 2), nullable=False)