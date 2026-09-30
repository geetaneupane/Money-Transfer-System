from sqlalchemy import select
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models.accounts import Account

#equivalent to writing raw sql INSERT INTO account ..... query

def create_account(
        session:Session,
        account:Account,   
)-> Account:
    session.add(account)
    session.commit()
    session.refresh(account)

    return account



#equivalent to writing SELECT * FROM account WHERE id=1;
def get_account_by_id(
        session:Session,
        account_id:int,
)-> Account | None:
    statement=select(Account).where(Account.id==account_id)
    return session.scalar(statement)

#writing equivalent raw SQL query for obtaining row level lock on certain row, RAW SQLko FOR UPDATE jastai use gareko:
def get_accounts_for_update(
    session: Session,
    account_ids: Sequence[int],
) -> dict[int, Account | None]:
    locked_accounts: dict[int, Account | None] = {}

    for account_id in sorted(set(account_ids)):
        statement = (
            select(Account)
            .where(Account.id == account_id)
            .with_for_update()
        )

        locked_accounts[account_id] = session.scalar(statement)

    return locked_accounts