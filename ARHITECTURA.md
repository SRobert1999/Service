
## 🎯 Scop
Să vezi exact ce fir să urmărești când depistezi erori - de la click-ul utilizatorului până la salvarea în baza de date.

## 📁 Fișierele Cheie
```
services/frontend/src/views/ProgramariView.vue  ← Click utilizator
services/backend/src/main.py                      ← API endpoint
services/backend/db/models.py                    ← Baza de date
```

## 🔗 Exemplu Complet: Adăugare Programare

### 1. Vue.js - Utilizatorul apasă "Trimite"
**Fișier:** `services/frontend/src/views/ProgramariView.vue:95`
```javascript
async adaugaProgramare() {
  try {
    // Trimite datele la backend
    await axios.post("/programari", this.newProgramare);
    alert("Programare adăugată!");
  } catch (err) {
    console.error("Eroare:", err);
    alert("Eroare la adăugare!");
  }
}
```

### 2. FastAPI - Primește request-ul
**Fișier:** `services/backend/src/main.py:160`
```python
@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    # Primesc datele, le validez, le salvez
    programare = await Programari.create(**programare_data)
    return programare
```

### 3. Database Model - Salvează în baza de date
**Fișier:** `services/backend/db/models.py:19`
```python
class Programari(Model):
    id = fields.IntField(pk=True)
    nume = fields.CharField(max_length=100)
    prenume = fields.CharField(max_length=100)
    # ... alte câmpuri
```

## 🐛 Firul de Debugging

Când ai o eroare, urmează exact acești pași:

### Pas 1: Verifică Console-ul Browserului
```bash
# Deschide browser → F12 → Console
# Caută erori ca: "Network Error", "500", "400", etc.
```

### Pas 2: Verifică Network Tab
```bash
# F12 → Network → vezi request-ul către /programari
# Click pe request → Status Code: 200/400/500?
# Vezi ce trimite (Request Payload) și ce primește (Response)
```

### Pas 3: Verifică Backend Logs
```bash
docker-compose logs -f backend
# Caută erori aici - vezi exact ce primește backend-ul
```

### Pas 4: Testează API-ul Direct
```bash
# Deschide: http://localhost:5000/docs
# Încearcă manual POST /programari cu aceleași date
```

## 🔄 Flow Complet de Urmărit

```
1. User Click (ProgramariView.vue)
   ↓
2. axios.post("/programari", data)
   ↓
3. HTTP Request → Backend (main.py)
   ↓
4. @app.post("/programari") (FastAPI)
   ↓
5. Programari.create() (models.py)
   ↓
6. SQLite Database
   ↓
7. Response → Vue.js
   ↓
8. UI Update
```

## ⚡ Exemple Debugging Rapide

### Problemă: "Network Error"
```javascript
// În ProgramariView.vue, adaugă logging:
async adaugaProgramare() {
  console.log("Trimit:", this.newProgramare);  // ← Vezi ce trimiți
  try {
    await axios.post("/programari", this.newProgramare);
  } catch (err) {
    console.error("Full error:", err.response?.data || err);  // ← Vezi eroarea exactă
  }
}
```

### Problemă: Backend nu primește datele
```python
# În main.py, adaugă logging:
@app.post("/programari")
async def create_programare(prog: ProgramareIn):
    print("Primit:", prog)  # ← Vezi ce primește backend
    # ... restul codului
```

## 🎯 Checklist Debugging

Când nu funcționează, verifică în ordine:

1. **Frontend:** Datele există în `this.newProgramare`?
2. **Network:** Request-ul pleacă? (F12 → Network)
3. **Backend:** Endpoint-ul primește request-ul?
4. **Database:** Datele se salvează corect?

## 🚀 Comenzi Quick Debug

```bash
# Vezi ce e în baza de date:
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/db/programari.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM Programari ORDER BY id DESC LIMIT 5')
print(cursor.fetchall())
"

# Restart backend după modificări:
docker-compose restart backend
```

---

**Astfel știi exact ce fir să urmărești:**
Click → axios → FastAPI → Database → Response → UI