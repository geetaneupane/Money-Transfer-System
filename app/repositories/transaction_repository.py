from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def get_account_transactions(session: Session, account_id:int, page:int, page_size:int)-> tuple[list[Transaction], int]:
    #I have used LIMIT OFFSET pagination technique:
    #so that our our request format becomes:  GET /accounts/1/transactions?page=2&page_size=20  i.e. OFFSET 20 LIMIT 20 kinda.
    offset = (page - 1) * page_size

    items = session.scalars(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    total = session.scalar(      #returns one value.
        select(func.count())
        .select_from(Transaction)
        .where(Transaction.account_id == account_id)
    )

    return list(items), total or 0