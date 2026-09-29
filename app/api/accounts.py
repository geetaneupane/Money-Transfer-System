from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import create_new_account


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("",response_model=AccountResponse,status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    session: Session = Depends(get_db),    #dependency injection.
) -> AccountResponse:
    return create_new_account(session, account_data)

