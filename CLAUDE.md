# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a **Docker-based full-stack appointment booking system** with:
- **Backend**: FastAPI + Tortoise ORM + SQLite
- **Frontend**: Vue.js 3 + Vue Router + Vuex + Bootstrap 5
- **Romanian-specific validation**: Phone numbers (+40), Romanian character support in names

### Key Architecture Decisions

**Database Schema**: Uses **snake_case** convention for all column names (`persoana_id`, `serviciu_id`, `data`, `ora`, etc.). Tortoise ORM models follow Python conventions without `source_field` mapping.

```python
# models.py
class Programari(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField('models.Persoana', related_name='programari', null=True)
    serviciu = fields.ForeignKeyField('models.Serviciu', related_name='programari', null=True)
    data = fields.CharField(max_length=50, null=True)
    # ...
```

**ForeignKey Relationships**: Uses proper `ForeignKeyField` relationships between tables:
- `Programari.persoana` → `Persoana` (CASCADE on delete)
- `Programari.serviciu` → `Serviciu` (CASCADE on delete)
- Tortoise automatically creates `persoana_id` and `serviciu_id` columns in the database

**Dual Validation Layers**:
1. **Pydantic models** (e.g., `ProgramareIn`) - API input validation with custom validators
2. **Tortoise ORM models** - Database mapping and relationships

The FastAPI flow is: `JSON input → Pydantic validation → dict → Tortoise ORM → SQLite`

## Development Commands

### Start/Stop Services
```bash
docker-compose up -d           # Start all services
docker-compose down            # Stop all services
docker-compose restart backend # Restart backend after code changes
docker-compose restart frontend
```

### Backend (FastAPI)
```bash
# Backend runs on http://localhost:5000
docker-compose logs -f backend              # View logs
docker-compose exec backend python -c "..." # Run Python commands
docker-compose up -d --build backend        # Rebuild after dependency changes

# API Documentation (auto-generated)
http://localhost:5000/docs  # Swagger UI
http://localhost:5000/redoc # ReDoc
```

### Frontend (Vue.js)
```bash
# Frontend runs on http://localhost:8080
docker-compose logs -f frontend             # View logs
docker-compose exec frontend npm run lint   # Lint code
docker-compose up -d --build frontend       # Rebuild after package.json changes
```

### Database Management
```bash
# Access SQLite database
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
# Run queries here
"

# Database migrations (Aerich)
docker-compose exec backend aerich init -t db.config.TORTOISE_ORM
docker-compose exec backend aerich init-db
docker-compose exec backend aerich migrate
docker-compose exec backend aerich upgrade
```

**IMPORTANT**: Database files (`*.db`, `*.db-shm`, `*.db-wal`) are in `.gitignore` and should never be committed.

## Critical Implementation Notes

### Adding New Fields to Programari

When adding fields to the `Programari` model:

1. **Add to Pydantic schema** (`main.py` → `ProgramareIn`)
2. **Add to Tortoise model** (`models.py` → use correct `source_field`)
3. **Add column to SQLite** with exact PascalCase name
4. **Update the create endpoint** to include the new field

Example:
```python
# 1. Pydantic (main.py)
class ProgramareIn(BaseModel):
    new_field: Optional[str] = Field(None, description="...")

# 2. Tortoise (models.py)
class Programari(Model):
    new_field = fields.CharField(null=True, source_field='NewField')

# 3. SQLite
ALTER TABLE Programari ADD COLUMN NewField TEXT;

# 4. Endpoint (main.py)
programare_data = {
    "new_field": prog.new_field,
    # ...
}
```

### CORS Configuration

Frontend origin is hardcoded in `main.py`:
```python
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]
```

Update this if frontend runs on different ports.

### Validation Rules

- **Date**: Must be YYYY-MM-DD format, cannot be in the past
- **Time**: Must be HH:MM format (24-hour)
- **Phone**: Romanian format `^(\+4|0)[0-9]{9}$` (e.g., +40712345678)
- **Email**: Requires `email-validator` package (Pydantic `EmailStr`)
- **Names**: Only letters and spaces allowed

### Database Schema

Tables:
- **Persoane** (ID, nume, prenume)
- **Servicii** (ID, descriere)
- **Programari** (ID, PersoanaId, ServiciuID, Data, Ora, Observatii, Nume, Prenume, Email, Telefon)

All column names in the database are **PascalCase**.
