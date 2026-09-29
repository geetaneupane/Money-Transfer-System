from app.models.transfer import Transfer


def test_transfer_table_definition() -> None:
    assert Transfer.__tablename__ == "transfers"

    assert "source_account_id" in Transfer.__table__.columns
    assert "destination_account_id" in Transfer.__table__.columns
    assert "amount_minor" in Transfer.__table__.columns
    assert "currency" in Transfer.__table__.columns
    assert "idempotency_key" in Transfer.__table__.columns
    assert "status" in Transfer.__table__.columns


def test_transfer_has_unique_idempotency_key() -> None:
    constraints = Transfer.__table__.constraints

    assert any(
        constraint.name == "uq_transfers_idempotency_key"
        for constraint in constraints
    )