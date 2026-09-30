from uuid import uuid4



def test_transaction_history_contains_debit_and_credit(
    client,
    create_account,
) -> None:
    source_id = create_account(10000)
    destination_id = create_account(1000)

    transfer_response = client.post(
        "/transfers",
        json={
            "source_account_id": source_id,
            "destination_account_id": destination_id,
            "amount_minor": 3000,
        },
        headers={"Idempotency-Key": f"history-{uuid4()}"},
    )

    assert transfer_response.status_code == 201

    transfer_id = transfer_response.json()["id"]

    source_response = client.get(
        f"/accounts/{source_id}/transactions",
        params={"page": 1, "page_size": 20},
    )

    destination_response = client.get(
        f"/accounts/{destination_id}/transactions",
        params={"page": 1, "page_size": 20},
    )

    assert source_response.status_code == 200
    assert destination_response.status_code == 200

    source_history = source_response.json()
    destination_history = destination_response.json()

    assert source_history["total"] == 1
    assert destination_history["total"] == 1

    source_transaction = source_history["items"][0]
    destination_transaction = destination_history["items"][0]

    assert source_transaction["transfer_id"] == transfer_id
    assert source_transaction["transaction_type"] == "debit"
    assert source_transaction["amount_minor"] == 3000
    assert source_transaction["balance_after"] == 7000

    assert destination_transaction["transfer_id"] == transfer_id
    assert destination_transaction["transaction_type"] == "credit"
    assert destination_transaction["amount_minor"] == 3000
    assert destination_transaction["balance_after"] == 4000