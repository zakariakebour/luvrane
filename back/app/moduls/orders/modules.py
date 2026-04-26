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

    #Identificador del pedido
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    #Relacion con el usuario que realiza el pedido
    user_id = Column(String(36), nullable=False, index=True)

    user = relationship(
        "User",
        primaryjoin="foreign(Order.user_id) == User.id",
        viewonly=True
    )

    #Relacion con la direccion de envio
    address_id = Column(String(36), nullable=False, index=True)

    address = relationship(
        "UserAddress",
        primaryjoin="foreign(Order.address_id) == UserAddress.id",
        viewonly=True
    )

    #Estado del pedido
    status = Column(
        SQLEnum(
            OrderStatus,
            native_enum=False,
            length=20
        ),
        nullable=False,
        default=OrderStatus.pending
    )

    #Precio total del pedido
    total_price = Column(Numeric(10, 2), nullable=False)

    #Notas del pedido (instrucciones especiales)
    notes = Column(String(500), nullable=True)

    #Relacion con los items del pedido
    items = relationship(
        "OrderItem",
        primaryjoin="Order.id == foreign(OrderItem.order_id)",
        back_populates="order",
        viewonly=True
    )

    #Fecha de creacion del pedido
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #Fecha de ultima modificacion
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    #Fecha de entrega
    delivered_at = Column(DateTime, nullable=True)

    #Fecha de cancelacion
    cancelled_at = Column(DateTime, nullable=True)


#Tabla de items del pedido
class OrderItem(Base):
    __tablename__ = "order_items"

    #Identificador del item
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    #Relacion con el pedido
    order_id = Column(String(36), nullable=False, index=True)

    order = relationship(
        "Order",
        primaryjoin="foreign(OrderItem.order_id) == Order.id",
        back_populates="items",
        viewonly=True
    )

    #Relacion con el producto
    product_id = Column(String(36), nullable=False, index=True)

    product = relationship(
        "Product",
        primaryjoin="foreign(OrderItem.product_id) == Product.id",
        viewonly=True
    )

    #Relacion con la variante del producto
    variant_id = Column(String(36), nullable=True, index=True)

    variant = relationship(
        "ProductVariant",
        primaryjoin="foreign(OrderItem.variant_id) == ProductVariant.id",
        viewonly=True
    )

    #Cantidad del producto
    quantity = Column(Integer, nullable=False)

    #Precio unitario en el momento del pedido
    unit_price = Column(Numeric(10, 2), nullable=False)

    #Precio total del item
    total_price = Column(Numeric(10, 2), nullable=False)