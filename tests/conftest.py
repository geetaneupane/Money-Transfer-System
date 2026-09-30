from collections.abc import Callable, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.accounts import Account
from app.models.transaction import Transaction
from app.models.transfer import Transfer


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def create_account() -> Generator[Callable[[int], int], None, None]:
    account_ids: list[int] = []

    def factory(balance_minor: int) -> int:
        client = TestClient(app)

        response = client.post(
            "/accounts",
            json={
                "owner_name": f"Test Account {uuid4()}",
                "currency": "USD",
                "initial_balance_minor": balance_minor,
            },
        )

        assert response.status_code == 201

        account_id = response.json()["id"]
        account_ids.append(account_id)

        return account_id

    yield factory

    session = SessionLocal()

    try:
        transfer_ids = session.scalars(
            Transfer.__table__.select().where(
                (Transfer.source_account_id.in_(account_ids))
                | (Transfer.destination_account_id.in_(account_ids))
            )
        ).all()

        session.query(Transaction).filter(
            Transaction.transfer_id.in_(transfer_ids)
        ).delete(synchronize_session=False)

        session.query(Transfer).filter(
            (Transfer.source_account_id.in_(account_ids))
            | (Transfer.destination_account_id.in_(account_ids))
        ).delete(synchronize_session=False)

        session.query(Account).filter(
            Account.id.in_(account_ids)
        ).delete(synchronize_session=False)

        session.commit()
    finally:
        session.close()