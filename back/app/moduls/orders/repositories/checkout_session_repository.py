from sqlalchemy.orm import Session
from moduls.orders.modules import CheckoutSession

def create_checkout_session(db: Session, data: dict):
    session = CheckoutSession(**data)
    db.add(session)
    return session

def get_checkout_session_by_token(db: Session, token: str):
    return db.query(CheckoutSession).filter(
        CheckoutSession.confirmation_token == token
    ).first()