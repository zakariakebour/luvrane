from sqlalchemy import Column, String, Numeric, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, object_session
from core.database import Base
from datetime import datetime, timezone
import enum
import uuid
from moduls.users.modules import UserAddress

class OrderStatus(enum.Enum):
    pending = "pending"           
    confirmed = "confirmed"      
    preparing = "preparing"       
    shipped = "shipped"           
    delivered = "delivered"      
    cancelled = "cancelled"       
    returned = "returned"
    pending_email_confirmation = "pending_email_confirmation"

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    address_id = Column(String(36), ForeignKey("user_addresses.id"), nullable=False, index=True)
    
    store_id = Column(String(36), nullable=False, index=True)
    
    status = Column(SQLEnum(OrderStatus, native_enum=False, length=50), 
                    nullable=False, default=OrderStatus.pending)
    
    total_price = Column(Numeric(10, 2), nullable=False)
    
    tracking_number = Column(String(100), nullable=True)
    
    notes = Column(String(500), nullable=True)
    
    checkout_session_id = Column(
        String(36),
        ForeignKey("checkout_sessions.id"),
        nullable=True
    )

    shipping_price = Column(Numeric(10, 2), nullable=False, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    address_rel = relationship(
        "UserAddress",
        primaryjoin="foreign(Order.address_id) == UserAddress.id",
        viewonly=True
    )

    @property
    def address(self):
        if self.address_rel:
            return self.address_rel
        session = object_session(self)
        if session:
            return session.query(UserAddress).filter(UserAddress.id == self.address_id).first()
        return None  
    
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)

    product_id = Column(String(36), nullable=False, index=True)
    variant_id = Column(String(36), nullable=True, index=True)

    order = relationship("Order", back_populates="items")
    
    product = relationship("Product", viewonly=True, 
                           primaryjoin="foreign(OrderItem.product_id) == Product.id")
    variant = relationship("ProductVariant", viewonly=True, 
                           primaryjoin="foreign(OrderItem.variant_id) == ProductVariant.id")

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False) 
    total_price = Column(Numeric(10, 2), nullable=False)

class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String(36), nullable=False)

    confirmation_token = Column(String(255), unique=True, nullable=False)

    is_confirmed = Column(Boolean, default=False)

    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))