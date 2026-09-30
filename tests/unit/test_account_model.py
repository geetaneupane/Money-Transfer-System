from app.models.accounts import Account


def test_account_has_non_negative_balance_constraint() -> None:
    constraint_names = {
        constraint.name for constraint in Account.__table__.constraints
    }

    assert "check_accounts_balance_is_non_negative" in constraint_names

