from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (AccountNotFoundError,InsufficientFundsError,InvalidTransferError)
from app.db.dependencies import get_db
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.transfer_service import create_transfer


router = APIRouter(
    prefix="/transfers",
    tags=["transfers"],
)

@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer_endpoint(
    transfer_data: TransferCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),   #idempotency key requestko headerma pathainxa.
    session: Session = Depends(get_db),
) -> TransferResponse:
    try:
        return create_transfer(
            session=session,
            transfer_data=transfer_data,
            idempotency_key=idempotency_key,
        )
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidTransferError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except InsufficientFundsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error