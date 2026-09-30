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
DATABASE_URL=postgresql+psycopg://<username>:<password>@<host>:<port>/<database_name>
```



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

## Database Schema

### `accounts`

Stores account balances.

| Column | Description |
|---|---|
| `id` | Primary key |
| `owner_name` | Account owner name |
| `currency` | Three-letter currency code |
| `balance_minor` | Balance stored in integer minor units |
| `created_at` | Account creation timestamp |

Constraints:

- `id` is the primary key.
- `balance_minor` cannot be negative.

### `transfers`

Stores transfer operations.

| Column | Description |
|---|---|
| `id` | Primary key |
| `source_account_id` | Foreign key to `accounts.id` |
| `destination_account_id` | Foreign key to `accounts.id` |
| `amount_minor` | Transfer amount in minor units |
| `currency` | Transfer currency |
| `idempotency_key` | Unique request key |
| `status` | Transfer status |
| `created_at` | Transfer creation timestamp |

Constraints and indexes:

- `id` is the primary key.
- `source_account_id` references `accounts.id`.
- `destination_account_id` references `accounts.id`.
- `idempotency_key` is unique.
- Account ID columns are indexed.

### `transactions`

Stores the ledger entries produced by transfers.

| Column | Description |
|---|---|
| `id` | Primary key |
| `account_id` | Foreign key to `accounts.id` |
| `transfer_id` | Foreign key to `transfers.id` |
| `transaction_type` | `debit` or `credit` |
| `amount_minor` | Transaction amount in minor units |
| `balance_after` | Account balance after the transaction |
| `created_at` | Transaction creation timestamp |

Constraints and indexes:

- `id` is the primary key.
- `account_id` references `accounts.id`.
- `transfer_id` references `transfers.id`.
- `account_id` and `created_at` are indexed.

### `alembic_version`

Internal Alembic table used to track the latest applied migration. It is not part of the money-transfer business domain.
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

-**Atomic transfers** - Balance updates, transfer records, and ledger entries are committed together so partial transfers cannot occur.
- **Integer-based money representation** - Money is stored in minor units to avoid floating-point rounding errors.
- **Row-level locking** - `SELECT FOR UPDATE` prevents concurrent requests from overspending an account.
- **Negative-balance prevention** - Application validation and database constraints prevent invalid balances.
- **Idempotency** - Retry requests do not transfer money more than once.
- **Debit and credit ledger entries** - Each transfer records both sides of the money movement for auditing.
- **Transaction-history pagination** - Limit-offset pagination keeps the API simple while satisfying the history requirement.
- **Database migrations** - Alembic makes schema changes reproducible.
- **Docker PostgreSQL** - Docker provides a consistent local database environment.
- **Automated tests** - Unit, integration, API, and concurrency tests verify success and failure cases.
- **Layered architecture** - API, service, repository, schema, and model responsibilities remain separated.

## Skipped Work

The following were intentionally skipped to keep the work appropriately scoped:
-**Refunds and transfer reversals** - They require additional transfer states and accounting rules.
-**Multi-currency exchange** - Exchange rates and conversion logic are outside the assignment scope.
-**Cursor-based pagination** - Limit-offset pagination was sufficient and simpler for this project.
- **Unified error-response envelopes** - HTTP status codes and useful error details are implemented; a common error schema would be a future improvement.

## Trade-offs and Future Improvements

Limit-offset pagination was chosen because it is simple and sufficient for this assignment. Cursor pagination could be considered for very large histories.

Integer minor units were chosen instead of floating-point values to avoid monetary precision errors.

Synchronous SQLAlchemy sessions were chosen to keep the implementation straightforward while database row locks protect concurrent transfers.

With more time, I would add a shared error-response schema and global exception handlers, improve test database isolation, add structured logging, add CI checks, and expand tests for simultaneous duplicate idempotency requests.

## License

This project was created as part of Insyde.ai Backend Engineering Assignment.
