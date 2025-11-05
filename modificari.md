# Modificări Structură Bază de Date - Programări System

## 📋 Overview
Documentație detaliată a modificărilor aplicate bazei de date pentru a îmbunătăți structura, performanța și funcționalitățile sistemului de programări. Ghid complet pentru începători cu explicații pas cu pas.

## 💾 Backup Realizat
- **Fișier backup**: `services/backend/db/programari_backup_20251030_102108.db`
- **Data creării**: 2025-10-30
- **Conținut verificat**: 1 programări, 5 job-uri, 5 persoane

---

## 🎯 Pentru Începători - Ce înseamnă aceste modificări?

### Ce este o bază de date?
O bază de date este ca un fișier Excel digital care stochează informații organizate. În cazul nostru, stochează:
- **Job-uri** (ex: Stomatolog, Mecanic)
- **Persoane** (ex: Dr. Popescu, Electrician Ion)
- **Servicii** (ex: Consultație, Revizie)
- **Programări** (când și cui servește)

### De ce am făcut modificări?
Imaginează-ți că ai un registru vechi în care:
- Unele pagini scriu cu majuscule, altele cu litere mici (confuzie)
- Nu poți înregistra că un dentist face mai multe tipuri de servicii (limitare)
- Nu știi când a fost adăugată fiecare informație (lipsă date)

Modificările noastre organizează totul ca într-un registru modern, curat și eficient.

---

## 1. Probleme Identificate în Structura Veche 🚫

### 1.1 Probleme de Naming (Nume incorecte)
**Explicație pentru începători**: În programare, numele trebuie să fie consistente, ca într-un registru unde folosești același stil peste tot.

- **❌ Inconsistență PascalCase vs snake_case**:
  - Unele coloane se numeau `Nume` (cu literă mare)
  - Altele se numeau `nume` (cu literă mică)
  - **Analogie**: Ca și cum ai scrie uneori "CLIENT" și alteori "client" în același registru

- **❌ Greșeală de scriere**: `Descreire` în loc de `descriere`
  - **Efect**: Căutarea după "descriere" nu găsea nimic

### 1.2 Probleme Structurale (Organizare greșită)
**Explicație pentru începători**: Structura e ca organizarea unui cabinet medical - trebuie să fie logică și completă.

- **❌ Relație limitată (1-M în loc de M-M)**:
  - **Problemă**: Un doctor putea fi asociat cu un singur serviciu
  - **Realitate**: Un dentist face extracții, consultații, albiri etc.
  - **Analogie**: Ca și cum un medic ar putea trata doar o boală

- **❌ Lipsă date de creare/modificare**:
  - **Problemă**: Nu știi când a fost adăugat un pacient sau serviciu
  - **Efect**: Imposibil de urmărit istoricul

- **❌ Lipsă date contact directe**:
  - **Problemă**: Email-ul și telefonul erau doar la programări
  - **Efect**: Nu puteai contacta direct un medic

### 1.3 Probleme de Funcționalitate (Nu funcționa corect)
**Explicație pentru începători**: Acestea sunt probleme practice care afectau folosirea zilnică.

- **❌ Programări vechi afișate**:
  - **Problemă**: Programările de ieri apăreau în listă
  - **Efect**: Listă aglomerată, greu de găsit programările relevante

- **❌ Performanță slabă**:
  - **Problemă**: Căutările erau lente
  - **Efect**: Timp de așteptare lung pentru utilizatori

---

## 2. Noua Structură a Bazei de Date

### 2.1 Tabela Job
```sql
CREATE TABLE Job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exemple date:
INSERT INTO Job (nume) VALUES
('Stomatolog'), ('Mecanic Auto'), ('Electrician'), ('Altele'), ('General/Ne-specificat');
```

### 2.2 Tabela Persoane
```sql
CREATE TABLE Persoane (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume VARCHAR(100) NOT NULL,
    prenume VARCHAR(100) NO TNULL,
    email VARCHAR(200) UNIQUE,
    telefon VARCHAR(50),
    job_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE SET NULL
);

-- Index pentru performanță
CREATE INDEX idx_persoane_job_id ON Persoane(job_id);
CREATE INDEX idx_persoane_nume_prenume ON Persoane(nume, prenume);
```

### 2.3 Tabela Servicii
```sql
CREATE TABLE Servicii (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descriere VARCHAR(255) NOT NULL,
    durata_min INTEGER DEFAULT 30,
    pret DECIMAL(10,2),
    job_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE SET NULL
);

-- Corectare: descriere în loc de "Descreire"
CREATE INDEX idx_servicii_job_id ON Servicii(job_id);
```

### 2.4 Tabela PersoanaServiciu (NOU)
```sql
CREATE TABLE PersoanaServiciu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persoana_id INTEGER NOT NULL,
    serviciu_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persoana_id) REFERENCES Persoane(id) ON DELETE CASCADE,
    FOREIGN KEY (serviciu_id) REFERENCES Servicii(id) ON DELETE CASCADE,
    UNIQUE(persoana_id, serviciu_id) -- Previne duplicate
);

-- Relație M-M: O persoană poate oferi mai multe servicii
CREATE INDEX idx_persoanaserviciu_persoana ON PersoanaServiciu(persoana_id);
CREATE INDEX idx_persoanaserviciu_serviciu ON PersoanaServiciu(serviciu_id);
```

### 2.5 Tabela Programari
```sql
CREATE TABLE Programari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persoana_serviciu_id INTEGER,
    data DATE NOT NULL,
    ora TIME NOT NULL,
    observatii TEXT,
    nume_client VARCHAR(100),
    prenume_client VARCHAR(100),
    email_client VARCHAR(200),
    telefon_client VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persoana_serviciu_id) REFERENCES PersoanaServiciu(id) ON DELETE SET NULL
);

-- Index pentru performanță și funcționalitate
CREATE INDEX idx_programari_data ON Programari(data);
CREATE INDEX idx_programari_data_status ON Programari(data, status);
CREATE INDEX idx_programari_persoana_serviciu ON Programari(persoana_serviciu_id);
```

### 2.6 Tabela Users (Păstrat)
```sql
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    role VARCHAR(20) DEFAULT 'user', -- admin, user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Modificări în Cod

### 3.1 Modele Tortoise ORM (`db/models.py`)

**Înainte:**
```python
class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True)
```

**După:**
```python
class Persoane(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    email = fields.CharField(max_length=200, unique=True, null=True)
    telefon = fields.CharField(max_length=50, null=True)
    job = fields.ForeignKeyField('models.Job', related_name='persoane', null=True, on_delete=fields.SET_NULL)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "Persoane"
        indexes = [
            ("job_id",),
            ("nume", "prenume"),
        ]

class PersoanaServiciu(Model):
    id = fields.IntField(pk=True)
    persoana = fields.ForeignKeyField('models.Persoane', related_name='servicii_relation', on_delete=fields.CASCADE)
    serviciu = fields.ForeignKeyField('models.Servicii', related_name='persoane_relation', on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "PersoanaServiciu"
        unique_together = [("persoana", "serviciu")]
        indexes = [
            ("persoana_id",),
            ("serviciu_id",),
        ]

class Programari(Model):
    id = fields.IntField(pk=True)
    persoana_serviciu = fields.ForeignKeyField('models.PersoanaServiciu', related_name='programari', null=True, on_delete=fields.SET_NULL)
    data = fields.DateField()
    ora = fields.TimeField()
    status = fields.CharField(max_length=20, default='pending')
    # ... restul câmpurilor
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

### 3.2 Funcționalitate de Ștergere Automată Programări Depășite

**Implementare în API endpoint:**
```python
from datetime import datetime, date

async def sterge_programari_depasite():
    """Șterge automat programările cu data în trecut"""
    try:
        azi = date.today()
        programari_sterse = await Programari.filter(
            data__lt=azi
        ).delete()

        if programari_sterse > 0:
            print(f"Șterse automat {programari_sterse} programări depășite")

        return programari_sterse
    except Exception as e:
        print(f"Eroare la ștergerea programărilor depășite: {e}")
        return 0

# Apelare în endpoint-ul GET /programari
@app.get("/programari")
async def get_programari():
    # Curățare programări depășite
    await sterge_programari_depasite()

    # Returnare programări curente
    programari = await Programari.all().select_related('persoana_serviciu').values()
    return programari
```

**Cron job (opțional):**
```python
import asyncio
from datetime import time

async def cleanup_task():
    """Task rulat zilnic la miezul nopții"""
    while True:
        now = datetime.now()

        # Așteaptă până la miezul nopții
        midnight = datetime.combine(now.date() + timedelta(days=1), time(0, 0))
        sleep_seconds = (midnight - now).total_seconds()

        await asyncio.sleep(sleep_seconds)

        # Șterge programările depășite
        await sterge_programari_depasite()

# Pornire în background
asyncio.create_task(cleanup_task())
```

---

## 4. Proces de Implementare

### 4.1 Pasul 1: Backup ✅
- Copiat `programari.db` în `programari_backup_20251030_102108.db`
- Verificat integritatea datelor

### 4.2 Pasul 2: Ștergere și Recreare Bază de Date
- Ștergere fișier `programari.db`
- Pornire Docker containers pentru creare automată tabele noi
- Populare cu date de test

### 4.3 Pasul 3: Migrare Date (Opțional)
- Extragere date din backup
- Transformare și inserare în noua structură
- Creare relații PersoanaServiciu

### 4.4 Pasul 4: Actualizare Cod
- Modificare modele Tortoise ORM
- Actualizare Pydantic schemas
- Modificare API endpoints
- Adaptare frontend components

### 4.5 Pasul 5: Testare
- Verificare funcționalități CRUD
- Testare ștergere automată programări
- Validare relații M-M Persoane-Servicii

---

## 5. 🔧 Sistem de Migrări - Explicații pentru Începători

### Ce este un sistem de migrări?
**Explicație simplă**: Un sistem de migrări este ca un jurnal de construcție pentru baza ta de date. Înregistrează fiecare modificare făcută structurii, exact ca un arhitect care păstrează planurile pentru fiecare modificare a unei clădiri.

### De ce este important?
- **📝 Istoric complet**: Știi exact ce s-a schimbat și când
- **🔄 Reversibilitate**: Poți reveni la o versiune anterioară dacă apare o problemă
- **👥 Echipă**: Mai mulți programatori pot lucra sincronizat
- **🚀 Producție**: Aplici modificările fără să pierzi datele existente

### Cum funcționează în proiectul nostru?

#### 🗂️ Structura fișierelor create:
```
migrations/
└── models/
    ├── __init__.py                    # Marchează directorul ca pachet Python
    └── 0_20251030112542_init.py       # Fișierul de migrare inițială
```

#### 📝 Fișierul de migrare explicat:
**Nume**: `0_20251030112542_init.py`
- **`0`** - Numărul versiunii (începem de la 0)
- **`20251030112542`** - Data și ora exactă: 2025-10-30, 11:25:42
- **`init`** - Descrierea migrării (inițializare)

**Conținutul fișierului**:
```python
from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    """Creează toate tabelele noi"""
    return """
        CREATE TABLE IF NOT EXISTS "Job" (...);
        CREATE TABLE IF NOT EXISTS "Persoane" (...);
        CREATE TABLE IF NOT EXISTS "Servicii" (...);
        -- etc.
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    """Șterge toate tabelele (dacă vrem să revenim)"""
    return """
        DROP TABLE IF EXISTS "Programari";
        DROP TABLE IF EXISTS "PersoanaServiciu";
        -- etc.
    """
```

### 🎚️ Comenzi esențiale pentru migrări:

#### **Inițializare (creează prima migrare)**:
```bash
aerich init-db
```
**Ce face**: Creează fișierul `0_..._init.py` cu toate tabelele curente

#### **Creare migrare nouă** (când modifici modelele):
```bash
aerich migrate
```
**Ce face**: Generează un fișier nou `1_..._nume_modificare.py`

#### **Aplicare migrări**:
```bash
aerich upgrade
```
**Ce face**: Aplică toate migrările neaplicate la baza de date

#### **Revenire la versiune anterioară**:
```bash
aerich downgrade
```
**Ce face**: Anulează ultima migrare aplicată

### 🚨 Probleme comune și soluții:

#### **❌ Eroare: "Inited models already"**
**Problemă**: Încerci să inițializezi o bază de date care deja există
**Soluție**: Șterge directorul `migrations/models` și reîncearcă

#### **❌ Eroare: "unable to open database file"**
**Problemă**: Calea către baza de date e greșită
**Soluție**: Verifică fișierul `db/config.py` pentru calea corectă

#### **❌ Eroare: "No module named 'tortoise'"**
**Problemă**: Lipsește pachetul tortoise-orm
**Soluție**: Instalează cu `pip install tortoise-orm`

### 💡 Tips pentru începători:

1. **📦 Backup mereu**: Înainte de migrări, fă mereu backup
2. **🧪 Testează local**: Nu aplica migrări direct în producție
3. **📝 Documentează**: Scrie ce face fiecare migrare
4. **🔄 Verifică**: După migrare, verifică că totul funcționează

---

## 6. Beneficii Noii Structuri 🎉

### 5.1 Flexibilitate
- **M-M Persoane-Servicii**: Un dentist poate oferi mai multe tipuri de servicii
- **Status programări**: Ușor de urmărit starea programărilor
- **Timestamp-uri**: Audit trail complet

### 5.2 Performanță
- **Indecși optimizați**: Query-uri mai rapide
- **Ștergere automată**: Bază de date curată, fără date vechi

### 5.3 Mentenanță
- **Naming consistent**: Toate coloanele snake_case
- **Documentație clară**: Schema explicată detaliat
- **Date valide**: Constraint-uri și validări

---

## 6. Note Importante

### 6.1 Reguli de Ștergere Automată
- **Se șterg**: Programări cu `data < data curentă`
- **Se păstrează**: Programări din aceeași zi chiar dacă ora a trecut
- **Frecvență**: La fiecare acces GET /programari + opțional cron job zilnic

### 6.2 Compatibilitate
- **API backwards compatibility**: Endpoint-urile rămân aceleași
- **Frontend adaptat**: Componentele actualizate pentru noua structură
- **Date migrate**: Toate datele importante păstrate

---

## 7. 🚀 Ghid Complet de Utilizare - Pentru Începători

### Cum pornești sistemul complet?

#### **Pasul 1: Pornește backend-ul (server-ul)**
```bash
cd services/backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 5001
```
**Ce face**: Pornește server-ul API pe portul 5001

#### **Pasul 2: Verifică că funcționează**
Deschide browser-ul și accesează:
- **http://localhost:5001** - Pagina principală
- **http://localhost:5001/docs** - Documentația API (Swagger)

### Cum adaugi date în sistem?

#### **Metoda 1: Prin API (Recomandat)**
```bash
# Adaugă un job nou
curl -X POST http://localhost:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"nume": "Programator"}'

# Adaugă o persoană
curl -X POST http://localhost:5001/persoane \
  -H "Content-Type: application/json" \
  -d '{"nume": "Popescu", "prenume": "Ion", "job_id": 1}'
```

#### **Metoda 2: Direct în baza de date (Avansați)**
```bash
cd services/backend
sqlite3 db/programari.db

INSERT INTO Job (nume) VALUES ('Nutriționist');
INSERT INTO Persoane (nume, prenume, job_id) VALUES ('Ionescu', 'Maria', 1);
```

### Cum funcționează programările?

#### **Adăugare programare**:
```bash
curl -X POST http://localhost:5001/programari \
  -H "Content-Type: application/json" \
  -d '{
    "data": "2025-11-15",
    "ora": "14:30",
    "nume_client": "Client",
    "prenume_client": "Test",
    "email_client": "test@email.com",
    "telefon_client": "+40712345678"
  }'
```

#### **Vizualizare programări**:
```bash
curl http://localhost:5001/programari
```
**Important**: Doar programările din data curentă și viitoare sunt afișate!

### Cum gestionezi migrările viitoare?

#### **Când modifici structura**:
1. **Modifică fișierul** `db/models.py`
2. **Generează migrarea**:
   ```bash
   aerich migrate --name "descriere_modificare"
   ```
3. **Aplică migrarea**:
   ```bash
   aerich upgrade
   ```

#### **Exemplu practic**:
Vrei să adaugi un câmp nou "adresa" la persoane:

1. **Modifici modelul**:
   ```python
   class Persoane(Model):
       # ... câmpuri existente
       adresa = fields.CharField(max_length=200, null=True)  # NOU
   ```

2. **Generezi migrarea**:
   ```bash
   aerich migrate --name "add_adresa_to_persoane"
   ```

3. **Aplici migrarea**:
   ```bash
   aerich upgrade
   ```

### Cum rezolvi probleme comune?

#### **❌ Serverul nu pornește**
**Verifică**:
- Python instalat?
- Dependințe instalate? `pip install -r requirements.txt`
- Port liber? Încearcă alt port

#### **❌ Eroare la conectare baza de date**
**Verifică**:
- Fișierul `db/programari.db` există?
- Permisiuni suficiente?
- Calea corectă în `db/config.py`?

#### **❌ Migrările nu funcționează**
**Verifică**:
- Fișierul `pyproject.toml` conține configurația corectă?
- Directorul `migrations/models` există?

### Tips pentru dezvoltatori începători:

#### **🎯 Best practices**:
1. **Test mereu**: Verifică API-ul după fiecare modificare
2. **Comentariază codul**: Explică ce face fiecare funcție
3. **Folosește nume descriptive**: `nume_client` în loc de `nume1`
4. **Verifică erorile**: Urmărește consola pentru mesaje de eroare

#### **🔍 Instrumente utile**:
- **Postman** sau **Insomnia** pentru testare API
- **DB Browser for SQLite** pentru vizualizarea bazei de date
- **VS Code** cu extensii Python și SQLite

---

## 8. Exemple de Query-uri Noi

### 7.1 Găsire servicii pentru o persoană
```sql
SELECT s.* FROM Servicii s
JOIN PersoanaServiciu ps ON s.id = ps.serviciu_id
WHERE ps.persoana_id = 1;
```

### 7.2 Programări active pentru o persoană
```sql
SELECT p.*, pr.nume, pr.prenume
FROM Programari p
JOIN PersoanaServiciu ps ON p.persoana_serviciu_id = ps.id
JOIN Persoane pr ON ps.persoana_id = pr.id
WHERE p.data >= DATE('now') AND p.status != 'cancelled';
```

### 7.3 Programări depășite de șters
```sql
DELETE FROM Programari
WHERE data < DATE('now');
```

---

**Data implementării:** 2025-10-30
**Status:** În curs de implementare
**Responsabil:** Claude Code Assistant