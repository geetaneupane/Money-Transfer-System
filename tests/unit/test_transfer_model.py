from app.models.transfer import Transfer

def test_transfer_has_unique_idempotency_key() -> None:
    constraints = Transfer.__table__.constraints

    assert any(
        constraint.name == "uq_transfers_idempotency_key"
        for constraint in constraints
    )