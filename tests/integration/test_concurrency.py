from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from app.core.exceptions import InsufficientFundsError
from app.db.session import SessionLocal
from app.models.accounts import Account
from app.schemas.transfer import TransferCreate
from app.services.transfer_service import create_transfer


def test_concurrent_transfers_do_not_overspend(
    create_account,
) -> None:
    source_id = create_account(1000)
    destination_id = create_account(0)

    def make_transfer(index: int) -> bool:
        session = SessionLocal()

        try:
            create_transfer(
                session,
                TransferCreate(
                    source_account_id=source_id,
                    destination_account_id=destination_id,
                    amount_minor=200,
                ),
                f"concurrency-test-{uuid4()}-{index}",
            )
            return True
        except InsufficientFundsError:
            session.rollback()
            return False
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(make_transfer, range(10)))

    session = SessionLocal()

    try:
        source = session.get(Account, source_id)
        destination = session.get(Account, destination_id)

        assert source is not None
        assert destination is not None

        assert sum(results) == 5
        assert source.balance_minor == 0
        assert destination.balance_minor == 1000
        assert source.balance_minor >= 0
    finally:
        session.close()


