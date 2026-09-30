from app.models.transaction import Transaction


def test_transaction_table_definition() -> None:
    assert Transaction.__tablename__ == "transactions"

    assert "account_id" in Transaction.__table__.columns
    assert "transfer_id" in Transaction.__table__.columns
    assert "transaction_type" in Transaction.__table__.columns
    assert "amount_minor" in Transaction.__table__.columns
    assert "balance_after" in Transaction.__table__.columns