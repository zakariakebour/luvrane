from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from core.exceptions import (NotFoundException, ValidationException)
from moduls.orders.modules import OrderStatus
from moduls.orders.repositories.order_repository import (get_orders_by_checkout_session)
from moduls.orders.repositories.checkout_session_repository import (get_checkout_session_by_token)
from moduls.products.repositories.product_repository import (get_product_by_id)
from moduls.products.repositories.product_variant import (get_product_variant_by_id)
from moduls.users.repositories.cart_repository import (clear_cart)
from moduls.users.repositories.user_repository import get_user_by_id
from moduls.users.repositories.address_repository import get_direction_by_id
from core.order_email_service import send_order_email

def confirm_checkout_service(db: Session, token: str, background_tasks: BackgroundTasks):
    try:

        session = get_checkout_session_by_token(db, token)

        if not session:
            raise NotFoundException("Session de commande introuvable")

        #Tiempo de comparacion
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            raise ValidationException("Le lien de confirmation a expiré")

        if session.is_confirmed:
            raise ValidationException("Cette commande a déjà été confirmée")

        orders = get_orders_by_checkout_session(db, session.id)

        if not orders:
            raise NotFoundException("Aucune commande associée à cette session")

        for order in orders:
            order.status = OrderStatus.confirmed
            order.confirmed_at = datetime.now(timezone.utc)

        session.is_confirmed = True

        clear_cart(db, session.user_id)

        db.commit()

        customer = get_user_by_id(db, session.user_id)

        if orders:
            address = get_direction_by_id(db, orders[0].address_id)

            background_tasks.add_task(
                send_order_email,
                customer.email,
                "order_confirmed",
                orders,
                getattr(address, "full_name", None) or "Client",
            )

        return {
            "message": "Commande confirmée avec succès",
            "orders_count": len(orders)
        }

    except Exception as e:
        db.rollback()
        raise e