from sqlalchemy import Column, String, Numeric, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import enum
import uuid

# Estados del pedido
class OrderStatus(enum.Enum):
    pending = "pending"           
    confirmed = "confirmed"      
    preparing = "preparing"       
    shipped = "shipped"           
    delivered = "delivered"      
    cancelled = "cancelled"       
    returned = "returned"      

# Tabla principal de pedidos
class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    address_id = Column(String(36), nullable=False, index=True)
    
    # NUEVO: Muy importante para que el dueño filtre sus pedidos rápido
    store_id = Column(String(36), nullable=False, index=True)
    
    status = Column(SQLEnum(OrderStatus, native_enum=False, length=20), 
                    nullable=False, default=OrderStatus.pending)
    
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # NUEVO: Tracking number para cuando el estado sea 'shipped'
    tracking_number = Column(String(100), nullable=True)
    
    notes = Column(String(500), nullable=True)
    
    # Relación con items (permitiendo guardado en cascada)
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    
    # Fechas de hitos para métricas y correos
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)

    product_id = Column(String(36), nullable=False, index=True)
    variant_id = Column(String(36), nullable=True, index=True)

    order = relationship("Order", back_populates="items")
    
    # Relaciones para traer info al serializar el pedido
    product = relationship("Product", viewonly=True, 
                           primaryjoin="foreign(OrderItem.product_id) == Product.id")
    variant = relationship("ProductVariant", viewonly=True, 
                           primaryjoin="foreign(OrderItem.variant_id) == ProductVariant.id")

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False) 
    total_price = Column(Numeric(10, 2), nullable=False)
