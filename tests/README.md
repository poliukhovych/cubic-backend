# Tests

## Setup
```bash
pip install pytest pytest-asyncio httpx
```

## Run Tests
```bash
# All tests
py -m pytest tests/ -v

# Database tests only
py -m pytest tests/test_simple.py -v

# Service tests only
py -m pytest tests/services/test_group_service_simple.py -v
```

## Database
Tests use local PostgreSQL:
- Host: localhost:5432
- Database: schedule_db
- User: postgres
- Password: 1234

Make sure PostgreSQL is running before running tests.
