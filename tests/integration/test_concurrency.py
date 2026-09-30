from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from app.core.exceptions import InsufficientFundsError
from app.db.session import SessionLocal
from app.models.accounts import Account
from app.models.transaction import Transaction
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate
from app.services.transfer_service import create_transfer


def test_concurrent_transfers_do_not_overspend() -> None:
    setup_session = SessionLocal()

    source = Account(
        owner_name=f"Concurrent Source {uuid4()}",
        currency="USD",
        balance_minor=1000,
    )
    destination = Account(
        owner_name=f"Concurrent Destination {uuid4()}",
        currency="USD",
        balance_minor=0,
    )

    setup_session.add_all([source, destination])
    setup_session.commit()

    source_id = source.id
    destination_id = destination.id

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

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(
                executor.map(make_transfer, range(10))
            )

        setup_session.refresh(source)
        setup_session.refresh(destination)

        successful_transfers = sum(results)

        assert successful_transfers == 5
        assert source.balance_minor == 0
        assert destination.balance_minor == 1000
        assert source.balance_minor >= 0

    finally:
        transfer_ids = setup_session.scalars(
            Transfer.__table__.select().where(
                Transfer.source_account_id == source_id
            )
        ).all()

        for transfer_id in transfer_ids:
            setup_session.query(Transaction).filter(
                Transaction.transfer_id == transfer_id
            ).delete(synchronize_session=False)

        setup_session.query(Transfer).filter(
            Transfer.source_account_id == source_id
        ).delete(synchronize_session=False)

        setup_session.delete(source)
        setup_session.delete(destination)
        setup_session.commit()
        setup_session.close()