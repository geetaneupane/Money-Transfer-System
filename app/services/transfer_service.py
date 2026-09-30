from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (AccountNotFoundError,InsufficientFundsError,InvalidTransferError,IdempotencyConflictError)
from app.models.transaction import Transaction
from app.models.transfer import Transfer
from app.repositories.account_repository import get_accounts_for_update
from app.repositories.transfer_repository import get_transfer_by_idempotency_key
from app.schemas.transfer import TransferCreate


def create_transfer(session: Session,transfer_data: TransferCreate,idempotency_key: str) -> Transfer:
    existing_transfer = get_transfer_by_idempotency_key(
        session,
        idempotency_key,
    )

    if existing_transfer is not None:
        same_request = (
            existing_transfer.source_account_id
            == transfer_data.source_account_id
            and existing_transfer.destination_account_id
            == transfer_data.destination_account_id
            and existing_transfer.amount_minor
            == transfer_data.amount_minor
        )

        if not same_request:
            raise IdempotencyConflictError(
                "Idempotency key was already used for another transfer"
            )
    
        return existing_transfer

    if (
        transfer_data.source_account_id
        == transfer_data.destination_account_id
    ):
        raise InvalidTransferError(
            "Source and destination accounts must be different"
        )

    accounts = get_accounts_for_update(
        session,
        [
            transfer_data.source_account_id,
            transfer_data.destination_account_id,
        ],
    )

    source_account = accounts[transfer_data.source_account_id]
    destination_account = accounts[transfer_data.destination_account_id]

    if source_account is None or destination_account is None:
        raise AccountNotFoundError(
            "One or both accounts were not found"
        )

    if source_account.balance_minor < transfer_data.amount_minor:
        raise InsufficientFundsError("Insufficient funds")

    source_account.balance_minor -= transfer_data.amount_minor
    destination_account.balance_minor += transfer_data.amount_minor

    transfer = Transfer(
        source_account_id=source_account.id,
        destination_account_id=destination_account.id,
        amount_minor=transfer_data.amount_minor,
        currency=source_account.currency,
        idempotency_key=idempotency_key,
        status="completed",
    )

    session.add(transfer)
    try:
        session.flush()

        session.add_all(
            [
                Transaction(
                    account_id=source_account.id,
                    transfer_id=transfer.id,
                    transaction_type="debit",
                    amount_minor=transfer_data.amount_minor,
                    balance_after=source_account.balance_minor,
                ),
                Transaction(
                    account_id=destination_account.id,
                    transfer_id=transfer.id,
                    transaction_type="credit",
                    amount_minor=transfer_data.amount_minor,
                    balance_after=destination_account.balance_minor,
                ),
            ]
        )

        session.commit()
    except IntegrityError:
        session.rollback()
    
        existing_transfer = get_transfer_by_idempotency_key(
            session,
            idempotency_key,
        )
    
        if existing_transfer is not None:
            return existing_transfer

        raise

    session.refresh(transfer)

    return transfer

#the create_transfer function is equivalent to the following raw sql query i.e. transaction query:
# BEGIN;

# -- Lock both accounts in a deterministic order
# SELECT id, currency, balance_minor
# FROM accounts
# WHERE id IN (:source_account_id, :destination_account_id)
# ORDER BY id
# FOR UPDATE;

# -- Application validates:
# -- - both accounts exist
# -- - source and destination are different
# -- - source has enough funds

# UPDATE accounts
# SET balance_minor = balance_minor - :amount_minor
# WHERE id = :source_account_id;

# UPDATE accounts
# SET balance_minor = balance_minor + :amount_minor
# WHERE id = :destination_account_id;

# INSERT INTO transfers (source_account_id, destination_account_id, amount_minor, currency, idempotency_key, status)
# VALUES (:source_account_id, :destination_account_id, :amount_minor, :currency, :idempotency_key,'completed')
# RETURNING id;

# -- Use the returned transfer ID below
# INSERT INTO transactions (account_id,transfer_id,transaction_type,amount_minor,balance_after)
# VALUES (:source_account_id,:transfer_id,'debit', :amount_minor,:source_balance_after);

# INSERT INTO transactions (account_id,transfer_id,transaction_type,amount_minor,balance_after)
# VALUES (:destination_account_id,:transfer_id,'credit',:amount_minor,:destination_balance_after);

# COMMIT;

# if error rolls back:
# ROLLBACK: