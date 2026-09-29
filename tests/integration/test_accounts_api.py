from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.accounts import Account


client = TestClient(app)


def test_create_account() -> None:
    response = client.post(
        "/accounts",
        json={
            "owner_name": "API Test",
            "currency": "usd",
            "initial_balance_minor": 10000,
        },
    )

    assert response.status_code == 201

    account_data = response.json()

    assert account_data["id"] is not None
    assert account_data["owner_name"] == "API Test"
    assert account_data["currency"] == "USD"
    assert account_data["balance_minor"] == 10000
    assert account_data["created_at"] is not None

    session = SessionLocal()

    try:
        account = session.get(Account, account_data["id"])

        assert account is not None

        session.delete(account)
        session.commit()
    finally:
        session.close()