class AccountNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class InvalidTransferError(Exception):
    pass

class IdempotencyConflictError(Exception):
    pass
