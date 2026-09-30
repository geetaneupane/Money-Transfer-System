from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories.transaction_repository import get_account_transactions
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import TransactionHistoryResponse
from app.services.account_service import create_new_account, get_account

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("",response_model=AccountResponse,status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    session: Session = Depends(get_db),    #dependency injection.
) -> AccountResponse:
    return create_new_account(session, account_data)

#for GET /accounts/{id}:
@router.get(
    "/{account_id}",
    response_model=AccountResponse,
)
def get_account_details(
    account_id: int,
    session: Session = Depends(get_db),
) -> AccountResponse:
    account = get_account(session, account_id)

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account



#for GET /accounts/{account_id}/transactions?page=2&page_size=20
@router.get(
    "/{account_id}/transactions",
    response_model=TransactionHistoryResponse,
)
def get_transactions(
    account_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> TransactionHistoryResponse:
    if get_account(session, account_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    items, total = get_account_transactions(
        session,
        account_id,
        page,
        page_size,
    )

    return TransactionHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
