# 🚀 **Ghid Aerich pentru Începători**

## 📚 **Ce este Aerich?**

**Aerich** este un instrument de migrări pentru bazele de date folosite cu Tortoise ORM (Python). Gândește-te la el ca la un "controlul versiunilor" pentru structura bazei tale de date.

**Analogie:** La fel cum Git urmărește modificările din codul tău, Aerich urmărește modificările din structura bazei de date.

---

## 🏗️ **Cum Funcționează Totul?**

### **Arhitectura Generală**
```
Service/
├── services/backend/
│   ├── db/models.py           # 👈 Aici definești structura (clasele Python)
│   ├── migrations/models/     # 👈 Aici se gen. fișiere SQL automate
│   ├── apply_migration.py     # 👈 Script care aplică migrările
│   └── test_data.py          # 👈 Date de test (opțional)
└── docker-compose.yml        # 👈 Configurare Docker
```

### **Fluxul de Lucru**
```
1. Modifici db/models.py (clase Python)
          ↓
2. Generezi migrare (aerich migrate)
          ↓
3. Se creează fișier SQL automat
          ↓
4. Aplici migrarea (aerich upgrade)
          ↓
5. Baza de date se modifică
```

---

## 📝 **Exemple Concrete de Cod**

### **1. Modelele în Python (`db/models.py`)**

```python
# db/models.py
from tortoise.models import Model
from tortoise import fields

class Job(Model):  # 🏢 Categorii de servicii
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nume

class Persoane(Model):  # 👨‍💼 Persoanele care oferă servicii
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)  # Ex: "Popescu"
    prenume = fields.CharField(max_length=100)  # Ex: "Ion"
    email = fields.CharField(max_length=200, unique=True)
    telefon = fields.CharField(max_length=50, null=True)

    # Relație: fiecare persoană are un job
    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True)

    def __str__(self):
        return f"{self.nume} {self.prenume}"

class Programari(Model):  # 📅 Programările clienților
    id = fields.IntField(pk=True)
    data = fields.DateField()  # Ex: "2025-11-06"
    ora = fields.CharField(max_length=5)  # Ex: "14:30"
    observatii = fields.CharField(max_length=500, null=True)

    # Date client
    nume = fields.CharField(max_length=100, null=True)
    prenume = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=200, null=True)
    telefon = fields.CharField(max_length=50, null=True)

    # Relații
    persoana = fields.ForeignKeyField('models.Persoane', related_name='programari', null=True)
    job = fields.ForeignKeyField('models.Job', related_name='programari', null=True)
    serviciu = fields.ForeignKeyField('models.Servicii', related_name='programari', null=True)
```

### **2. Fișierul de Migrare Generat (`migrations/models/1_20251103141033_None.py`)**

```python
# migrations/models/1_20251103141033_None.py
# 👈 ASTA e generat AUTOMAT - NU edita manual!
from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Job" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "nume" VARCHAR(100) NOT NULL UNIQUE,
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS "Persoane" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "nume" VARCHAR(100) NOT NULL,
            "prenume" VARCHAR(100) NOT NULL,
            "email" VARCHAR(200) UNIQUE,
            "telefon" VARCHAR(50),
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL,
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS "Programari" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "data" DATE NOT NULL,
            "ora" VARCHAR(5) NOT NULL,
            "observatii" VARCHAR(500),
            "nume" VARCHAR(100),
            "prenume" VARCHAR(100),
            "email" VARCHAR(200),
            "telefon" VARCHAR(50),
            "job_id" INT REFERENCES "Job" ("id") ON DELETE SET NULL,
            "persoana_id" INT REFERENCES "Persoane" ("id") ON DELETE SET NULL,
            "serviciu_id" INT REFERENCES "Servicii" ("id") ON DELETE SET NULL,
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        -- Indecși pentru performanță
        CREATE INDEX IF NOT EXISTS "idx_Job_nume_1b66a2" ON "Job" ("nume");
        CREATE INDEX IF NOT EXISTS "idx_Persoane_job_id_58d8bb" ON "Persoane" ("job_id");
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "Programari";
        DROP TABLE IF EXISTS "Persoane";
        DROP TABLE IF EXISTS "Job";
    """
```

### **3. Scriptul de Aplicare (`apply_migration.py`)**

```python
# apply_migration.py
# 👈 ASTA controlează aplicarea migrărilor
import sqlite3
import os
import glob

def apply_migration():
    """Aplică migrările dacă nu sunt deja aplicate"""

    # 1. Creează directorul pentru baza de date
    os.makedirs('/tmp/db', exist_ok=True)

    # 2. Conectare la baza de date SQLite
    conn = sqlite3.connect('/tmp/db/programari.db')
    cursor = conn.cursor()

    # 3. Creează tabela aerich (pentru tracking migrări)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "aerich" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "version" VARCHAR(255) NOT NULL,
            "app" VARCHAR(100) NOT NULL,
            "content" TEXT NOT NULL
        )
    """)

    # 4. Caută toate fișierele de migrări
    migration_files = sorted(glob.glob('/app/migrations/models/*.py'))

    for migration_file in migration_files:
        filename = migration_file.split('/')[-1]
        version = filename.replace('.py', '')

        # 5. Verifică dacă migrarea e deja aplicată
        cursor.execute("SELECT version FROM aerich WHERE version = ?", (version,))
        if cursor.fetchone():
            print(f"✅ Migration {version} deja aplicată, sar...")
            continue

        print(f"🔄 Applying migration: {version}")

        # 6. Citeste și extrage SQL-ul din fișierul de migrare
        with open(migration_file, 'r') as f:
            content = f.read()

        # Extrage SQL-ul din funcția upgrade
        start_idx = content.find('"""', content.find('async def upgrade'))
        start_idx += 3
        end_idx = content.find('"""', start_idx)
        sql = content[start_idx:end_idx]

        # 7. Execută SQL-ul
        try:
            cursor.executescript(sql)
            conn.commit()
            print(f"✅ Migration {version} aplicată cu succes!")

            # 8. Înregistrează migrarea în tabela aerich
            cursor.execute("""
                INSERT INTO aerich (version, app, content)
                VALUES (?, 'models', '{}')
            """, (version,))
            conn.commit()

        except Exception as e:
            print(f"❌ Eroare la aplicarea migration {version}: {e}")
            return False

    conn.close()
    return True

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
```

### **4. Configurare Docker (`docker-compose.yml`)**

```yaml
# docker-compose.yml
services:
  backend:
    build: ./services/backend
    ports:
      - 5000:5000
    environment:
      - DATABASE_URL=sqlite:///tmp/db/programari.db
    volumes:
      - ./services/backend:/app
      - backend_db:/tmp/db  # 👈 Volume pentru a păstra baza de date
    command: >
      sh -c "
      mkdir -p /tmp/db &&           # 👈 Creează directorul BD
      python apply_migration.py &&  # 👈 Aplică migrările
      python test_data.py &&        # 👈 Adaugă date de test
      uvicorn src.main:app --reload --host 0.0.0.0 --port 5000  # 👈 Pornește server
      "

volumes:
  backend_db:  # 👈 Aici se salvează fișierul .db
    driver: local
```

---

## 🎯 **Scenarii Practice pentru Începători**

### **Scenariul 1: Ești nou și vrei să rulezi proiectul**

**Pași simpli:**
```bash
# 1. Clonează proiectul
git clone <url-proiect>
cd Service

# 2. Pornește Docker (TOTUL SE FACE AUTOMAT!)
docker-compose up -d

# 3. Așteaptă 1-2 minute... și gata! 🎉
# Poți accesa http://localhost:8080
```

**Ce se întâmplă în spate?**
1. Docker builduiește imaginile
2. Se creează baza de date în `/tmp/db/programari.db`
3. `apply_migration.py` aplică migrările:
   - Creează tabela `aerich` (tracking)
   - Creează tabelele: `Job`, `Persoane`, `Programari`, etc.
   - Înregistrează migrările aplicate
4. `test_data.py` adaugă date de test
5. Serverul FastAPI pornește pe port 5000

### **Scenariul 2: Vrei să adaugi un câmp nou**

**Exemplu: Vrei să adaugi câmpul "adresă" la Persoane**

**Pasul 1: Modifică modelul**
```python
# db/models.py
class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    email = fields.CharField(max_length=200, unique=True)
    telefon = fields.CharField(max_length=50, null=True)

    # 👈 ADAUGĂ CÂMP NOU:
    adresa = fields.CharField(max_length=200, null=True)  # NOU!

    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True)
```

**Pasul 2: Generează migrare**
```bash
docker-compose exec backend aerich migrate --name add_adresa_to_persoane
# Output: ✅ Migration 3_20251105143000_add_adresa_to_persoane.py created
```

**Pasul 3: Aplică migrarea**
```bash
docker-compose exec backend aerich upgrade
# Output: ✅ Migration applied successfully
```

**Ce s-a întâmplat?**
- S-a creat fișier: `migrations/models/3_20251105143000_add_adresa_to_persoane.py`
- Conține SQL: `ALTER TABLE "Persoane" ADD COLUMN "adresa" VARCHAR(200);`
- Baza de date are acum câmpul `adresa`

### **Scenariul 3: Vrei să vezi ce migrări sunt aplicate**

```bash
# Vezi migrările aplicate
docker-compose exec backend aerich heads

# Vezi istoricul complet
docker-compose exec backend aerich history

# Verifică direct în baza de date
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM aerich ORDER BY id;')
print('📋 Migrări aplicate:')
for row in cursor.fetchall():
    print(f'  ✅ {row[1]} - {row[2]}')
conn.close()
"
```

---

## 🔧 **Comenzi Utile**

### **Comenzi de Bază Aerich**
```bash
# Generează migrare nouă
docker-compose exec backend aerich migrate --name descriere_scurta

# Aplică migrări neaplicate
docker-compose exec backend aerich upgrade

# Revenire la versiune anterioară (ATENȚIE!)
docker-compose exec backend aerich downgrade

# Vezi status migrări
docker-compose exec backend aerich heads

# Vezi istoric complet
docker-compose exec backend aerich history
```

### **Comenzi de Verificare**
```bash
# Verifică tabelele create
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = [row[0] for row in cursor.fetchall()]
print('📊 Tabele în baza de date:', tables)
conn.close()
"

# Verifică structura unei tabele
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/tmp/db/programari.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(Persoane);')
print('📋 Structura tabelului Persoane:')
for row in cursor.fetchall():
    print(f'  {row[1]} - {row[2]}')
conn.close()
"
```

---

## ⚠️ **Probleme Comune și Soluții**

### **Problema 1: "No upgrade items found"**
```bash
# Semn: Migrările par aplicate dar tabelele nu există
# Cauză: Tabela aerish spune că e ok dar BD e goală

# Soluție: Reset complet
docker-compose down -v  # Șterge volumele (baza de date)
docker-compose up -d    # Rebuild și aplică migrările din nou
```

### **Problema 2: "Table already exists"**
```bash
# Semn: Încearcă să creeze tabele care deja există
# Soluție: Scriptul apply_migration.py e idempotent - nu face nimic
# Dacă tot dă eroare, verifică if NOT EXISTS în SQL
```

### **Problema 3: Modifici modelul dar nu generezi migrare**
```bash
# ❌ GREȘIT: Modifici db/models.py și speri că "merge magic"
# ✅ CORECT: Modifici → Generezi migrare → Aplici migrare

# Flow corect:
# 1. Editezi db/models.py
# 2. docker-compose exec backend aerich migrate --name descriere
# 3. docker-compose exec backend aerich upgrade
```

---

## 🎓 **Concepte Cheie pentru Începători**

### **1. Idempotență**
**Ce înseamnă:** Poți rula scriptul de mai multe ori fără efecte secundare
```python
# Exemplu: CREATE TABLE IF NOT EXISTS (nu doar CREATE TABLE)
# Dacă tabela există, nu face nimic - nu dă eroare
```

### **2. ForeignKey**
**Ce înseamnă:** Legătură între tabele
```python
# Persoane.job_id se leagă de Job.id
# Dacă ștergi un Job, Persoane.job_id devine NULL
job = fields.ForeignKeyField('models.Job', on_delete=fields.SET_NULL)
```

### **3. Migration Version**
**Format:** `numar_data_nume_descriptiv`
- `numar`: Ordine (1, 2, 3...)
- `data`: Timestamp (20251105143000)
- `nume`: Nume scurt descriptiv

**Exemplu:** `3_20251105143000_add_adresa_to_persoane.py`

---

## 📋 **Checklist pentru Începători**

### **✅ Setup Inițial**
- [ ] Clonat proiectul
- [ ] Verificat `docker-compose.yml`
- [ ] Rulat `docker-compose up -d`
- [ ] Așteptat 2-3 minute
- [ ] Accesat http://localhost:8080

### **✅ Modificări Schema**
- [ ] Modificat `db/models.py`
- [ ] Generat migrare: `aerich migrate --name descriere`
- [ ] Verificat fișier generat în `migrations/models/`
- [ ] Aplicat migrare: `aerich upgrade`
- [ ] Testat că API-ul funcționează

### **✅ Debugging**
- [ ] Verificat log-urile: `docker-compose logs backend`
- [ ] Verificat migrări: `aerich heads`
- [ ] Verificat tabele: `sqlite3 /tmp/db/programari.db`

---

## 🚀 **Pro Tip-uri**

### **Tip 1: Verifică mereu migrarea generată**
```bash
# După ce generezi migrare, uită-te în fișierul creat
cat migrations/models/3_*.py
# Asigură-te că SQL-ul arată corect
```

### **Tip 2: Nume descriptive pentru migrări**
```bash
# ❌ RU: aerich migrate --name test
# ✅ BUN: aerich migrate --name add_phone_to_users
# ✅ BUN: aerich migrate --name create_appointments_table
```

### **Tip 3: Testează migrările local**
```bash
# Înainte de commit, testează pe baza de date goală
docker-compose down -v
docker-compose up -d
# Verifică că totul merge ok
```

---

## 📚 **Resurse Utile**

### **Documentație Oficială**
- [Tortoise ORM](https://tortoise.github.io/)
- [Aerich](https://github.com/tortoise/aerich)

### **Fișiere Importante în Proiect**
- `CLAUDE.md` - Arhitectura generală
- `AERICH_WORKFLOW.md` - Workflow avansat
- `db/models.py` - Modelele curente
- `apply_migration.py` - Script aplicare

---

**🎉 Felicitări! Acum înțelegi cum funcționează sistemul de migrări Aerich!**

**Ideea principală:** Modifici clasele Python → Generezi migrare → Aplici migrare. Asta asigură că toți dezvoltatorii au aceeași structură a bazei de date!