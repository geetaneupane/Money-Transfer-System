from sqlalchemy import select
from sqlalchemy.orm import Session

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

