from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transfer import Transfer


def get_transfer_by_idempotency_key(
    session: Session,
    idempotency_key: str,
) -> Transfer | None:
    statement = select(Transfer).where(
        Transfer.idempotency_key == idempotency_key
    )

    return session.scalar(statement)