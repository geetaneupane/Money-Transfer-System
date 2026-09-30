from datetime import datetime

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transfer_id: int
    transaction_type: str
    amount_minor: int
    balance_after: int
    created_at: datetime

#schema for getting transaction history and pagination
class TransactionHistoryResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
#next we'll write SQLAlchemy orm code equivalent to RAW SQL in repositories/transaction.py
