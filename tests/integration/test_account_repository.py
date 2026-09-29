from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.accounts import Account
from app.repositories.account_repository import (
    create_account,
    get_account_by_id,
)


def test_create_and_get_account() -> None:
    session = SessionLocal()

    try:
        account = Account(owner_name="Repository Test", currency="USD", balance_minor=5000)

        created_account = create_account(session, account)
        found_account = get_account_by_id(session, created_account.id)

        assert created_account.id is not None
        assert found_account is not None
        assert found_account.owner_name == "Repository Test"
        assert found_account.currency == "USD"
        assert found_account.balance_minor == 5000

        session.delete(found_account)
        session.commit()
    finally:
        session.close()