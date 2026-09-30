from app.db.session import SessionLocal
from app.models.accounts import Account
from app.schemas.transfer import TransferCreate
from app.services.transfer_service import create_transfer
from uuid import uuid4


def test_create_transfer_updates_balances() -> None:
    session = SessionLocal()

    source = Account(
        owner_name="Source",
        currency="USD",
        balance_minor=10000,
    )
    destination = Account(
        owner_name="Destination",
        currency="USD",
        balance_minor=2000,
    )

    session.add_all([source, destination])
    session.commit()

    transfer = create_transfer(
        session,
        TransferCreate(
            source_account_id=source.id,
            destination_account_id=destination.id,
            amount_minor=3000,
        ),
        f"simple-transfer-test-{uuid4()}",
    )

    session.refresh(source)
    session.refresh(destination)

    assert transfer.status == "completed"
    assert source.balance_minor == 7000
    assert destination.balance_minor == 5000

    session.close()