import pytest
from pydantic import ValidationError

from app.schemas.transfer import TransferCreate


def test_transfer_create_accepts_valid_data() -> None:
    transfer = TransferCreate(
        source_account_id=1,
        destination_account_id=2,
        amount_minor=500,
    )

    assert transfer.amount_minor == 500


def test_transfer_create_rejects_zero_amount() -> None:
    with pytest.raises(ValidationError):
        TransferCreate(
            source_account_id=1,
            destination_account_id=2,
            amount_minor=0,
        )


def test_transfer_create_rejects_negative_account_id() -> None:
    with pytest.raises(ValidationError):
        TransferCreate(
            source_account_id=-1,
            destination_account_id=2,
            amount_minor=500,
        )