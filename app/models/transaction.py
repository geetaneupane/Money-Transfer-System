from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


#Added Database indexes on account_id and created_at. 
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True     #adding index for account_id in transaction table. 
    )
    transfer_id: Mapped[int] = mapped_column(
        ForeignKey("transfers.id"),
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(length=10),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    balance_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True 
    )