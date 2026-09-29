import pytest
from pydantic import ValidationError

from app.schemas.account import AccountCreate


def test_account_create_accepts_valid_data() -> None:
    account = AccountCreate(
        owner_name="Geeta",
        currency="usd",
        initial_balance_minor=10000,
    )

    assert account.owner_name == "Geeta"
    assert account.currency == "USD"
    assert account.initial_balance_minor == 10000

#validation error vayo vane matrai test pass garxa. 
def test_account_create_rejects_negative_balance() -> None:
    with pytest.raises(ValidationError):
        AccountCreate(
            owner_name="Geeta",
            currency="USD",
            initial_balance_minor=-1,
        )


def test_account_create_rejects_invalid_currency() -> None:
    with pytest.raises(ValidationError):
        AccountCreate(
            owner_name="Geeta",
            currency="US1",
            initial_balance_minor=10000,
        )