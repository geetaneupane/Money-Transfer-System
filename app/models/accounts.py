from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

#creating accounts table in the database.

class Account(Base):
    __tablename__="accounts"
    __table_args__=(
        CheckConstraint(            #using database constraint.
               "balance_minor >= 0",
               name="check_accounts_balance_is_non_negative",
        ),
    )


    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    owner_name:Mapped[str]=mapped_column(String(length=120))
    currency:Mapped[str]=mapped_column(String(3))
    balance_minor:Mapped[int]=mapped_column(Integer, default=0)   #$23.40= 2340cents, using integer, avoiding floating points.
    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


