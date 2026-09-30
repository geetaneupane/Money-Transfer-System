from sqlalchemy.orm import Session

from app.models.accounts import Account
from app.repositories.account_repository import create_account, get_account_by_id
from app.schemas.account import AccountCreate


def create_new_account(
    session: Session,
    account_data: AccountCreate,
) -> Account:
    account = Account(
        owner_name=account_data.owner_name,
        currency=account_data.currency,
        balance_minor=account_data.initial_balance_minor,
    )

    return create_account(session, account)



#for GET /users/{id} feature:
def get_account(
    session: Session,
    account_id: int,
) -> Account | None:
    return get_account_by_id(session, account_id)