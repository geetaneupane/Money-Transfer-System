
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


#schema for validating incoming account creation data:
class AccountCreate(BaseModel):
    owner_name: str = Field(min_length=1, max_length=120)
    currency: str = Field(min_length=3, max_length=3)
    initial_balance_minor: int = Field(ge=0)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.upper()

        if not value.isalpha():
            raise ValueError("Currency must contain only letters")

        return value

#schema for validating the data to be returned to the clients:

class AccountResponse(BaseModel):
    id: int
    owner_name: str
    currency: str
    balance_minor: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  #from_attributes allow Pydantic to convert SQLAlchemy Account object into an API response.