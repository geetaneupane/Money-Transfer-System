from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import create_new_account, get_account
from fastapi import APIRouter, Depends, HTTPException, status


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