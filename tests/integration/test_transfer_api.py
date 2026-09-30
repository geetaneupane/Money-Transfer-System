from uuid import uuid4


def test_repeated_transfer_returns_same_transfer(
    client,
    create_account,
) -> None:
    source_id = create_account(10000)
    destination_id = create_account(1000)
    idempotency_key = f"transfer-{uuid4()}"

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

    second_response = client.post(
        "/transfers",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] == second_response.json()["id"]

    source = client.get(f"/accounts/{source_id}").json()
    destination = client.get(f"/accounts/{destination_id}").json()

    assert source["balance_minor"] == 7000
    assert destination["balance_minor"] == 4000




def test_transfer_requires_idempotency_key(client)-> None:
    response=client.post(
        "/transfers",
        json={
            "source_account_id": 1,
            "destination_account_id":2,
            "amount_minor": 100,
        },
    )

    assert response.status_code==422

#testing transfer error task:
#tested tge following cases:  repeating the same request with same idempotency-key gives the same transfer, no transfer within same account,  trnasfer using missing accounts is rejected.
def test_transfer_rejects_self_transfer(client, create_account) -> None:
    account_id = create_account(1000)

    response = client.post(
        "/transfers",
        json={
            "source_account_id": account_id,
            "destination_account_id": account_id,
            "amount_minor": 100,
        },
        headers={"Idempotency-Key": f"self-{uuid4()}"},
    )

    assert response.status_code == 400


def test_transfer_rejects_missing_account(client) -> None:
    response = client.post(
        "/transfers",
        json={
            "source_account_id": 999999,
            "destination_account_id": 999998,
            "amount_minor": 100,
        },
        headers={"Idempotency-Key": f"missing-account-{uuid4()}"},
    )

    assert response.status_code == 404


#testing whether it rejects  the case when there is insufficent amount in the account:
def test_transfer_rejects_insufficient_funds(client, create_account) -> None:
    source_id = create_account(100)
    destination_id = create_account(0)

    response = client.post(
        "/transfers",
        json={
            "source_account_id": source_id,
            "destination_account_id": destination_id,
            "amount_minor": 500,
        },
        headers={"Idempotency-Key": f"insufficient-{uuid4()}"},
    )

    assert response.status_code == 409


def test_idempotency_key_cannot_be_reused_for_different_transfer(
    client,
    create_account,
) -> None:
    source_id = create_account(10000)
    destination_id = create_account(0)
    idempotency_key = f"conflict-{uuid4()}"

    first_response = client.post(
        "/transfers",
        json={
            "source_account_id": source_id,
            "destination_account_id": destination_id,
            "amount_minor": 1000,
        },
        headers={"Idempotency-Key": idempotency_key},
    )

    second_response = client.post(
        "/transfers",
        json={
            "source_account_id": source_id,
            "destination_account_id": destination_id,
            "amount_minor": 2000,
        },
        headers={"Idempotency-Key": idempotency_key},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409