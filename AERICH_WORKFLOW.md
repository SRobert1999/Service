# 🔄 Aerich Migration Guide - IMPLEMENTARE FINALĂ

## 📋 Overview

Ghid complet pentru sistemul de migrări implementat corect în proiectul de programări.

---

## 🏗️ Arhitectura Finală a Sistemului

### 1. Fișiere de Migrări (Existente ACUM)

```
services/backend/
├── migrations/
│   ├── models/
│   │   ├── __init__.py
│   │   └── 1_20251103141033_None.py     # Migrarea inițială cu schema
│   └── models.py                        # Metadata
├── apply_migration.py                    # Script aplicare migrări
├── migrations/test_data.py               # Date de test
└── db/config.py                         # Configurație Aerich
```

### 2. Docker Compose Configurat Corect

```yaml
backend:
  build: ./services/backend
  command: >
    sh -c "
    mkdir -p /tmp/db &&
    python apply_migration.py &&
    python migrations/test_data.py &&
    uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
    "
```

---

## 🔍 Cum Funcționează Sistemul ACUM

### La `docker-compose up`:

1. **`mkdir -p /tmp/db`** - Creează directorul pentru baza de date
2. **`python apply_migration.py`** - Aplică automat toate migrările
   - Verifică dacă migrările sunt deja aplicate
   - Dacă nu, aplică SQL-ul din fișierele de migrare
   - Inserează înregistrări în tabelul `aerich`
3. **`python migrations/test_data.py`** - Populează cu date de test
   - Jobs (Stomatolog, Mecanic, etc.)
   - Persoane (Popescu Ion, etc.)
   - Servicii (Consultații, reparații, etc.)
   - Programări sample
   - Utilizatori default
4. **`uvicorn`** - Pornește server-ul FastAPI

### Tabelul `aerich` în Baza de Date:

```sql
CREATE TABLE "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);

-- Înregistrare după migrarea inițială:
INSERT INTO aerich VALUES
(1, '1_20251103141033_None', 'models', '{}');
```

---

## 📝 Workflow pentru Dezvoltatori

### 🔄 Când Modifici Structura Bazei de Date

**Pasul 1: Modifică Modelele**
```python
# În db/models.py
class Persoane(Model):
    # ... câmpuri existente
    adresa = fields.CharField(max_length=200, null=True)  # NOU
```

**Pasul 2: Generează Migrarea Nouă**
```bash
docker-compose exec backend aerich migrate --name add_adresa_to_persoane
```

**Ce se întâmplă:**
- Se creează fișier nou: `migrations/models/2_YYYYMMDDHHMMSS_add_adresa_to_persoane.py`
- Conține SQL `ALTER TABLE Persoane ADD COLUMN adresa VARCHAR(200)`

**Pasul 3: Aplică Migrarea (Automat la Docker Compose)**
```bash
# Opțional - poți aplica manual pentru test:
docker-compose exec backend aerich upgrade

# Sau doar restart:
docker-compose restart backend
```

**Pasul 4: Dă Commit la Cod**
```bash
git add migrations/models/2_YYYYMMDDHHMMSS_add_adresa_to_persoane.py
git add db/models.py
git commit -m "Add address field to Persoane model"
git push
```

---

## 🚀 Setup pentru un Nou Dezvoltator

### Ce face un nou dev când clonează proiectul:

```bash
# 1. Clonează repository-ul
git clone <repository-url>
cd Service

# 2. Pornește Docker
docker-compose up -d
```

**Ce se întâmplă automat:**
1. **Build containers** - Se construiesc imaginile Docker
2. **apply_migration.py** - Aplică migrarea `1_20251103141033_None.py`
   - Creează toate tabelele: Job, Persoane, Servicii, PersoanaJob, Programari, Users
   - Adaugă indecșii și constraint-urile
   - Inserează înregistrare în tabelul `aerich`
3. **test_data.py** - Populează cu date de test complete
4. **Server startup** - Pornește backend + frontend

**Rezultat:** Aplicație complet funcțională cu date de test!

---

## 🛠️ Comenzi Utilitare

### Comenzi Aerich
```bash
# Afișează versiunea curentă
docker-compose exec backend aerich heads

# Afișează istoricul migrărilor
docker-compose exec backend aerich history

# Generează migrare nouă
docker-compose exec backend aerich migrate --name descriere_modificare

# Aplică migrări (se face automat)
docker-compose exec backend aerich upgrade

# Revenire la versiune anterioară
docker-compose exec backend aerich downgrade
```

### Verificare Bază de Date
```bash
# Verifică tabelele create
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
print('Tables:', [row[0] for row in cursor.fetchall()])
conn.close()
"

# Verifică migrările aplicate
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM aerich;')
print('Migrations:', cursor.fetchall())
conn.close()
"
```

---

## 🔧 Troubleshooting

### ❌ Eroare: "No upgrade items found" dar tabelele nu există
**Problemă:** Tabelul `aerich` spune că migrarea e aplicată dar tabelele nu există
**Soluție:** Șterge baza de date și lasă migrările să se aplice:
```bash
docker-compose down -v
docker-compose up -d
```

### ❌ Eroare: "Database file not found"
**Problemă:** Permisiuni sau cale greșită pentru baza de date
**Soluție:** Verifică `DATABASE_URL` în `db/config.py`:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tmp/db/programari.db")
```

### ❌ Eroare: "Migration failed"
**Problemă:** SQL-ul din migrare are erori
**Soluție:** Verifică fișierul de migrare și corectează SQL-ul

### ❌ Eroare: "Table already exists"
**Problemă:** Se încearcă aplicarea duplicată a migrării
**Soluție:** Scriptul `apply_migration.py` e idempotent - nu face nimic dacă migrarea e deja aplicată

---

## 📁 Structura Fișierelor de Migrări

### Fișier de Migrare Exemplu
```python
# migrations/models/2_20251103150000_add_adresa_to_persoane.py

from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "Persoane" ADD COLUMN "adresa" VARCHAR(200);
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Pentru SQLite, ar necesita recreere tabel
        """
```

### Script de Aplicare Migrări
```python
# apply_migration.py - Acest script verifică și aplică migrările
# Este idempotent - poate fi rulat de mai multe ori
# Gestionează automat tabela aerich
# Aplică migrările în ordinea corectă
```

### Script Date de Test
```python
# migrations/test_data.py - Doar date, nu schema
# Jobs, Persoane, Servicii, Programări, Users
# Poate fi rulat repetat fără probleme (cu verificări)
```

---

## 🎯 Best Practices

### 1. **Separarea Responsabilităților**
- **Migrări** (`migrations/models/`) - Doar schema bazei de date
- **Date de test** (`migrations/test_data.py`) - Doar date inițiale
- **Aplicare** (`apply_migration.py`) - Logică de aplicare migrări

### 2. **Versionare Corectă**
- Commit mereu fișierele de migrări
- Nu commit baza de date (`*.db`)
- Nume descriptive pentru migrări

### 3. **Testare**
- Testează migrările local înainte de commit
- Verifică că API-ul funcționează după migrări
- Testează cu date goale și cu date existente

### 4. **Rollback**
- Păstrează funcțiile `downgrade()` în migrări
- Testează rollback-ul pentru migrări critice
- Documentează procedura de rollback

---

## 📊 Status Actual al Implementării

### ✅ Funcționalități Implementate:
- [x] Migrări Aerich generate corect
- [x] Script aplicare automată migrări
- [x] Date de test separate de schema
- [x] Docker Compose configurat corect
- [x] Tabel `aerich` funcțional
- [x] API funcțional cu date complete
- [x] Frontend funcțional
- [x] Sistem idempotent (poate fi rulat repetat)

### 🔧 Fișiere Create/Modificate:
- `migrations/models/1_20251103141033_None.py` - Migrare inițială
- `apply_migration.py` - Script aplicare migrări
- `migrations/test_data.py` - Date de test
- `docker-compose.yml` - Configurat cu scripturi corecte
- `db/config.py` - Corectat DATABASE_URL

### 📝 Documentație:
- `AERICH_WORKFLOW.md` - Acest ghid complet
- `aerich.md` - Documentație generală (actualizată)

---

## 🚀 Concluzie

**Sistemul de migrări este acum complet funcțional și corect implementat:**

1. **Un nou dezvoltator** poate clona și rula `docker-compose up -d` și are aplicație completă
2. **Dezvoltatorii existenți** pot modifica modelele și genera migrări ușor
3. **Sistemul e robust** - idempotent, cu rollback, versionat corect
4. **Separare clară** între schema și datele de test
5. **Integrare perfectă** cu Docker și workflow-ul de dezvoltare

**Proiectul este ready pentru teamwork și deployment în producție!**