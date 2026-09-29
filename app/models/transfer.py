from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Transfer(Base):
    __tablename__ = "transfers"

    __table_args__ = (
        UniqueConstraint(
            "idempotency_key",    #creating idempotency key for removing the duplicate actions.
            #our client includes this idempotency key in a custom header along with the payload so taht the same actions couldnot be done twice.
            name="uq_transfers_idempotency_key",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
    )
    destination_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(length=3), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default="completed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )