# 📋 Programari API - Database Migration Workflow

## 🏗️ Arhitectură

**Stack:**
- Backend: FastAPI + Tortoise ORM + SQLite
- Frontend: Vue.js 3
- Migrări: Aerich (automat la pornire)
- Schema: **snake_case** cu **ForeignKey relationships**

---

## 🚀 Quick Start

### **Prima rulare:**

```bash
# 1. Clonează repository
git clone <repo-url>
cd Service

# 2. Pornește serviciile (migrările se aplică automat)
docker-compose up -d

# Backend: http://localhost:5000
# Frontend: http://localhost:8080
# API Docs: http://localhost:5000/docs
```

### ⚠️ **DUPĂ GIT PULL (Important pentru colegi!):**

```bash
# 1. Pull modificări
git pull

# 2. Verifică dacă sunt fișiere noi în migrations/models/
# Dacă DA, șterge baza de date:
rm services/backend/db/programari.db*

# 3. Restart (migrările se aplică automat)
docker-compose down
docker-compose up -d

# ✅ Schema nouă este aplicată automat
```

---

## 🔄 Workflow Migrări Database (Aerich)

### 📊 Cum Funcționează

```
┌─────────────────────────────────────────────────────────────┐
│  La fiecare docker-compose up / restart:                    │
├─────────────────────────────────────────────────────────────┤
│  1. aerich upgrade    ← Aplică automat migrările existente  │
│  2. uvicorn ...       ← Pornește serverul FastAPI           │
└─────────────────────────────────────────────────────────────┘

Schema Database (snake_case + ForeignKey):
├─ Persoane (id, nume, prenume)
├─ Servicii (id, descriere)
└─ Programari (id, persoana_id, serviciu_id, data, ora, ...)
   ├─ FK: persoana_id → Persoane.id (CASCADE)
   └─ FK: serviciu_id → Servicii.id (CASCADE)
```

### ✅ Pași pentru Modificări Schema

#### **1. Modifică Modelul**

```python
# services/backend/db/models.py

class Programari(Model):
    # ... câmpuri existente
    status = fields.CharField(max_length=20, default="pending")  # ← câmp nou

# IMPORTANT:
# ✅ Folosește snake_case: persoana_id, data_expirare
# ✅ Pentru relații: ForeignKeyField('models.Persoana', ...)
# ❌ NU folosi: IntField pentru FK
# ❌ NU folosi: source_field (nu mai este necesar)
```

#### **2. Generează Migrarea (MANUAL)**

```bash
docker-compose exec backend aerich migrate --name "add_status_field"
```

**Ce face:**
- Compară schema curentă din DB cu modelele Python
- Generează fișier SQL în `migrations/models/`
- Exemplu: `1_20251007_add_status_field.py`

#### **3. Restart Backend (AUTOMAT)**

```bash
docker-compose restart backend
```

**Ce se întâmplă automat:**
- `aerich upgrade` - Aplică migrarea nouă în DB
- Backend pornește cu schema actualizată

---

## 📝 Comenzi Utile

### Database Migrations

```bash
# Vezi istoricul migrărilor
docker-compose exec backend aerich history

# Vezi migrările aplicate
docker-compose exec backend aerich heads

# Revin la versiune anterioară (cu grijă!)
docker-compose exec backend aerich downgrade
```

### Backend Management

```bash
# Restart după modificări cod
docker-compose restart backend

# Vezi logs live
docker-compose logs -f backend

# Rebuild după schimbări dependencies
docker-compose up -d --build backend
```

### Database Inspection

```bash
# Inspectează schema tabelelor
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(Programari)')
for row in cursor.fetchall():
    print(f'{row[1]} ({row[2]})')
conn.close()
"

# Query date din tabel
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM Programari LIMIT 5')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

---

## 🔧 Exemple Modificări Schema

### Adaugă Câmp Nou

```python
# models.py
class Programari(Model):
    status = fields.CharField(max_length=20, default="confirmed")
```

```bash
docker-compose exec backend aerich migrate --name "add_status"
docker-compose restart backend
```

### Modifică Câmp Existent

```python
# models.py
class Programari(Model):
    email = fields.CharField(max_length=255, null=True)  # ← mărit de la 200
```

```bash
docker-compose exec backend aerich migrate --name "increase_email_length"
docker-compose restart backend
```

### Șterge Câmp

```python
# models.py - șterge linia
# telefon = fields.CharField(...)  ← comentat/șters
```

```bash
docker-compose exec backend aerich migrate --name "remove_telefon"
docker-compose restart backend
```

### Adaugă Index

```python
# models.py
class Programari(Model):
    data = fields.CharField(max_length=50, index=True)  # ← adăugat index
```

```bash
docker-compose exec backend aerich migrate --name "add_data_index"
docker-compose restart backend
```

### Adaugă ForeignKey

```python
# models.py
class Programari(Model):
    user = fields.ForeignKeyField(
        'models.User',
        related_name='programari',
        on_delete=fields.CASCADE,
        null=True
    )
```

```bash
docker-compose exec backend aerich migrate --name "add_user_fk"
docker-compose restart backend
```

---

## 🗂️ Structură Fișiere

```
services/backend/
├── db/
│   ├── config.py              # Configurație Tortoise ORM
│   ├── models.py              # Modele (snake_case, ForeignKeyField)
│   └── programari.db          # SQLite database (git ignored)
├── migrations/
│   └── models/
│       ├── 0_20251007094343_init.py  # Migrare inițială (snake_case)
│       └── 1_*.py                     # Migrări ulterioare
├── src/
│   └── main.py                # FastAPI app + endpoints + validări
├── pyproject.toml             # Configurație Aerich
├── requirements.txt           # Dependencies Python
└── Dockerfile

services/frontend/
├── src/
│   ├── components/
│   ├── views/
│   └── router/
├── package.json
└── Dockerfile
```

---

## ⚠️ Reguli Importante

### ✅ DO

- **ÎNTOTDEAUNA** generează migrare după modificări în `models.py`
- **COMMIT** fișierele de migrare în git
- **TEST** migrările local înainte de producție
- **VERIFICĂ** logs după restart: `docker-compose logs backend`
- **FOLOSEȘTE** snake_case pentru toate câmpurile: `persoana_id`, `data_expirare`
- **FOLOSEȘTE** ForeignKeyField pentru relații, NU IntField
- **CITEȘTE** sectiunea "DUPĂ GIT PULL" când faci update

### ❌ DON'T

- **NU edita manual** fișierele de migrare (dacă nu știi exact ce faci)
- **NU șterge** directorul `migrations/`
- **NU commit** fișierele `*.db`, `*.db-shm`, `*.db-wal` (sunt în `.gitignore`)
- **NU rula** `aerich upgrade` manual (se face automat la restart)
- **NU folosi** PascalCase sau camelCase pentru câmpuri
- **NU folosi** `source_field` în modele (nu mai este necesar)

---

## 🐛 Troubleshooting

### Backend nu pornește după migrare

```bash
# Verifică logs pentru erori
docker-compose logs backend

# Verifică ultima migrare
docker-compose exec backend aerich history

# Verifică schema actuală
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(Programari)')
for row in cursor.fetchall():
    print(f'{row[1]} ({row[2]})')
conn.close()
"
```

### Migrarea eșuează

```bash
# Revin la versiunea anterioară
docker-compose exec backend aerich downgrade

# Fix problema în models.py
# Generează migrare nouă
docker-compose exec backend aerich migrate --name "fix_issue"
docker-compose restart backend
```

### Eroare: "Inited models already"

```bash
# Acest error apare când încerci aerich init-db pe un sistem deja inițializat
# Pentru migrări noi, folosește:
docker-compose exec backend aerich migrate --name "descriere"
docker-compose restart backend

# Pentru reset complet, vezi secțiunea de mai jos
```

### Schema veche (PascalCase) după git pull

```bash
# Dacă vezi erori legate de coloane care nu există:
# 1. Șterge baza de date veche
rm services/backend/db/programari.db*

# 2. Restart - migrările snake_case se aplică automat
docker-compose down
docker-compose up -d
```

### Reset complet DB (DEV only!)

```bash
# ⚠️ ATENȚIE: Șterge toate datele!

# Opțiunea 1: Păstrează migrările (recomandat)
docker-compose down
rm services/backend/db/programari.db*
docker-compose up -d
# Migrările existente se aplică automat

# Opțiunea 2: Reset total (inclusiv migrări)
docker-compose down
rm services/backend/db/programari.db*
rm services/backend/migrations/models/*.py
docker-compose up -d backend
docker-compose exec backend aerich init -t db.config.TORTOISE_ORM
docker-compose exec backend aerich init-db
docker-compose down
# Apoi restaurează aerich upgrade în docker-compose.yml
docker-compose up -d
```

---

## 📚 Resurse

- [Tortoise ORM Docs](https://tortoise.github.io/)
- [Aerich Docs](https://github.com/tortoise/aerich)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLite PRAGMA](https://www.sqlite.org/pragma.html)

---

## 🎯 Workflow Zilnic Tipic

### **Pentru Developer (Tu - când faci modificări):**

```bash
# 1. Pull ultimele modificări
git pull

# 2. Dacă sunt modificări la schema, reset DB
rm services/backend/db/programari.db*

# 3. Pornește serviciile (migrările se aplică automat)
docker-compose up -d

# 4. Verifică că totul merge
curl http://localhost:5000/

# 5. Faci modificări în models.py
nano services/backend/db/models.py

# 6. Generezi migrare
docker-compose exec backend aerich migrate --name "add_status_field"

# 7. Restart (migrarea se aplică automat)
docker-compose restart backend

# 8. Test
curl http://localhost:5000/programari

# 9. Commit & push
git add services/backend/migrations/models/
git add services/backend/db/models.py
git commit -m "Add: status field to Programari"
git push
```

### **Pentru Colegi (După git pull):**

```bash
# 1. Pull modificări
git pull

# 2. Verifică dacă sunt fișiere noi în migrations/models/
ls services/backend/migrations/models/

# 3. Dacă vezi fișiere noi, fă reset DB:
rm services/backend/db/programari.db*

# 4. Restart (migrările se aplică automat)
docker-compose down
docker-compose up -d

# 5. Verifică
curl http://localhost:5000/programari

# ✅ Gata! Schema nouă aplicată automat
```

---

## 📋 Migration History

| Data | Versiune | Descriere | Breaking Change |
|------|----------|-----------|-----------------|
| 2025-10-07 | `0_20251007094343_init.py` | Schema inițială cu snake_case și ForeignKey relationships | ✅ **YES** - Reset DB necesar pentru cei cu schema veche PascalCase |

### **Detalii Breaking Change (2025-10-07):**

**Ce s-a schimbat:**
- ✅ Toate coloanele DB acum folosesc **snake_case** (`persoana_id`, nu `PersoanaId`)
- ✅ ForeignKey-uri reale cu **CASCADE on delete**
- ✅ Nu mai folosim `source_field` în models.py
- ✅ Aerich upgrade automat la pornire

**Dacă ai bază de date veche (înainte de 2025-10-07):**
```bash
# TREBUIE să ștergi baza veche
rm services/backend/db/programari.db*
docker-compose down
docker-compose up -d
```

---

**Autor:** Robert
**Data:** 2025-10-07
**Versiune:** 1.0
**Last Updated:** 2025-10-07
