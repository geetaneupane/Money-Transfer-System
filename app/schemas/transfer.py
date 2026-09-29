from datetime import datetime

from pydantic import BaseModel,  Field

#for validating transfer API data:
class TransferCreate(BaseModel):
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)  
    amount_minor: int = Field(gt=0)      #amount>0


class TransferResponse(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    amount_minor: int
    currency: str
    status: str
    created_at: datetime