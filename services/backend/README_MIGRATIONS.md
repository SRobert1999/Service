# Aerich Migration Guide

This document explains how to use Aerich for database migrations in this project.

## 🐳 Docker Migration Commands

The project includes a dedicated `backend-migrate` service for running migration commands.

### Available Commands

```bash
# Initialize migration system
docker-compose run --rm backend-migrate COMMAND=init

# Create initial migration
docker-compose run --rm backend-migrate COMMAND=init-db

# Create new migration
docker-compose run --rm backend-migrate COMMAND=migrate MIGRATION_NAME=add_new_field

# Apply migrations
docker-compose run --rm backend-migrate COMMAND=upgrade

# Rollback migrations
docker-compose run --rm backend-migrate COMMAND=downgrade

# Show migration heads
docker-compose run --rm backend-migrate COMMAND=heads

# Show migration history
docker-compose run --rm backend-migrate COMMAND=history
```

## 🔄 Workflow

### 1. Making Changes to Models

1. **Modify your models** in `db/models.py`
2. **Create migration:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=migrate MIGRATION_NAME=describe_your_changes
   ```
3. **Apply migration:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=upgrade
   ```

### 2. Initial Database Setup

For a fresh database setup:
```bash
docker-compose run --rm backend-migrate COMMAND=init-db
docker-compose run --rm backend-migrate COMMAND=upgrade
```

### 3. Development Workflow

When developing:
```bash
# Apply any pending migrations
docker-compose run --rm backend-migrate COMMAND=upgrade

# Start backend (automatically runs migrations)
docker-compose up backend
```

## 📁 File Structure

```
migrations/
├── models/
│   ├── __init__.py
│   └── 0_20251103112800_init.py    # Initial migration
└── models.py                        # Migration metadata
```

## 🗄️ Database Configuration

The database path is configured via the `DATABASE_URL` environment variable:

- **Development**: `sqlite:///tmp/db/programari.db`
- **Production**: Set via environment variables

## 🔧 Troubleshooting

### Migration Conflicts

If you encounter migration conflicts:
```bash
# Check current migration status
docker-compose run --rm backend-migrate COMMAND=history

# Rollback if needed
docker-compose run --rm backend-migrate COMMAND=downgrade
```

### Database Reset

To completely reset the database:
```bash
# Stop containers
docker-compose down -v

# Remove database volume
docker volume rm service_backend_db

# Start fresh
docker-compose up -d
```

### Manual Migration

If automated migration fails, you can manually run SQL commands:
```bash
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
# Your SQL here
conn.commit()
conn.close()
"
```

## 📝 Examples

### Adding a New Field

1. **Update model:**
   ```python
   # In db/models.py
   class Persoane(Model):
       # ... existing fields
       adresa = fields.CharField(max_length=200, null=True)  # NEW
   ```

2. **Create migration:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=migrate MIGRATION_NAME=add_adresa_to_persoane
   ```

3. **Apply migration:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=upgrade
   ```

### Creating New Table

1. **Add new model:**
   ```python
   # In db/models.py
   class Adrese(Model):
       id = fields.IntField(pk=True)
       strada = fields.CharField(max_length=100)
       # ... other fields
   ```

2. **Create and apply migration:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=migrate MIGRATION_NAME=create_adrese_table
   docker-compose run --rm backend-migrate COMMAND=upgrade
   ```

## 🚀 Production Deployment

For production deployment:

1. **Set production database URL:**
   ```yaml
   environment:
     - DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Run migrations:**
   ```bash
   docker-compose run --rm backend-migrate COMMAND=upgrade
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```