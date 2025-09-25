# Database Setup

## Switching between local and Docker database

The project supports two database connection options:

### 1. Local PostgreSQL database

To use local database:

1. Make sure PostgreSQL is running on `localhost:5432`
2. Use the `env.local` file - it's already configured for local database
3. Or copy the contents of `env.local` to the main configuration file

**Local database parameters:**
- Host: `localhost:5432`
- User: `postgres`
- Password: `1234`
- Database: `schedule_db`

### 2. Docker database

To use Docker database:

1. Use the `env.docker` file - it's configured for Docker database
2. Or copy the contents of `env.docker` to the main configuration file
3. Run `docker-compose up -d` to start the database

**Docker database parameters:**
- Host: `db:5432` (inside Docker network)
- User: `appuser`
- Password: `DB7x9Kp2RqLm4N8sTvW3yZ5`
- Database: `schedule_db`

## Quick switching

### Option 1: Using script (Recommended)
```bash
# Switch to local database
python switch_db.py local

# Switch to Docker database
python switch_db.py docker

# Show current configuration
python switch_db.py status
```

### Option 2: File renaming
```bash
# For local database
cp env.local env

# For Docker database
cp env.docker env
```

### Option 3: Direct use of env files
The application automatically picks up configuration from files:
- `env` (main)
- `env.local` (local database)
- `env.docker` (Docker database)
- `env.development` (for docker-compose)

## Running

### Local database
```bash
python run.py
```

### Docker database
```bash
docker-compose up -d
```

## Connection check

The application will output information about which database it connected to on startup.
