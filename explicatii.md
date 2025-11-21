# 📚 Explicații Detaliate - Sistem Programări Plan V2

## Cuprins
1. [Flow de Selecție Persoană](#1-flow-de-selectie-persoana)
2. [V-Calendar cu Disponibilitate](#2-v-calendar-cu-disponibilitate)
3. [Concepte Vue.js Folosite](#3-concepte-vuejs-folosite)
4. [Diagrame de Flow](#4-diagrame-de-flow)

---

## 1. Flow de Selecție Persoană

### 🎯 Scopul
Utilizatorul selectează **mai întâi persoana** (ex: Dr. Popescu Ion) și **apoi** completează formularul de programare. Acest flow asigură că vezi disponibilitatea exactă a persoanei respective.

---

### 📊 Variabile de Stare

#### **În `data()`:**

```javascript
data() {
  return {
    // ETAPA 1: Jobs
    jobs: [],              // Lista joburilor de la backend: [{ id: 1, nume: 'Stomatolog' }, ...]
    selectedJob: null,     // Jobul selectat (obiect complet): { id: 1, nume: 'Stomatolog' }
    selectedJobId: null,   // ID-ul jobului selectat: 1
    loading: true,         // Dacă se încarcă joburile (true/false)
    
    // ETAPA 2: Persoane
    persoane: [],          // Lista persoanelor pentru job: [{ id: 1, nume: 'Popescu', prenume: 'Ion' }, ...]
    selectedPersoana: null, // Persoana selectată (obiect complet): { id: 1, nume: 'Popescu', prenume: 'Ion' }
    loadingPersoane: false, // Dacă se încarcă persoanele (true/false)
  }
}
```

**Cum funcționează aceste variabile:**

| Variabilă | Valoare Inițială | După ce selectezi "Stomatolog" | După ce selectezi "Dr. Popescu Ion" |
|-----------|------------------|--------------------------------|-------------------------------------|
| `selectedJob` | `null` | `{ id: 1, nume: 'Stomatolog' }` | `{ id: 1, nume: 'Stomatolog' }` |
| `selectedJobId` | `null` | `1` | `1` |
| `selectedPersoana` | `null` | `null` | `{ id: 1, nume: 'Popescu', prenume: 'Ion' }` |
| `persoane` | `[]` | `[{ id: 1, ... }, { id: 2, ... }]` | `[{ id: 1, ... }, { id: 2, ... }]` |

---

### 🔄 Flow Pas cu Pas

#### **PAS 1: Încărcare Inițială**

**Când:** La deschiderea paginii

**Ce se întâmplă:**

```javascript
async mounted() {
  await this.loadJobs();
}
```

1. Vue.js apelează automat `mounted()` când componenta e gata
2. Se apelează `loadJobs()` care face `axios.get('/jobs')`
3. Backend returnează: `[{ id: 1, nume: 'Stomatolog' }, { id: 2, nume: 'Mecanic Auto' }]`
4. Se salvează în `this.jobs = [...date...]`
5. Se setează `this.loading = false`

**În template:**

```vue
<div v-if="loading" class="loading">
  Se încarcă categoriile...
</div>

<div v-else class="jobs-grid">
  <div v-for="job in jobs" :key="job.id" @click="selectJob(job)">
    <h3>{{ job.nume }}</h3>
  </div>
</div>
```

- Dacă `loading = true` → afișează "Se încarcă..."
- Dacă `loading = false` → afișează grid-ul cu joburi
- `v-for="job in jobs"` → creează un card pentru fiecare job
- `@click="selectJob(job)"` → când dai click, apelează funcția `selectJob()` cu jobul ca parametru

---

#### **PAS 2: Selectare Job**

**Când:** User click pe "Stomatolog"

**Ce se întâmplă:**

```javascript
selectJob(job) {
  // job = { id: 1, nume: 'Stomatolog' }
  
  this.selectedJob = job;           // Salvează jobul complet
  this.selectedJobId = job.id;      // Salvează doar ID-ul (pentru filtrare)
  this.selectedPersoana = null;     // Resetează persoana (dacă ai avut alta selectată)
  this.loadPersoane();              // Încarcă persoanele pentru acest job
}
```

**Linie cu linie:**

1. `this.selectedJob = job;`
   - Salvează obiectul complet: `{ id: 1, nume: 'Stomatolog' }`
   - **De ce?** Ca să afișăm numele job-ului în titlu: "Selectați persoana pentru **Stomatolog**"

2. `this.selectedJobId = job.id;`
   - Salvează doar ID-ul: `1`
   - **De ce?** Pentru filtrare în API: `/persoane?job_id=1`

3. `this.selectedPersoana = null;`
   - Resetează persoana la `null`
   - **De ce?** Dacă user schimbă job-ul, trebuie să selecteze din nou o persoană

4. `this.loadPersoane();`
   - Apelează funcția care încarcă persoanele

**În template, ce se întâmplă:**

```vue
<!-- ETAPA 1: Jobs grid -->
<div v-else class="jobs-grid">
  <!-- Acest div are acum clasa 'job-card-active' dacă selectedJobId === job.id -->
  <div :class="{ 'job-card-active': selectedJobId === job.id }">
    <h3>{{ job.nume }}</h3>
  </div>
</div>

<!-- ETAPA 2: Persoane -->
<div v-if="selectedJob && !selectedPersoana" class="persoane-section">
  <h2>Selectați persoana pentru {{ selectedJob.nume }}</h2>
  <!-- Acum afișează: "Selectați persoana pentru Stomatolog" -->
</div>
```

**Condiția `v-if="selectedJob && !selectedPersoana"`:**

| `selectedJob` | `selectedPersoana` | Rezultat | Explicație |
|---------------|-------------------|----------|------------|
| `null` | `null` | ❌ **NU afișa** | Nu ai selectat job-ul |
| `{ id: 1, ... }` | `null` | ✅ **AFIȘEAZĂ** | Ai selectat job-ul, trebuie să selectezi persoana |
| `{ id: 1, ... }` | `{ id: 1, ... }` | ❌ **NU afișa** | Ai selectat și persoana, mergi la formular |

---

#### **PAS 3: Încărcare Persoane**

**Ce se întâmplă:**

```javascript
async loadPersoane() {
  this.loadingPersoane = true;  // Setează flag de loading
  
  try {
    // Construiește URL cu filtrul: /persoane?job_id=1
    const url = `/persoane?job_id=${this.selectedJobId}`;
    
    // Face cerere la backend
    const response = await axios.get(url);
    
    // Salvează rezultatul: [{ id: 1, nume: 'Popescu', prenume: 'Ion' }, ...]
    this.persoane = response.data;
    
    console.log(`Loaded ${this.persoane.length} persoane for job_id:`, this.selectedJobId);
  } catch (error) {
    console.error('Error loading persoane:', error);
    this.showMessage({
      text: 'Eroare la încărcarea persoanelor!',
      type: 'error'
    });
  } finally {
    this.loadingPersoane = false;  // Șterge flag de loading (indiferent de succes/eroare)
  }
}
```

**Pas cu pas:**

1. **`this.loadingPersoane = true;`**
   - Setează flag de loading
   - Template-ul afișează "Se încarcă persoanele..."

2. **`const url = `/persoane?job_id=${this.selectedJobId}`;`**
   - Construiește URL: `/persoane?job_id=1`
   - **Template literal:** `${this.selectedJobId}` = valoarea lui `selectedJobId` (1)

3. **`const response = await axios.get(url);`**
   - Face cerere HTTP GET la backend
   - `await` = așteaptă răspunsul (funcția e asincronă)
   - Backend răspunde cu: `[{ id: 1, nume: 'Popescu', prenume: 'Ion' }, { id: 2, nume: 'Ionescu', prenume: 'Maria' }]`

4. **`this.persoane = response.data;`**
   - Salvează persoanele în `this.persoane`
   - Vue.js detectează automat schimbarea și actualizează UI-ul

5. **`finally { this.loadingPersoane = false; }`**
   - Se execută mereu (succes SAU eroare)
   - Șterge loading-ul

**În template:**

```vue
<div v-if="loadingPersoane" class="loading">
  Se încarcă persoanele...
</div>

<div v-else class="persoane-grid">
  <div v-for="persoana in persoane" :key="persoana.id" @click="selectPersoana(persoana)">
    <h3>{{ persoana.nume }} {{ persoana.prenume }}</h3>
    <button>Selectează</button>
  </div>
</div>
```

- Dacă `loadingPersoane = true` → afișează "Se încarcă..."
- Dacă `loadingPersoane = false` → afișează grid-ul cu persoane
- `v-for="persoana in persoane"` → creează un card pentru fiecare persoană
- `@click="selectPersoana(persoana)"` → când dai click, apelează funcția cu persoana

---

#### **PAS 4: Selectare Persoană**

**Când:** User click pe "Dr. Popescu Ion"

**Ce se întâmplă:**

```javascript
selectPersoana(persoana) {
  // persoana = { id: 1, nume: 'Popescu', prenume: 'Ion' }
  
  this.selectedPersoana = persoana;              // Salvează persoana selectată
  this.newProgramare.persoana_id = persoana.id;  // Setează ID-ul în formular
  this.loadServicii();                           // Încarcă serviciile pentru job
  this.loadProgramari();                         // Încarcă programările pentru calendar
  this.refreshTable = !this.refreshTable;        // Refresh tabel
}
```

**Linie cu linie:**

1. **`this.selectedPersoana = persoana;`**
   - Salvează obiectul complet: `{ id: 1, nume: 'Popescu', prenume: 'Ion' }`
   - **De ce?** Ca să afișăm numele în titlu: "Programare pentru **Dr. Popescu Ion**"

2. **`this.newProgramare.persoana_id = persoana.id;`**
   - Setează ID-ul persoanei în obiectul formularului
   - **De ce?** Când trimiți programarea, backend-ul trebuie să știe pentru cine e

3. **`this.loadServicii();`**
   - Încarcă serviciile pentru job-ul selectat
   - Exemplu: Pentru "Stomatolog" → ["Consultație", "Detartraj", etc.]

4. **`this.loadProgramari();`**
   - Încarcă programările existente ale persoanei
   - **De ce?** Pentru calendar - să știm ce zile sunt ocupate

5. **`this.refreshTable = !this.refreshTable;`**
   - Inversează valoarea (true → false sau false → true)
   - **De ce?** Trigger pentru componenta `ProgramariTable` să se reîncarce

**În template, ce se întâmplă:**

```vue
<!-- ETAPA 2 dispare (selectedJob = true, selectedPersoana = true) -->

<!-- ETAPA 3 apare -->
<div v-if="selectedPersoana" class="content-section">
  <h2>
    Programare pentru {{ selectedPersoana.nume }} {{ selectedPersoana.prenume }}
    <span>({{ selectedJob.nume }})</span>
  </h2>
  <!-- Afișează: "Programare pentru Popescu Ion (Stomatolog)" -->
  
  <button @click="backToPersoane">Schimbă persoana</button>
  
  <!-- Formular + Calendar + Tabel -->
</div>
```

**Condiția `v-if="selectedPersoana"`:**

- Dacă `selectedPersoana = null` → ❌ **NU afișa** formularul
- Dacă `selectedPersoana = { ... }` → ✅ **AFIȘEAZĂ** formularul

---

#### **PAS 5: Butoane de Navigare**

**Butonul "Înapoi la categorii":**

```javascript
backToJobs() {
  this.selectedJob = null;       // Resetează job-ul
  this.selectedJobId = null;     // Resetează ID-ul job-ului
  this.selectedPersoana = null;  // Resetează persoana
  this.persoane = [];            // Golește lista de persoane
  this.resetForm();              // Resetează formularul
}
```

**Rezultat:**
- Revii la **ETAPA 1** (grid jobs)
- Toate secțiunile ulterioare dispar

**Butonul "Schimbă persoana":**

```javascript
backToPersoane() {
  this.selectedPersoana = null;     // Resetează persoana
  this.programariExistente = [];    // Golește programările (pentru calendar)
  this.resetForm();                 // Resetează formularul
}
```

**Rezultat:**
- Revii la **ETAPA 2** (grid persoane)
- Formularul dispare
- Job-ul rămâne selectat (nu trebuie să selectezi din nou)

---

### 🔗 Cum Se Conectează Toate

```
┌─────────────────────────────────────────────────────────────┐
│                    STAREA COMPONENTEI                        │
├─────────────────────────────────────────────────────────────┤
│ selectedJob = null                                           │
│ selectedJobId = null                                         │
│ selectedPersoana = null                                      │
│ persoane = []                                                │
└─────────────────────────────────────────────────────────────┘
                             ↓
                    [User click "Stomatolog"]
                             ↓
                      selectJob(job)
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ selectedJob = { id: 1, nume: 'Stomatolog' }                 │
│ selectedJobId = 1                                            │
│ selectedPersoana = null (resetat)                            │
│ persoane = [] (se încarcă...)                                │
└─────────────────────────────────────────────────────────────┘
                             ↓
                      loadPersoane()
                             ↓
              axios.get('/persoane?job_id=1')
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ persoane = [                                                 │
│   { id: 1, nume: 'Popescu', prenume: 'Ion' },              │
│   { id: 2, nume: 'Ionescu', prenume: 'Maria' }             │
│ ]                                                            │
└─────────────────────────────────────────────────────────────┘
                             ↓
              [User click "Dr. Popescu Ion"]
                             ↓
                  selectPersoana(persoana)
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ selectedPersoana = { id: 1, nume: 'Popescu', prenume: 'Ion' }│
│ newProgramare.persoana_id = 1                                │
└─────────────────────────────────────────────────────────────┘
                             ↓
            loadServicii() + loadProgramari()
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ servicii = [                                                 │
│   { id: 1, descriere: 'Consultație' },                     │
│   { id: 2, descriere: 'Detartraj' }                        │
│ ]                                                            │
│ programariExistente = [                                      │
│   { data: '2025-11-20', ora: '09:00' },                    │
│   { data: '2025-11-21', ora: '10:00' }                     │
│ ]                                                            │
└─────────────────────────────────────────────────────────────┘
                             ↓
                    FORMULAR GATA!
```

---

### 🎨 Cum Funcționează Afișarea Condițională

**Template-ul folosește 3 secțiuni cu condiții:**

```vue
<!-- ETAPA 1: Mereu vizibilă -->
<div class="jobs-grid">
  <!-- Jobs -->
</div>

<!-- ETAPA 2: Vizibilă DOAR dacă ai selectat job dar NU persoană -->
<div v-if="selectedJob && !selectedPersoana">
  <!-- Persoane -->
</div>

<!-- ETAPA 3: Vizibilă DOAR dacă ai selectat persoană -->
<div v-if="selectedPersoana">
  <!-- Formular + Calendar -->
</div>
```

**Tabel de Vizibilitate:**

| `selectedJob` | `selectedPersoana` | ETAPA 1 | ETAPA 2 | ETAPA 3 |
|---------------|-------------------|---------|---------|---------|
| `null` | `null` | ✅ | ❌ | ❌ |
| `{ ... }` | `null` | ✅ | ✅ | ❌ |
| `{ ... }` | `{ ... }` | ✅ | ❌ | ✅ |

---

## 2. V-Calendar cu Disponibilitate

### 🎯 Scopul
Calendarul arată utilizatorului care zile sunt disponibile, parțial ocupate sau complet ocupate, și blochează zilele care nu mai pot fi rezervate.

---

### 📊 Variabile de Stare pentru Calendar

```javascript
data() {
  return {
    programariExistente: [],     // Programările existente ale persoanei: [{ data: '2025-11-20', ora: '09:00' }, ...]
    loadingProgramari: false,    // Dacă se încarcă programările
    capacitateMaxima: 8,         // Câte programări maxime pe zi (8 ore = 8 programări)
    
    newProgramare: {
      data: null,                // Data selectată în calendar (Date object)
      // ... alte câmpuri
    }
  }
}
```

---

### 🔄 Flow Pas cu Pas

#### **PAS 1: Încărcare Programări**

**Când:** După ce selectezi o persoană

**Ce se întâmplă:**

```javascript
async loadProgramari() {
  if (!this.selectedPersoana) return;  // Nu încarcă dacă nu e selectată o persoană
  
  this.loadingProgramari = true;
  
  try {
    // Cerere la backend cu filtru după persoană
    const url = `/programari?persoana_id=${this.selectedPersoana.id}`;
    const response = await axios.get(url);
    
    // Salvează programările: [{ data: '2025-11-20', ora: '09:00' }, ...]
    this.programariExistente = response.data;
    
    console.log(`Loaded ${this.programariExistente.length} programări`);
  } catch (error) {
    console.error('Error loading programari:', error);
  } finally {
    this.loadingProgramari = false;
  }
}
```

**Exemplu răspuns backend:**

```json
[
  { "id": 1, "data": "2025-11-20", "ora": "09:00", "nume": "Client 1" },
  { "id": 2, "data": "2025-11-20", "ora": "10:00", "nume": "Client 2" },
  { "id": 3, "data": "2025-11-20", "ora": "11:00", "nume": "Client 3" },
  { "id": 4, "data": "2025-11-21", "ora": "09:00", "nume": "Client 4" }
]
```

**Interpretare:**
- 20 noiembrie: 3 programări (disponibilă - 🟢)
- 21 noiembrie: 1 programare (disponibilă - 🟢)

---

#### **PAS 2: Calculare Atribute Calendar**

**Ce face:**
Transformă lista de programări într-o listă de "atribute" pe care V-Calendar le înțelege (dots colorați, highlights).

**Computed Property:**

```javascript
computed: {
  calendarAttributes() {
    const attrs = [];
    
    // 1. Marchează azi cu albastru
    attrs.push({
      key: 'today',
      highlight: {
        color: 'blue',
        fillMode: 'light'
      },
      dates: new Date()  // Data de azi
    });
    
    // 2. Grupează programările pe zile
    const programariPeZi = this.programariExistente.reduce((acc, p) => {
      const dataStr = p.data;  // "2025-11-20"
      acc[dataStr] = (acc[dataStr] || 0) + 1;  // Numără programările pe zi
      return acc;
    }, {});
    // Rezultat: { "2025-11-20": 3, "2025-11-21": 1 }
    
    // 3. Pentru fiecare zi cu programări, adaugă un atribut
    Object.keys(programariPeZi).forEach(dataStr => {
      const numarProgramari = programariPeZi[dataStr];
      const data = new Date(dataStr);
      
      if (numarProgramari >= this.capacitateMaxima) {
        // Zi COMPLET ocupată (8+ programări) - DOT ROȘU
        attrs.push({
          key: `full-${dataStr}`,
          dot: { color: 'red', class: 'dot-full' },
          dates: data
        });
      } else if (numarProgramari > this.capacitateMaxima / 2) {
        // Zi PARȚIAL ocupată (5-7 programări) - DOT PORTOCALIU
        attrs.push({
          key: `partial-${dataStr}`,
          dot: { color: 'orange', class: 'dot-partial' },
          dates: data
        });
      } else {
        // Zi DISPONIBILĂ (1-4 programări) - DOT VERDE
        attrs.push({
          key: `available-${dataStr}`,
          dot: { color: 'green', class: 'dot-available' },
          dates: data
        });
      }
    });
    
    return attrs;
  }
}
```

**Pas cu pas:**

1. **`const attrs = [];`**
   - Creează array gol pentru atribute

2. **Marchează azi:**
   ```javascript
   attrs.push({
     key: 'today',
     highlight: { color: 'blue', fillMode: 'light' },
     dates: new Date()
   });
   ```
   - Adaugă highlight albastru pentru ziua curentă

3. **Grupare programări:**
   ```javascript
   const programariPeZi = this.programariExistente.reduce((acc, p) => {
     acc[p.data] = (acc[p.data] || 0) + 1;
     return acc;
   }, {});
   ```
   - `reduce()` = transformă array-ul într-un obiect
   - Din: `[{ data: '2025-11-20' }, { data: '2025-11-20' }, { data: '2025-11-21' }]`
   - În: `{ "2025-11-20": 2, "2025-11-21": 1 }`

4. **Adaugă dots colorați:**
   ```javascript
   Object.keys(programariPeZi).forEach(dataStr => {
     const numarProgramari = programariPeZi[dataStr];
     
     if (numarProgramari >= 8) {
       attrs.push({ dot: { color: 'red' }, dates: new Date(dataStr) });
     } else if (numarProgramari > 4) {
       attrs.push({ dot: { color: 'orange' }, dates: new Date(dataStr) });
     } else {
       attrs.push({ dot: { color: 'green' }, dates: new Date(dataStr) });
     }
   });
   ```
   - Pentru fiecare zi cu programări, decide culoarea dot-ului

**Rezultat final (exemplu):**

```javascript
[
  { key: 'today', highlight: { color: 'blue' }, dates: Date(2025-11-19) },
  { key: 'available-2025-11-20', dot: { color: 'green' }, dates: Date(2025-11-20) },
  { key: 'partial-2025-11-21', dot: { color: 'orange' }, dates: Date(2025-11-21) },
  { key: 'full-2025-11-22', dot: { color: 'red' }, dates: Date(2025-11-22) }
]
```

---

#### **PAS 3: Calculare Zile Disabled**

**Ce face:**
Determină care zile NU pot fi selectate (complet ocupate).

**Computed Property:**

```javascript
computed: {
  disabledDates() {
    const disabled = [];
    
    // Grupează programările pe zile (la fel ca mai sus)
    const programariPeZi = this.programariExistente.reduce((acc, p) => {
      acc[p.data] = (acc[p.data] || 0) + 1;
      return acc;
    }, {});
    
    // Pentru fiecare zi cu >= 8 programări, adaugă în disabled
    Object.keys(programariPeZi).forEach(dataStr => {
      if (programariPeZi[dataStr] >= this.capacitateMaxima) {
        disabled.push(new Date(dataStr));
      }
    });
    
    return disabled;
  }
}
```

**Exemplu:**

Dacă `programariPeZi = { "2025-11-20": 3, "2025-11-21": 8 }`:
- 20 nov: 3 programări → ✅ Poate fi selectată
- 21 nov: 8 programări → ❌ DISABLED (adăugat în array)

**Rezultat:**
```javascript
[Date(2025-11-21)]  // Doar 21 nov e disabled
```

---

#### **PAS 4: Binding V-Calendar în Template**

**Template:**

```vue
<VDatePicker 
  v-model="newProgramare.data"
  mode="date"
  :min-date="minDate"
  :attributes="calendarAttributes"
  :disabled-dates="disabledDates"
  locale="ro"
>
  <template v-slot="{ inputValue, inputEvents }">
    <input
      :value="inputValue"
      v-on="inputEvents"
      placeholder="Selectează data (YYYY-MM-DD)"
      class="calendar-input"
      readonly
    />
  </template>
</VDatePicker>
```

**Explicație directive:**

1. **`v-model="newProgramare.data"`**
   - **Ce face:** Legătură bidirecțională între calendar și variabila `data`
   - Când selectezi o dată în calendar → `newProgramare.data` se actualizează automat
   - Când schimbi `newProgramare.data` programatic → calendarul se actualizează

2. **`mode="date"`**
   - Modul de selecție: doar o singură dată (nu range, nu multiple)

3. **`:min-date="minDate"`**
   - `:` = prescurtare pentru `v-bind:`
   - Leagă proprietatea `min-date` la computed property `minDate()`
   - `minDate()` returnează `new Date()` (azi)
   - **Rezultat:** Nu poți selecta zile din trecut

4. **`:attributes="calendarAttributes"`**
   - Leagă proprietatea `attributes` la computed property `calendarAttributes()`
   - V-Calendar folosește aceste atribute pentru dots și highlights
   - Se recalculează automat când `programariExistente` se schimbă

5. **`:disabled-dates="disabledDates"`**
   - Leagă proprietatea `disabled-dates` la computed property `disabledDates()`
   - Zilele din acest array NU pot fi selectate
   - Click pe ele nu face nimic

6. **`locale="ro"`**
   - Limba calendarului (luni, denumiri luni, etc.)

7. **`<template v-slot="{ inputValue, inputEvents }">`**
   - Slot scoped = customizare input-ului
   - V-Calendar oferă `inputValue` (data formatată) și `inputEvents` (handlers click, focus, etc.)
   - Le aplicăm pe input-ul nostru custom

---

#### **PAS 5: Interacțiune User**

**Scenariul 1: User selectează o zi disponibilă (verde)**

```
1. User click pe 20 noiembrie (🟢 dot verde, 3 programări)
   ↓
2. V-Calendar validează:
   - E în viitor? ✅ (> minDate)
   - E disabled? ❌ (nu e în disabledDates)
   ↓
3. V-Calendar actualizează:
   newProgramare.data = Date(2025-11-20)
   ↓
4. Input-ul afișează: "2025-11-20"
```

**Scenariul 2: User încearcă să selecteze zi ocupată (roșu)**

```
1. User click pe 22 noiembrie (🔴 dot roșu, 8 programări)
   ↓
2. V-Calendar validează:
   - E în viitor? ✅
   - E disabled? ✅ (e în disabledDates)
   ↓
3. V-Calendar REFUZĂ selecția
   - newProgramare.data rămâne neschimbată
   - Click-ul nu face nimic
```

**Scenariul 3: User încearcă să selecteze în trecut**

```
1. User click pe 15 noiembrie (în trecut)
   ↓
2. V-Calendar validează:
   - E în viitor? ❌ (< minDate)
   ↓
3. V-Calendar REFUZĂ selecția (disabled automat prin :min-date)
```

---

#### **PAS 6: Watch pentru Reîncărcare Automată**

**Ce face:**
Când schimbi persoana, calendarul se actualizează automat cu programările noii persoane.

```javascript
watch: {
  selectedPersoana(newVal) {
    if (newVal) {
      this.loadProgramari();
    }
  }
}
```

**Explicație:**

- `watch` = observă schimbări ale unei variabile
- `selectedPersoana(newVal)` = când `selectedPersoana` se schimbă, apelează această funcție
- `newVal` = noua valoare a variabilei
- `if (newVal)` = doar dacă noua valoare NU e null
- `this.loadProgramari()` = încarcă programările pentru noua persoană

**Flow:**

```
1. User selectează "Dr. Popescu Ion"
   selectedPersoana = { id: 1, ... }
   ↓
2. Watch detectează schimbarea
   ↓
3. Apelează loadProgramari()
   ↓
4. axios.get('/programari?persoana_id=1')
   ↓
5. programariExistente = [...]
   ↓
6. calendarAttributes se recalculează automat (computed)
   ↓
7. Calendarul se actualizează cu dots noi
```

---

### 🎨 Cum Arată Calendar-ul în Browser

```
┌────────────────────────────────────────────────────┐
│  Noiembrie 2025                                    │
├────────────────────────────────────────────────────┤
│  L    M    M    J    V    S    D                  │
│                                  1    2    3       │
│  4    5    6    7    8    9   10                  │
│ 11   12   13   14   15   16   17                  │
│ 18  [19]  20🟢 21🟠 22🔴 23   24                  │
│      🔵                                            │
│ 25   26   27   28   29   30                       │
└────────────────────────────────────────────────────┘

Legendă:
🔵 = Azi (19 nov) - highlight albastru
🟢 = Disponibil (20 nov) - dot verde (3 programări)
🟠 = Parțial ocupat (21 nov) - dot portocaliu (6 programări)
🔴 = Complet ocupat (22 nov) - dot roșu (8 programări) + DISABLED

Click pe 20 nov → ✅ Se selectează
Click pe 22 nov → ❌ Nu se întâmplă nimic (disabled)
Click pe 15 nov → ❌ Nu se întâmplă nimic (în trecut)
```

---

## 3. Concepte Vue.js Folosite

### 🔹 `v-model`

**Ce face:** Legătură bidirecțională între UI și date.

```vue
<input v-model="newProgramare.nume" />
```

**Echivalent cu:**
```vue
<input 
  :value="newProgramare.nume"
  @input="newProgramare.nume = $event.target.value"
/>
```

**Flow:**
1. User scrie "Ion" în input
2. Vue detectează event-ul `input`
3. Actualizează automat `newProgramare.nume = "Ion"`
4. UI-ul se actualizează (dacă afișezi variabila undeva)

---

### 🔹 `v-if` și `v-else`

**Ce face:** Afișare condițională (elementul se adaugă/șterge din DOM).

```vue
<div v-if="loading">Se încarcă...</div>
<div v-else>Date încărcate</div>
```

**Comportament:**
- Dacă `loading = true` → primul div EXISTĂ în HTML, al doilea NU
- Dacă `loading = false` → primul div NU EXISTĂ, al doilea DA

---

### 🔹 `v-for`

**Ce face:** Repetă un element pentru fiecare item dintr-un array.

```vue
<div v-for="job in jobs" :key="job.id">
  {{ job.nume }}
</div>
```

**Rezultat:** Dacă `jobs = [{ id: 1, nume: 'Stomatolog' }, { id: 2, nume: 'Mecanic' }]`:

```html
<div>Stomatolog</div>
<div>Mecanic</div>
```

**`:key="job.id"`** = ID unic pentru fiecare element (Vue are nevoie pentru optimizare)

---

### 🔹 `@click`

**Ce face:** Ascultă event-ul de click și apelează o funcție.

```vue
<button @click="selectJob(job)">Selectează</button>
```

**Echivalent cu:**
```vue
<button v-on:click="selectJob(job)">Selectează</button>
```

**Ce se întâmplă:**
1. User click pe buton
2. Vue apelează `this.selectJob(job)` din `methods`
3. Funcția se execută cu `job` ca parametru

---

### 🔹 `:class` (class binding)

**Ce face:** Adaugă clase CSS dinamic.

```vue
<div :class="{ 'active': selectedJobId === job.id }">
```

**Rezultat:**
- Dacă `selectedJobId = 1` și `job.id = 1` → `<div class="active">`
- Dacă `selectedJobId = 1` și `job.id = 2` → `<div>` (fără clasă)

---

### 🔹 Computed Properties

**Ce face:** Proprietăți calculate bazate pe alte date, cu caching.

```javascript
computed: {
  minDate() {
    return new Date();
  }
}
```

**Când se recalculează:**
- La prima accesare
- Când dependințele se schimbă

**Diferență față de methods:**
- Computed = cached, recalculat doar când e necesar
- Methods = se execută mereu când e apelată

---

### 🔹 Watch

**Ce face:** Observă schimbări ale unei variabile și execută cod.

```javascript
watch: {
  selectedPersoana(newVal, oldVal) {
    console.log('Schimbat din', oldVal, 'în', newVal);
  }
}
```

**Când se execută:**
- De fiecare dată când `selectedPersoana` se modifică

---

## 4. Diagrame de Flow

### 🔄 Flow Complet User

```
START
  ↓
[Pagină se încarcă]
  ↓
loadJobs() → axios.get('/jobs')
  ↓
jobs = [{ id: 1, nume: 'Stomatolog' }, ...]
  ↓
[AFIȘEAZĂ: Grid Jobs]
  ↓
[USER CLICK "Stomatolog"]
  ↓
selectJob(job)
  │
  ├─ selectedJob = { id: 1, nume: 'Stomatolog' }
  ├─ selectedJobId = 1
  ├─ selectedPersoana = null
  └─ loadPersoane()
        ↓
  axios.get('/persoane?job_id=1')
        ↓
  persoane = [{ id: 1, nume: 'Popescu', prenume: 'Ion' }, ...]
        ↓
[AFIȘEAZĂ: Grid Persoane]
  ↓
[USER CLICK "Dr. Popescu Ion"]
  ↓
selectPersoana(persoana)
  │
  ├─ selectedPersoana = { id: 1, nume: 'Popescu', prenume: 'Ion' }
  ├─ newProgramare.persoana_id = 1
  ├─ loadServicii() → axios.get('/servicii?job_id=1')
  └─ loadProgramari() → axios.get('/programari?persoana_id=1')
        ↓
  servicii = [{ id: 1, descriere: 'Consultație' }, ...]
  programariExistente = [{ data: '2025-11-20', ora: '09:00' }, ...]
        ↓
[AFIȘEAZĂ: Formular + Calendar cu dots]
  ↓
[USER selectează data în calendar]
  ↓
newProgramare.data = Date(2025-11-20)
  ↓
[USER completează formular + click "Adaugă programare"]
  ↓
adaugaProgramare()
  ↓
axios.post('/programari', payload)
  ↓
[SUCCESS]
  ↓
loadProgramari() → Reîncarcă programări
  ↓
[Calendar se actualizează cu dots noi]
  ↓
END
```

---

### 🎨 Diagrama Stării Variabilelor

```
┌─────────────────────────────────────────────────────────┐
│                   LA ÎNCEPUT                             │
├─────────────────────────────────────────────────────────┤
│ selectedJob = null                                       │
│ selectedJobId = null                                     │
│ selectedPersoana = null                                  │
│ jobs = []                                                │
│ persoane = []                                            │
│ servicii = []                                            │
│ programariExistente = []                                 │
│                                                          │
│ UI: Grid Jobs (gol până se încarcă)                     │
└─────────────────────────────────────────────────────────┘
                      ↓ loadJobs()
┌─────────────────────────────────────────────────────────┐
│                 DUPĂ ÎNCĂRCARE JOBS                      │
├─────────────────────────────────────────────────────────┤
│ jobs = [{ id: 1, ... }, { id: 2, ... }]                │
│                                                          │
│ UI: Grid Jobs (cu carduri)                              │
└─────────────────────────────────────────────────────────┘
                  ↓ selectJob(job)
┌─────────────────────────────────────────────────────────┐
│               DUPĂ SELECTARE JOB                         │
├─────────────────────────────────────────────────────────┤
│ selectedJob = { id: 1, nume: 'Stomatolog' }            │
│ selectedJobId = 1                                        │
│ selectedPersoana = null                                  │
│ persoane = [] → se încarcă...                           │
│                                                          │
│ UI: Grid Jobs (cu job activ) + "Se încarcă persoanele"  │
└─────────────────────────────────────────────────────────┘
                  ↓ loadPersoane()
┌─────────────────────────────────────────────────────────┐
│             DUPĂ ÎNCĂRCARE PERSOANE                      │
├─────────────────────────────────────────────────────────┤
│ persoane = [{ id: 1, ... }, { id: 2, ... }]            │
│                                                          │
│ UI: Grid Jobs + Grid Persoane                           │
└─────────────────────────────────────────────────────────┘
                ↓ selectPersoana(persoana)
┌─────────────────────────────────────────────────────────┐
│             DUPĂ SELECTARE PERSOANĂ                      │
├─────────────────────────────────────────────────────────┤
│ selectedPersoana = { id: 1, nume: 'Popescu', ... }     │
│ servicii = [] → se încarcă...                           │
│ programariExistente = [] → se încarcă...                │
│                                                          │
│ UI: Grid Jobs + Formular (încă se încarcă date)         │
└─────────────────────────────────────────────────────────┘
         ↓ loadServicii() + loadProgramari()
┌─────────────────────────────────────────────────────────┐
│                FORMULAR COMPLET                          │
├─────────────────────────────────────────────────────────┤
│ servicii = [{ id: 1, descriere: 'Consultație' }, ...]  │
│ programariExistente = [{ data: '2025-11-20', ... }]    │
│                                                          │
│ UI: Grid Jobs + Formular COMPLET + Calendar cu dots     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Rezumat

### **Flow Selecție Persoană:**

1. **loadJobs()** → încarcă jobs de la backend
2. **selectJob()** → salvează job selectat + apelează loadPersoane()
3. **loadPersoane()** → încarcă persoane filtrate după job
4. **selectPersoana()** → salvează persoană + încarcă servicii + programări
5. **Butoane back** → resetează stările pentru navigare înapoi

### **Flow Calendar:**

1. **loadProgramari()** → încarcă programări existente pentru persoană
2. **calendarAttributes()** → calculează dots colorați (verde/portocaliu/roșu)
3. **disabledDates()** → determină zile complet ocupate
4. **VDatePicker** → afișează calendar cu dots + disabled dates
5. **watch selectedPersoana** → reîncarcă automat când schimbi persoana

### **Concepte Vue.js Cheie:**

- `v-model` = legătură bidirecțională
- `v-if` = afișare condițională
- `v-for` = repetare element
- `@click` = handler click
- `:class` = clase CSS dinamice
- `computed` = proprietăți calculate (cached)
- `watch` = observare schimbări

---

**📖 Acest document explică PAS CU PAS cum funcționează sistemul de programări Plan V2!**
