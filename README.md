# Shipment Management API

An asynchronous REST API for managing sellers, delivery partners, shipments, and shipment tracking events. Built with FastAPI, SQLModel/SQLAlchemy, PostgreSQL, Redis, and JWT authentication.

## Features

- Seller and delivery-partner registration and login
- JWT access-token authentication and Redis-based token revocation
- Shipment creation, retrieval, updates, and cancellation
- Delivery-partner assignment based on destination ZIP code and available capacity
- Shipment tracking timeline through events
- Asynchronous PostgreSQL database access
- Alembic migration configuration
- Interactive API documentation

## Tech Stack

- Python and FastAPI
- SQLModel / SQLAlchemy AsyncIO
- PostgreSQL and `asyncpg`
- Alembic
- PyJWT
- Redis
- Pydantic Settings
- Uvicorn

## Project Structure

```text
app/
├── main.py
├── config.py
├── utils.py
├── api/
│   ├── router.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── seller.py
│   │   ├── delivery_partner.py
│   │   └── shipment.py
│   └── schemas/
├── core/security.py
├── database/
│   ├── models.py
│   ├── session.py
│   └── redis.py
└── services/
    ├── base.py
    ├── user.py
    ├── seller.py
    ├── delivery_partner.py
    ├── shipment.py
    └── shipment_event.py

migration/
├── env.py
└── versions/
```

## How It Works

1. A seller registers and logs in to receive a JWT.
2. The seller creates a shipment.
3. The backend searches for a delivery partner that supports the destination ZIP code and has available capacity.
4. The shipment is stored with its seller and assigned partner.
5. Shipment events record tracking updates.
6. Protected endpoints validate the token and enforce access checks.

## Main API Routes

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/seller/signup` | Register seller |
| `POST` | `/seller/token` | Seller login |
| `POST` | `/partner/signup` | Register delivery partner |
| `POST` | `/partner/token` | Partner login |
| `POST` | `/shipment/` | Create shipment |
| `GET` | `/shipment/?id={uuid}` | Retrieve shipment |
| `PATCH` | `/shipment/?id={uuid}` | Update shipment |

Other account and cancellation routes are available in the application. Check `/docs` for the exact current API contract.

## Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/Abdullah0617/Shipment.git
cd Shipment
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

Otherwise, install the packages used by the project (including FastAPI, Uvicorn, SQLModel, SQLAlchemy, asyncpg, Alembic, PyJWT, Redis, Pydantic Settings, and the password-hashing dependency used in `app/services/user.py`).

### 4. Configure environment variables

Create a local `.env` file in the project root. Use the exact variable names expected by `app/config.py`.

```dotenv
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_DB=shipment_db

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
```

Start PostgreSQL and Redis, then ensure the credentials match your local services. Never commit real `.env` values to GitHub.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

Open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Database

The project uses async SQLAlchemy sessions for database operations and includes Alembic configuration under `migration/`. Verify that the initial migration contains actual table-creation operations before using `alembic upgrade head`; the reviewed migration had empty `upgrade()` and `downgrade()` functions.

Use Alembic migrations for schema changes in deployment rather than relying on `create_all()` to update existing tables.

## Authentication and Security

- JWTs authenticate sellers and delivery partners.
- Redis stores revoked token IDs (`jti`).
- Validate JWT signature, expiry, `jti`, and user UUID before using claims.
- Return `401 Unauthorized` for malformed or expired tokens.
- Remove logs that print tokens or decoded JWT payloads.
- Add a TTL to Redis blacklist entries.
- Use explicit response schemas and enforce seller ownership/partner assignment on protected routes.
- Use short-lived access tokens and disable verbose SQL logging in production.

**Credential safety:** If a real `.env` file or secret was previously pushed to GitHub, rotate the database password and JWT secret. Deleting the file from the latest commit does not remove it from Git history.

## Known Items to Verify

- The reviewed initial Alembic migration was empty.
- Check JWT claim validation and remove token debug logging.
- Ensure update/cancel services handle missing shipments.
- Use `POST` or `PATCH` for state-changing operations such as logout and cancellation.
- Make shipment and event writes transactional.
- Exclude cancelled shipments from delivery-partner active capacity.
- Add tests for authentication, authorization, shipment lifecycle, and migrations.

## License

No license file was identified in the reviewed project. Add one if you plan to publish the project under an open-source license.
