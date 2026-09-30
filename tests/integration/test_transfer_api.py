from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.accounts import Account


client = TestClient(app)


def test_repeated_transfer_request_returns_same_transfer() -> None:
    source_response = client.post(
        "/accounts",
        json={
            "owner_name": f"Idempotency Source {uuid4()}",
            "currency": "USD",
            "initial_balance_minor": 10000,
        },
    )

    destination_response = client.post(
        "/accounts",
        json={
            "owner_name": f"Idempotency Destination {uuid4()}",
            "currency": "USD",
            "initial_balance_minor": 1000,
        },
    )

    assert source_response.status_code == 201, source_response.text
    assert destination_response.status_code == 201, destination_response.text

    source_id = source_response.json()["id"]
    destination_id = destination_response.json()["id"]
    idempotency_key = f"api-idempotency-{uuid4()}"

    payload = {
        "source_account_id": source_id,
        "destination_account_id": destination_id,
        "amount_minor": 3000,
    }

    first_response = client.post(
        "/transfers",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert first_response.status_code == 201, first_response.text

    second_response = client.post(
        "/transfers",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert second_response.status_code == 201, second_response.text
    assert first_response.json()["id"] == second_response.json()["id"]

    session = SessionLocal()

    try:
        source_account = session.get(Account, source_id)
        destination_account = session.get(Account, destination_id)

        assert source_account is not None
        assert destination_account is not None

        assert source_account.balance_minor == 7000
        assert destination_account.balance_minor == 4000
    finally:
        session.close()


def test_transfer_requires_idempotency_key()-> None:
    response=client.post(
        "/transfers",
        json={
            "source_account_id": 1,
            "destination_account_id":2,
            "amount_minor": 100,
        },
    )

    assert response.status_code==422