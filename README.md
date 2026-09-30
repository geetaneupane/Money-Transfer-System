# Money Transfer System

An API-only money transfer system built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose, and Pytest.

## Features

- Create and retrieve accounts
- Transfer money between accounts
- Integer minor-unit money representation
- Atomic transfers with row-level locking
- Negative-balance prevention
- Debit and credit transaction ledger
- Limit-Offset based Paginated transaction history
- Idempotent transfer requests
- Concurrent transfer protection
- Database migrations and Docker PostgreSQL
- Swagger API documentation
- Unit, integration, and concurrency tests

## Technology Stack

- Python 3.11+
- FastAPI
- PostgreSQL 16
- SQLAlchemy
- Alembic
- Psycopg
- Pytest
- Docker Compose
- uv

## Requirements

- Python 3.11 or newer
- Docker Desktop
- uv

## Installation

Install dependencies:

```powershell
uv sync
```

Create a local `.env` file:

```env
DATABASE_URL=postgresql+psycopg://money_user:money_password@localhost:5434/money_transfer
```

Do not commit `.env`. Use `.env.example` as a reference.

## Start PostgreSQL

```powershell
docker compose up -d db
docker compose ps
```

PostgreSQL is exposed on host port `5434` and uses port `5432` inside the container.

## Run Migrations

```powershell
uv run alembic upgrade head
uv run alembic current
```

Main tables:

- `accounts`
- `transfers`
- `transactions`

## Start the API

```powershell
uv run uvicorn app.main:app --reload
```

API URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/accounts` | Create an account |
| GET | `/accounts/{id}` | Retrieve account details |
| POST | `/transfers` | Transfer money between accounts |
| GET | `/accounts/{id}/transactions` | Retrieve paginated transaction history |

## Example Requests

### Create an account

```json
{
  "owner_name": "Geeta",
  "currency": "USD",
  "initial_balance_minor": 10000
}
```

Money uses integer minor units:

```text
$100.00 = 10000 cents
```

### Create a transfer

Header:

```text
Idempotency-Key: unique-transfer-key
```

Body:

```json
{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount_minor": 3000
}
```

### Get transaction history

```text
GET /accounts/1/transactions?page=1&page_size=20
```

The endpoint uses limit-offset pagination and returns transaction items, total count, page, and page size.

## Consistency and Concurrency

Each transfer runs in one database transaction. The system:

1. Locks both account rows using `SELECT FOR UPDATE`.
2. Locks account IDs in deterministic order to reduce deadlocks.
3. Checks the source balance.
4. Updates both account balances.
5. Creates one transfer record.
6. Creates debit and credit ledger entries.
7. Commits all changes together.

If any step fails, the transaction rolls back.

The concurrency test sends multiple transfers against a limited balance and verifies that the source balance never becomes negative and money is neither lost nor created.

## Idempotency

Transfers require an `Idempotency-Key` header.

```text
Same key + same request data
→ return the original transfer
→ do not move money again
```

Reusing the same key with different transfer data returns `409 Conflict`. A unique database constraint protects the key.

## Validation and Status Codes

The API validates positive account IDs, positive transfer amounts, existing accounts, sufficient funds, and different source and destination accounts.

Used status codes include:

- `201 Created`
- `200 OK`
- `400 Bad Request`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`

## Project Structure

```text
app/
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── services/
└── main.py

alembic/
└── versions/

tests/
├── integration/
├── unit/
└── conftest.py
```

## Testing

Run all tests:

```powershell
uv run pytest
```


## Prioritized Work

The implementation prioritized:

- Correct atomic transfers
- Safe integer-based money representation
- Row-level locking and concurrency safety
- Negative-balance prevention
- Idempotency
- Debit and credit ledger entries
- Transaction-history pagination
- Database migrations
- Docker PostgreSQL
- Unit, integration, and concurrency tests
- Clear API, service, repository, and model separation

## Skipped Work

The following were intentionally skipped to keep the work appropriately scoped:
- Refunds and transfer reversals
- Multi-currency exchange
- Cursor-based pagination

## Trade-offs and Future Improvements

Limit-offset pagination was chosen because it is simple and sufficient for this assignment. Cursor pagination could be considered for very large histories.

Integer minor units were chosen instead of floating-point values to avoid monetary precision errors.

Synchronous SQLAlchemy sessions were chosen to keep the implementation straightforward while database row locks protect concurrent transfers.

With more time, I would add a shared error-response schema and global exception handlers, improve test database isolation, add structured logging, add CI checks, and expand tests for simultaneous duplicate idempotency requests.

## License

This project was created as part of Backend Engineering Assignment.
