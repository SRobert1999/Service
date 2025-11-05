# Update Documentation - Sistem Programări

## Modificări Bază de Date

### Structura Actuală a Tabelelor

#### 1. Users
- `id` (PK, Int)
- `username` (VarChar(50), Unique)
- `password` (VarChar(200))
- `email` (VarChar(200), Unique)
- `created_at` (DateTime)
- `modified_at` (DateTime)

#### 2. Job2
- `id` (PK, Int)
- `nume` (VarChar(100), Unique)

#### 3. Persoane (Modificat)
- `id` (PK, Int)
- `nume` (VarChar(100))
- `prenume` (VarChar(100))
- `job` (ForeignKey → Job.id, SET_NULL) **NOU**

#### 4. Servicii (Modificat)
- `id` (PK, Int)
- `descriere` (VarChar(255))
- `job` (ForeignKey → Job.id, SET_NULL) **NOU**

#### 5. Programari (Modificat)
- `id` (PK, Int)
- `persoana` (ForeignKey → Persoane.id, CASCADE)
- `serviciu` (ForeignKey → Servicii.id, CASCADE)
- `data` (VarChar(50), Nullable)
- `ora` (VarChar(10), Nullable)
- `observatii` (Text, Nullable)
- `nume` (VarChar(100), Nullable)
- `prenume` (VarChar(100), Nullable)
- `email` (VarChar(200), Nullable)
- `telefon` (VarChar(50), Nullable)

## Noi Foreign Keys Adăugate

### 1. Persoane.job → Job.id
- **Tip**: ForeignKeyField cu SET_NULL on_delete
- **Scop**: Asociază fiecare persoană cu o categorie de servicii (job)
- **Comportament**: Dacă un job se șterge, persoanele rămân dar job_id devine NULL

### 2. Servicii.job → Job.id
- **Tip**: ForeignKeyField cu SET_NULL on_delete
- **Scop**: Asociază fiecare serviciu cu o categorie de servicii (job)
- **Comportament**: Dacă un job se șterge, serviciile rămân dar job_id devine NULL

## Impact în Frontend

### Flux Navigare Actualizat
```
HomeView (/)
  → SelectJobView (/select-job)
    → ProgramariView (/programari?job_id=X&job_name=Y)
```

### Componente Afectate

#### 1. SelectJobView.vue (NOU)
- **Funcționalitate**: Afișează toate categoriile (Job) disponibile
- **Interacțiune**: Utilizatorul selectează o categorie
- **Navigare**: Redirecționează către `/programari` cu `job_id` și `job_name` în query params

#### 2. ProgramariView.vue (Modificat)
- **Modificare**: Primește `job_id` și `job_name` din query params
- **Filtrare**: Încarcă persoane și servicii filtrate după `job_id`
- **API Calls**:
  - `/persoane?job_id=${this.selectedJobId}`
  - `/servicii?job_id=${this.selectedJobId}`

#### 3. ProgramariTable.vue (Modificat)
- **Modificare**: Folosește `job_id` din route query pentru filtrare
- **Consistență**: Afișează doar programările relevante pentru categoria selectată

## Teorie - Conexiuni Frontend-Backend

### 1. Arhitectura de Date
```
Frontend (Vue.js)
  ↔ API Calls (Axios)
    ↔ Backend (FastAPI)
      ↔ Tortoise ORM
        ↔ SQLite Database
```

### 2. Flux de Filtrare
```
SelectJobView: GET /jobs → Afișează categorii
          ↓ Utilizator selectează job
ProgramariView: GET /persoane?job_id=X + GET /servicii?job_id=X
          ↓ Utilizator completează formular
          POST /programari → Creează programare
```

### 3. Mapare Relații Database ↔ Frontend

#### Relația Job → Persoane/Servicii
**Backend:**
```python
# models.py
class Persoane(Model):
    job = fields.ForeignKeyField('models.Job', related_name='persoane')

# main.py
@app.get("/persoane")
async def get_persoane(job_id: Optional[int] = None):
    if job_id is not None:
        persoane = await Persoane.filter(job_id=job_id).values()
```

**Frontend:**
```javascript
// ProgramariView.vue
async loadData() {
  const persoaneUrl = this.selectedJobId ?
    `/persoane?job_id=${this.selectedJobId}` : '/persoane';
  const response = await axios.get(persoaneUrl);
  this.persoane = response.data;
}
```

#### Relația Persoane/Servicii → Programari
**Backend:**
```python
# models.py
class Programari(Model):
    persoana = fields.ForeignKeyField('models.Persoane', related_name='programari')
    serviciu = fields.ForeignKeyField('models.Servicii', related_name='programari')

# main.py
@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    programare_data = {
      "persoana_id": prog.persoana_id,
      "serviciu_id": prog.serviciu_id,
      # ... alte câmpuri
    }
    p = await Programari.create(**programare_data)
```

**Frontend:**
```javascript
// ProgramariView.vue
<select v-model.number="newProgramare.persoana_id">
  <option v-for="p in persoane" :key="p.id" :value="p.id">
    {{ p.nume }} {{ p.prenume }}
  </option>
</select>

// ProgramariTable.vue - Afișare nume în loc de ID
this.persoaneMap[p.id] = `${p.nume} ${p.prenume}`;
// Template: {{ persoaneMap[p.persoana_id] || 'N/A' }}
```

### 4. Query Parameters în Vue Router

#### Transmitere Job ID între componente
```javascript
// SelectJobView.vue
selectJob(job) {
  this.$router.push({
    name: 'programari',
    query: { job_id: job.id, job_name: job.nume }
  });
}

// ProgramariView.vue
async mounted() {
  const { job_id, job_name } = this.$route.query;
  if (job_id) {
    this.selectedJobId = parseInt(job_id);
    this.selectedJobName = job_name || 'Categoria selectată';
  }
  await this.loadData();
}
```

### 5. Validare Dual-layer

#### Backend (Pydantic + Tortoise)
```python
# main.py - Validare input
@validator('telefon')
def validate_telefon(cls, v):
    if v and not re.match(r'^(\+4|0)[0-9]{9}$', v):
        raise ValueError('Telefon invalid')
    return v

# models.py - Validare database
telefon = fields.CharField(max_length=50, null=True)
```

#### Frontend (HTML5 + JavaScript)
```html
<input v-model="newProgramare.telefon"
       placeholder="Telefon"
       pattern="^(\+4|0)[0-9]{9}$" />
```

### 6. Stare Consistentă între Componente

#### Props și Events
```javascript
// ProgramariView.vue
<ProgramariTable :refresh="refreshTable" />

// ProgramariTable.vue
props: {
  refresh: Boolean
},
watch: {
  refresh() {
    this.fetchProgramari();
  }
}
```

#### Dependency Injection
```javascript
// ProgramariView.vue & ProgramariTable.vue
inject: ['showMessage'],

// Apel
this.showMessage({
  text: "Programare adăugată cu succes!",
  type: "success"
});
```

## Beneficiile Arhitecturii Actuale

1. **Separare Responsabilități**: Frontend doar afișează, backend gestionează logica
2. **Scalabilitate**: Ușor de adăugat noi categorii de servicii
3. **Consistență Date**: ForeignKey relationships asigură integritate
4. **Flexibilitate**: SET_NULL permite ștergerea categoriilor fără a pierde date
5. **Validare Robustă**: Dublă validare previne date invalide
6. **UX Fluid**: Navigare logică cu starea păstrată între pagini