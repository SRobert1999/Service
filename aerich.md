# 🔄 Aerich Migration Guide - Setup și Deploy pentru Proiecte Noi

## 📋 Overview

Acest ghid explică cum funcționează migrările Aerich în proiectul de programări și cum se configurează pentru ca un nou dezvoltator să poți rula proiectul din Docker fără baza de date.

## ⚠️ IMPORTANT: Analiza Situației Actuale

După analiza fișierelor din proiect, **sistemul actual NU folosește Aerich în mod standard**! În schimb, folosește 3 componente diferite:

1. **`apply_migration.py`** - Script manual care aplică migrările
2. **`test_data.py`** - Script pentru date de test
3. **Migrări Aerich standard** - NU sunt folosite în fluxul normal

## 🔍 Componentele Sistemului Actual (REALITATEA)

### 1. `apply_migration.py` - Script Manual de Aplicare

**Ce face exact acest script:**

```python
# Funcționalități principale:
1. Creează tabela 'aerich' pentru urmărirea migrărilor (liniile 21-28)
2. Găsește automat fișierele de migrare (linia 31)
3. Verifică ce migrări au fost deja aplicate (liniile 38-41)
4. Extrage SQL-ul din fișierele de migrare (liniile 49-65)
5. Aplică SQL-ul direct în baza de date (linia 70)
6. Înregistrează migrările aplicate (liniile 75-78)
```

**Rol și utilizare:**
- ✅ **Backup pentru Aerich standard** - Funcționează dacă `aerich upgrade` eșuează
- ✅ **Debugging** - Poți vedea exact ce SQL se execută
- ❌ **Nu e folosit în fluxul normal** - Doar pentru situații speciale
- ❌ **Manual process** - Nu detectează automat modificările de modele

**Cum funcționează:**
```bash
# Rulează manual (doar dacă e necesar)
docker-compose exec backend python apply_migration.py

# Output exemplu:
# Applying migration: 1_20251103141033_None
# Applying SQL for 1_20251103141033_None...
# Migration 1_20251103141033_None applied successfully!
# Final tables: ['Job', 'Persoane', 'Servicii', 'Programari', 'Users', 'aerich']
# Applied migrations: ['1_20251103141033_None', '2_20251103142500_simplify_tables']
```

### 2. `test_data.py` - Date de Test Inițiale

**Ce face exact acest script:**

```python
# Funcționalități principale:
1. Verifică dacă există deja date (previne duplicate) (liniile 32-37)
2. Creează job-uri de test: Stomatolog, Mecanic Auto, etc. (liniile 40-44)
3. Creează persoane test (liniile 47-51)
4. Creează servicii pentru fiecare job (liniile 54-62)
5. Asociază persoane cu job-uri (relații many-to-many) (liniile 64-73)
6. Creează programări example cu date viitoare (liniile 81-121)
7. Adaugă useri de test cu parola "parola123" (liniile 124-129)
```

**Date importante create:**
- **5 Job-uri**: Stomatolog, Mecanic Auto, Electrician, Altele, General
- **5 Persoane**: Popescu Ion, Ionescu Maria, Stan Radu, etc.
- **9 Servicii**: Consultație, Extracție, Revizie tehnică, etc.
- **3 Programări**: Cu status-uri 'pending' și 'confirmed'
- **3 Useri**: admin, user1, user2 (toate cu parola: `parola123`)

**Cum se folosește:**
```bash
# Automat la setup inițial
docker-compose exec backend python migrations/test_data.py

# Output:
# Adding initial test data...
# Date de test adăugate cu succes
```

### 3. Fișierele de Migrare Existente

**Structura actuală:**
```
migrations/models/
├── 1_20251103141033_None.py           # Prima migrare - creează toate tabelele
├── 2_20251103142500_simplify_tables.py # A doua migrare - simplifică tabelele
└── test_data.py                       # Date de test (nu e migrare)
```

**Migrarea 1 - `1_20251103141033_None.py`:**
- Creează tabelele: `Job`, `Persoane`, `Servicii`, `Programari`, `Users`
- Include indecși și foreign keys
- Creează și tabela `aerich` pentru urmărirea migrărilor

**Migrarea 2 - `2_20251103142500_simplify_tables.py`:**
- Elimină coloane suplimentare din `Persoane` (email, telefon, created_at, updated_at)
- Elimină coloane suplimentare din `Servicii` (durata_min, pret, created_at, updated_at)
- Folosește tehnica "create new table → copy data → drop old → rename"

---

## 🚀 Setup pentru un Coleg Nou (RĂSPUNS DIRECT)

### ✅ DA, docker-compose este DE AJUNS!

Un coleg nou poate porni totul cu **doar 2 comenzi**:

```bash
# 1. Clonează repository-ul
git clone <repository-url>
cd Service

# 2. Pornește totul cu Docker
docker-compose up -d --build
```

### Ce se întâmplă automat:

1. **Docker build** - Se construiește imaginea backend
2. **Volume creation** - Se creează volume pentru persistența datelor
3. **Database initialization** - Se aplică migrările existente
4. **Test data population** - Se adaugă datele de test
5. **Server startup** - Se pornește FastAPI + Vue.js

### Procesul automat în detaliu:

**În `docker-compose.yml` se execută:**
```yaml
command: >
  sh -c "
  mkdir -p /tmp/db &&
  aerich upgrade &&
  python init_db.py &&
  uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
  "
```

**Ce înseamnă fiecare pas:**
1. `mkdir -p /tmp/db` - Creează directorul pentru baza de date
2. `aerich upgrade` - Aplică migrările existente (1 și 2)
3. `python init_db.py` - Populează cu date de test
4. `uvicorn` - Pornește server-ul

### Verificare setup:

```bash
# Verifică log-urile
docker-compose logs backend

# Ar trebui să vezi:
# Successfully connected to database
# Database upgraded to version 2
# Database initialized with test data
# Application started on http://0.0.0.0:5000

# Verifică baza de date
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
print('Tabele create:', [row[0] for row in cursor.fetchall()])
cursor.execute('SELECT COUNT(*) FROM Job')
print('Job-uri create:', cursor.fetchone()[0])
conn.close()
"
```

---

## 🔍 Tabelul Aerich din Baza de Date

**Situația actuală în proiect:**
- ✅ **EXISTĂ tabel `aerich`** - Creat de migrarea 1
- ✅ **EXISTĂ fișiere de migrare** - 1 și 2 sunt deja aplicate
- ✅ `apply_migration.py` menține tabelul `aerich` actualizat

**Rolul tabelului `aerich`:**
- **Version tracking** - Urmărește ce migrări au fost aplicate
- **Migration history** - Stochează istoricul complet al migrărilor
- **Rollback support** - Permite revenirea la versiuni anterioare
- **Conflict prevention** - Previne aplicarea duplicată a migrărilor

**Structura tabelului `aerich`:**
```sql
CREATE TABLE "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL  UNIQUE,
    "app" VARCHAR(100) NOT NULL,
    "content" TEXT NOT NULL
);
```

**Înregistrări actuale (după setup):**
```sql
INSERT INTO "aerich" VALUES
(1, '1_20251103141033_None', 'models', '{}'),
(2, '2_20251103142500_simplify_tables', 'models', '{}');
```

---

## 🔄 Cum Funcționează Migrările Viitoare

### Workflow Complete pentru Modificări de Baze de Date

#### Pasul 1: Modifică Modelele în `db/models.py`

```python
# Exemplu: Adăugăm câmp nou la Persoane
class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True)
    adresa = fields.CharField(max_length=200, null=True)  # <-- CÂMP NOU
    data_nasterii = fields.DateField(null=True)          # <-- ALT CÂMP NOU
```

#### Pasul 2: Generează Migrarea cu Aerich

```bash
# Comanda standard:
docker-compose exec backend aerich migrate --name add_adresa_and_date_to_persoane

# Output:
# Success Create migration 3_20251103150000_add_adresa_and_date_to_persoane.py
```

**Ce se întâmplă în backend:**
1. **Compară modelele Python** cu starea actuală a bazei de date
2. **Detectează diferențele**: adăugarea coloanelor `adresa` și `data_nasterii`
3. **Generează automat SQL-ul**: `ALTER TABLE Persoane ADD COLUMN adresa TEXT NULL;`
4. **Creează fișierul de migrare**: `migrations/models/3_20251103150000_add_adresa_and_date_to_persoane.py`

#### Pasul 3: Verifică Fișierul de Migrare Generat

```python
# migrations/models/3_20251103150000_add_adresa_and_date_to_persoane.py
from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "Persoane" ADD COLUMN "adresa" VARCHAR(200);
        ALTER TABLE "Persoane" ADD COLUMN "data_nasterii" DATE;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- SQLite nu suportă DROP COLUMN simplu
        -- Ar necesita recreere tabelă (vezi migrarea 2 pentru exemplu)
    """
```

#### Pasul 4: Aplică Migrarea

```bash
# Opțiunea A: Aplică manual
docker-compose exec backend aerich upgrade

# Opțiunea B: Repornește containerul (se aplică automat)
docker-compose restart backend
```

#### Pasul 5: Dă Commit la Modificări

```bash
# Adaugă TOATE modificările la git
git add db/models.py                                    # Modelele modificate
git add migrations/models/3_20251103150000_add_*.py     # Migrarea nouă
git commit -m "Add address and birthdate fields to Persoane model"
git push
```

**Important:** NU da commit la fișierele `.db`!

### Exemple Specifice de Modificări

#### Exemplul 1: Adăugare Câmp Simplu
```python
# models.py
class Servicii(Model):
    descriere = fields.CharField(max_length=255)
    pret = fields.DecimalField(max_digits=8, decimal_places=2, null=True)  # NOU
```

```bash
# Generează migrare
docker-compose exec backend aerich migrate --name add_pret_to_servicii
```

#### Exemplul 2: Modificare Constrângere
```python
# models.py
class Servicii(Model):
    descriere = fields.CharField(max_length=255, unique=True)  # ACUM E UNIQUE
```

```bash
# Generează migrare (mai complexă)
docker-compose exec backend aerich migrate --name make_serviciu_unique
```

#### Exemplul 3: Adăugare Relație Nouă
```python
# models.py - Adăugăm categorie la servicii
class CategorieServiciu(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)

class Servicii(Model):
    descriere = fields.CharField(max_length=255)
    categorie = fields.ForeignKeyField('models.CategorieServiciu', null=True)  # NOU
```

```bash
# Generează migrare (complexă - creează 2 tabele noi)
docker-compose exec backend aerich migrate --name add_category_to_servicii
```

### Procesul pentru Colegul Noi

Când un coleg nou face `git pull` după modificările tale:

```bash
# 1. Trage ultimele modificări
git pull origin main

# 2. Docker le aplică automat la restart
docker-compose up -d

# Ce se întâmplă automat:
# - aerich upgrade detectează migrări noi
# - Aplică 3_20251103150000_add_adresa_and_date_to_persoane.py
# - Baza de date e acum la zi cu noile coloane
```

### Comenzi Utile pentru Debugging

```bash
# Vezi ce migrări sunt aplicate
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT version FROM aerich ORDER BY id;')
print('Migrări aplicate:', cursor.fetchall())
conn.close()
"

# Vezi starea actuală a bazei de date
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(Persoane);')
print('Coloane Persoane:', cursor.fetchall())
conn.close()
"

# Forțează aplicarea migrărilor (dacă ceva nu funcționează)
docker-compose exec backend aerich upgrade
```

---

## 🛠️ Comenzi Aerich Utile

### Comenzi de Bază
```bash
# Afișează versiunea curentă a bazei de date
docker-compose exec backend aerich heads

# Afișează istoricul migrărilor
docker-compose exec backend aerich history

# Aplică migrările (se execută automat la docker-compose up)
docker-compose exec backend aerich upgrade

# Revenire la versiunea anterioară (ATENȚIE!)
docker-compose exec backend aerich downgrade
```

### Comenzi de Dezvoltare
```bash
# Generează migrare nouă cu nume specific
docker-compose exec backend aerich migrate --name descriere_modificare

# Creează migrare inițială (doar la setup proiect nou)
docker-compose exec backend aerich init-db

# Verifică status migrări
docker-compose exec backend aerich current

# Listează migrările pending
docker-compose exec backend aerich pending
```

---

## 🚀 Setup pentru un Nou Dezvoltator

### Ce se întâmplă când un nou dev clonează și rulează:

```bash
# 1. Clonează repository-ul
git clone <repository-url>
cd Service

# 2. Pornește Docker
docker-compose up -d
```

**Proces automat:**


1. **Build containers** - Se construiește imagine Docker
2. **Volume creation** - Se creează volume pentru persistența datelor
3. **Database creation** - Se generează fișierul bazei de date în directorul specificat
4. **Migration execution** - Se aplică automat scripturile de migrare existente
5. **Test data insertion** - Se populează baza de date cu informații inițiale
6. **Server launch** - Se pornește serviciile backend și frontend

**Verificare:**
```bash
# Verifică log-urile
docker-compose logs backend

# Ar trebui să vezi:
# Database upgraded to version 1
# Database initialized with test data
# Application started on http://0.0.0.0:5000
```

---

## 🛠️ Comenzi Aerich Utile

### Comenzi de Bază
```bash
# Afișează versiunea curentă a bazei de date
docker-compose exec backend aerich heads

# Afișează istoricul migrărilor
docker-compose exec backend aerich history

# Aplică migrările (se execută automat la docker-compose up)
docker-compose exec backend aerich upgrade

# Revenire la versiunea anterioară
docker-compose exec backend aerich downgrade
```

### Comenzi de Dezvoltare
```bash
# Generează migrare nouă
docker-compose exec backend aerich migrate --name descriere_modificare

# Creează migrare inițială (doar la setup proiect nou)
docker-compose exec backend aerich init-db

# Verifică status migrări
docker-compose exec backend aerich current
```

---

## 🔧 Serviciul Dedicat pentru Migrări

**Proiectul include un serviciu special pentru migrări:**

```yaml
backend-migrate:
  build: ./services/backend
  environment:
    - DATABASE_URL=sqlite:///tmp/db/programari.db
  volumes:
    - ./services/backend:/app
    - backend_db:/tmp/db
  command: >
    sh -c "
    mkdir -p /tmp/db &&
    aerich upgrade
    "
```

**Utilizare:**
```bash
# Rulează migrări fără a porni server-ul
docker-compose run --rm backend-migrate COMMAND=upgrade

# Generează migrare nouă
docker-compose run --rm backend-migrate COMMAND=migrate MIGRATION_NAME=modificare

# Verifică status
docker-compose run --rm backend-migrate COMMAND=heads
```

---

## 📁 Structura Fișierelor de Migrare

### Fișier de Migrare Exemplu
```python
# migrations/models/1_20251103120000_add_adresa_to_persoane.py

from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "Persoane" ADD COLUMN "adresa" VARCHAR(200);
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Nu se poate șterge coloana în SQLite simplu
        -- Ar necesita recreere tabel
    """
```

---

## 🚨 Probleme Comune și Soluții

### ❌ Eroare: "No migrations found"
**Problemă:** Fișierele de migrare lipsesc sau sunt greșit localizate
**Soluție:** Verifică structura directorului `migrations/models/`

### ❌ Eroare: "Database already initialized"
**Problemă:** Încerci să rulezi `init-db` pe o bază de date existentă
**Soluție:** Șterge volume-ul Docker și reconstruiește:
```bash
docker-compose down -v
docker-compose up -d
```

### ❌ Eroare: "Migration failed"
**Problemă:** SQL-ul din migrare are erori
**Soluție:** Verifică fișierul de migrare, corectează SQL-ul

### ❌ Eroare: "Permission denied"
**Problemă:** Permisiuni insuficiente pe fișierele `.db`
**Soluție:** Verifică permisiunile pe volume-ul Docker

---

## 🎯 Best Practices

### 1. **Nu Commit Baza de Date**
```bash
# .gitignore
*.db
*.db-shm
*.db-wal
tmp/db/
```

### 2. **Commit Mereu Migrările**
```bash
# După fiecare modificare de model
git add migrations/models/
git commit -m "Add migration for field X"
```

### 3. **Nume Descriptive pentru Migrări**
```bash
# ❌ Nume greșit
aerich migrate --name update

# ✅ Nume corect
aerich migrate --name add_phone_to_persoane
```

### 4. **Testează Migrările Local**
```bash
# Înainte de commit
docker-compose down -v
docker-compose up -d
# Verifică că totul funcționează
```

### 5. **Documentează Modificările Majore**
- Adaugă notițe în `modificari.md`
- Explică ce s-a schimbat și de ce

---

## 🔄 Workflow Complet pentru Echipă

### 1. **Setup Inițial (O singură dată)**
```bash
# Primul dezvoltator
aerich init -t db.config.TORTOISE_ORM
aerich init-db
git add migrations/
git commit -m "Initial migration setup"
```

### 2. **Dezvoltare Zilnică**
```bash
# Dezvoltatorul A
# Modifică model
docker-compose exec backend aerich migrate --name add_new_field
git add .
git commit -m "Add new feature"
git push

# Dezvoltatorul B
git pull
docker-compose up -d  # Automat aplică migrările noi
```

### 3. **Deploy în Producție**
```bash
# Pe serverul de producție
git pull origin main
docker-compose down
docker-compose up -d --build
# Migrările se aplică automat
```

---

## 📝 Rezumat

**Răspunsuri la întrebările tale:**

1. **✅ Da, tabelele se creează automat** - La `docker-compose up`, `aerich upgrade` aplică toate migrările

2. **✅ Nu trebuie manual `aerich migrate` la setup** - Doar la modificări de modele

3. **✅ `init_db` este separat** - Acesta doar populează cu date de test, nu creează tabelele

4. **✅ Docker-compose se ocupă de tot** - Include comenzile necesare pentru setup automat

**Procesul pentru un nou dezvoltator este simplu:**
```bash
git clone <repo>
cd Service
docker-compose up -d
# GATA! Aplicația funcționează cu baza de date completă
```

**Procesul pentru dezvoltatorul existent:**
```bash
# Modifică model
docker-compose exec backend aerich migrate --name descriere
git add . && git commit && git push
```