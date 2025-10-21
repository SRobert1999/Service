# 🚨 Ghidul Erorilor Comune și Soluții - Cum să Depășești Problemele de Programare

Bun venit în ghidul de depanare! Aici vei găsi cele mai comune erori pe care le poți întâlni și soluții clare, pas cu pas, cu exemple de cod. Gândește-te la acest ghid ca la un medic pentru codul tău! 🩺

---

## 🔍 **Cum Să Depanăm Erorile Eficient**

### **Procesul de Debugging - Ca un Detectiv Digital**

1. **Identifică eroarea** - Când și unde apare?
2. **Înțelege mesajul** - Ce încearcă să îți spună?
3. **Izolează problema** - Găsește codul exact care cauzează eroarea
4. **Aplică soluția** - Urmează pașii de corectare
5. **Verifică rezultatul** - Asigură-te că funcționează

**Instrumente utile:**
- **Console.log** (JavaScript) - Pentru debugging frontend
- **Print/Logging** (Python) - Pentru debugging backend
- **Developer Tools** (Browser) - Network tab, Console tab
- **Postman/Insomnia** - Pentru testare API direct

---

## 🚨 **1. Eroarea: `this.$root.$on is not a function`**

### **Când apare?**
Eroarea apare în Vue.js 3 când încerci să folosești metodele `$on`, `$off`, `$once` sau `$emit` pe instanța `$root`.

### **De ce apare?**
În Vue.js 3, API-ul de event management pe instanța `$root` a fost eliminat. Aceste metode existeau în Vue.js 2 dar nu mai sunt disponibile în Vue.js 3.

**Metafora:** E ca și cum ai încerca să folosești un telefon vechi cu aplicații noi - nu sunt compatibile!

### **Exemplu de cod care produce eroarea:**

```javascript
// ❌ ACEST COD NU FUNCȚIONEAZĂ ÎN VUE.JS 3
export default {
  created() {
    // EROARE: $on nu mai există în Vue.js 3
    this.$root.$on('user-logged-in', this.handleUserLogin);
    this.$root.$on('user-logged-out', this.handleUserLogout);
  },
  beforeDestroy() {
    // EROARE: $off nu mai există în Vue.js 3
    this.$root.$off('user-logged-in', this.handleUserLogin);
    this.$root.$off('user-logged-out', this.handleUserLogout);
  },
  methods: {
    sendMessage() {
      // EROARE: $emit nu mai există pe $root în Vue.js 3
      this.$root.$emit('show-message', {
        text: 'Salut!',
        type: 'success'
      });
    }
  }
}
```

### **Soluția 1: Folosirea `provide/inject` pattern (RECOMANDAT)**

**Componenta părinte (App.vue):**
```html
<template>
  <div id="app">
    <!-- Navigare -->
    <nav>
      <span v-if="currentUser">Bună, {{ currentUser.username }}!</span>
      <router-link v-else to="/login">Login</router-link>
    </nav>

    <!-- Conținut principal -->
    <main>
      <router-view/>
    </main>

    <!-- Componenta mesajelor -->
    <GlobalMessage ref="globalMessage" />
  </div>
</template>

<script>
import GlobalMessage from './components/GlobalMessage.vue';

export default {
  name: 'App',
  components: {
    GlobalMessage
  },
  data() {
    return {
      currentUser: null
    }
  },
  // ✅ FOLOSEȘTE PROVIDE pentru a partaja metodele
  provide() {
    return {
      showMessage: this.showMessage,
      updateUser: this.handleLogin,
      logout: this.handleLogout
    };
  },
  methods: {
    showMessage(messageData) {
      // Comunică direct cu componenta GlobalMessage
      if (this.$refs.globalMessage) {
        this.$refs.globalMessage.showMessage(messageData);
      }
    },

    handleLogin(user) {
      this.currentUser = user;
      // Salvează în localStorage pentru persistență
      localStorage.setItem('currentUser', JSON.stringify(user));
    },

    handleLogout() {
      this.currentUser = null;
      localStorage.removeItem('currentUser');
    }
  }
}
</script>
```

**Componenta copil (LoginView.vue):**
```html
<template>
  <div class="login-form">
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  // ✅ FOLOSEȘTE INJECT pentru a primi metodele
  inject: ['showMessage', 'updateUser'],
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async login() {
      try {
        // Login logic...
        const response = await axios.post('/login', {
          username: this.username,
          password: this.password
        });

        // ✅ FOLOSEȘTE METODELE INJECTATE
        this.showMessage({
          text: `Bun venit, ${this.username}!`,
          type: 'success'
        });

        this.updateUser({
          username: this.username,
          email: response.data.email
        });

      } catch (error) {
        this.showMessage({
          text: 'Username sau parolă greșită!',
          type: 'error'
        });
      }
    }
  }
}
</script>
```

### **Soluția 2: Folosirea `ref` pentru comunicare directă**

```javascript
// Componenta părinte (App.vue)
export default {
  methods: {
    showMessageToGlobalMessage(messageData) {
      // ✅ ACCES DIRECT PRIN REF
      if (this.$refs.globalMessage) {
        this.$refs.globalMessage.showMessage(messageData);
      }
    },

    sendMessageFromChild(messageData) {
      // Metodă pe care o pot apela componentele copil
      this.showMessageToGlobalMessage(messageData);
    }
  }
}
```

### **✅ Checklist pentru Corectare:**

1. **Elimină** `this.$root.$on()` din metodele `created()`
2. **Elimină** `this.$root.$off()` din metodele `beforeDestroy()`
3. **Înlocuiește** `beforeDestroy` cu `beforeUnmount` (nume nou în Vue.js 3)
4. **Folosește** `provide/inject` sau `ref` pentru comunicare între componente
5. **Testează** că evenimentele funcționează corect după modificări

---

## 🚨 **2. Eroarea: `422 Unprocessable Entity` la Adăugarea Programărilor**

### **Când apare?**
Când încerci să trimiți un formular la API și validarea de pe server eșuează. Codul de status 422 înseamnă "Entitate neprocesabilă" - serverul înțelege request-ul, dar datele sunt invalide.

### **De ce apare?**
API-ul returnează 422 când datele trimise nu respectă schema de validare Pydantic din backend.

**Metafora:** E ca și cum ai încerca să trimiți o scrisoare la poștă fără timbru sau adresă corectă - poștășul o refuză!

### **Exemplu de request care cauzează eroarea:**

```javascript
// ❌ REQUEST INVALID - CAUZEAAZĂ 422
const invalidPayload = {
  data: '',                    // String gol - ar trebui să fie null sau valid
  ora: '',                     // String gol - ar trebui să fie null sau valid
  nume: '',                    // String gol - ar trebui să fie valid
  prenume: null,               // OK - null este permis
  email: 'email-invalid',      // Format invalid de email
  telefon: '123',              // Prea scurt pentru telefon românesc
  observatii: '',              // String gol - e OK să fie gol
  persoana_id: 'abc',          // String în loc de integer
  serviciu_id: -1              // ID negativ - probabil invalid
};

// Acest request va returna 422
await axios.post('/api/programari', invalidPayload);
```

### **Cauze comune și soluții:**

#### **Cauza 1: Stringuri goale în loc de `null`**

```javascript
// ❌ PROBLEMĂ - Stringuri goale
const badPayload = {
  data: '',
  ora: '',
  nume: '',
  prenume: '',
  email: '',
  telefon: ''
};

// ✅ SOLUȚIE - Transformă stringurile goale în null
function cleanPayload(payload) {
  return Object.keys(payload).reduce((cleaned, key) => {
    const value = payload[key];
    if (value === '' || value === undefined) {
      cleaned[key] = null;  // String gol devine null
    } else {
      cleaned[key] = value;
    }
    return cleaned;
  }, {});
}

// Folosire:
const goodPayload = cleanPayload({
  data: this.newProgramare.data,
  ora: this.newProgramare.ora,
  nume: this.newProgramare.nume,
  prenume: this.newProgramare.prenume,
  email: this.newProgramare.email,
  telefon: this.newProgramare.telefon,
  observatii: this.newProgramare.observatii,
  persoana_id: this.newProgramare.persoana_id,
  serviciu_id: this.newProgramare.serviciu_id
});

// Acum request-ul va funcționa
await axios.post('/api/programari', goodPayload);
```

#### **Cauza 2: Câmpuri obligatorii lipsă**

```javascript
// ❌ PROBLEMĂ - Lipsesc data și ora (câmpuri obligatorii)
const incompletePayload = {
  nume: 'John Doe',
  email: 'john@example.com'
  // data și ora lipsesc!
};

// ✅ SOLUȚIE - Validare frontend înainte de trimitere
function validatePayload(payload) {
  const errors = [];

  if (!payload.data || payload.data.trim() === '') {
    errors.push('Data este obligatorie');
  }

  if (!payload.ora || payload.ora.trim() === '') {
    errors.push('Ora este obligatorie');
  }

  if (errors.length > 0) {
    throw new Error(errors.join(', '));
  }

  return true;
}

// Folosire în componenta Vue:
async adaugaProgramare() {
  try {
    // Validare frontend
    validatePayload(this.newProgramare);

    // Trimite request-ul
    const response = await axios.post('/api/programari', this.newProgramare);

    // Succes...

  } catch (error) {
    if (error.message.includes('obligatorie')) {
      // Afișează eroarea de validare
      this.showError(error.message);
    } else {
      // Alte erori (network, server)
      this.showError('Eroare la conectare');
    }
  }
}
```

#### **Cauza 3: Format invalid de date**

```javascript
// ❌ PROBLEMĂ - Formate invalide
const badFormats = {
  data: '2025-13-45',     // Lună 13 și ziua 45 nu există
  ora: '25:70',           // Ora 25 și minutele 70 nu există
  email: 'fără@sufix',    // Email invalid
  telefon: 'abc'          // Telefon invalid
};

// ✅ SOLUȚIE - Validare format cu regex
function validateFormats(payload) {
  const errors = [];

  // Validare format dată (YYYY-MM-DD)
  if (payload.data && !/^\d{4}-\d{2}-\d{2}$/.test(payload.data)) {
    errors.push('Data trebuie să fie în format YYYY-MM-DD');
  }

  // Validare format oră (HH:MM)
  if (payload.ora && !/^\d{2}:\d{2}$/.test(payload.ora)) {
    errors.push('Ora trebuie să fie în format HH:MM');
  }

  // Validare email
  if (payload.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) {
    errors.push('Email invalid');
  }

  // Validare telefon românesc
  if (payload.telefon && !/^(\+4|0)[0-9]{9}$/.test(payload.telefon.replace(/\s/g, ''))) {
    errors.push('Telefonul trebuie să fie în format românesc (ex: 0723123456)');
  }

  if (errors.length > 0) {
    throw new Error(errors.join(', '));
  }

  return true;
}
```

### **Exemplu complet de soluție:**

```html
<!-- ProgramariView.vue - Formular robust -->
<template>
  <div class="programari-form">
    <h2>Adaugă Programare</h2>

    <form @submit.prevent="adaugaProgramare">
      <!-- Data -->
      <div class="form-group">
        <label>Data *</label>
        <input
          v-model="newProgramare.data"
          type="date"
          :min="todayDate"
          required
        >
        <span v-if="errors.data" class="error">{{ errors.data }}</span>
      </div>

      <!-- Ora -->
      <div class="form-group">
        <label>Ora *</label>
        <input
          v-model="newProgramare.ora"
          type="time"
          required
        >
        <span v-if="errors.ora" class="error">{{ errors.ora }}</span>
      </div>

      <!-- Email -->
      <div class="form-group">
        <label>Email</label>
        <input
          v-model="newProgramare.email"
          type="email"
          placeholder="email@example.com"
        >
        <span v-if="errors.email" class="error">{{ errors.email }}</span>
      </div>

      <!-- Telefon -->
      <div class="form-group">
        <label>Telefon</label>
        <input
          v-model="newProgramare.telefon"
          type="tel"
          placeholder="07xx xxx xxx"
          @input="formatTelefon"
        >
        <span v-if="errors.telefon" class="error">{{ errors.telefon }}</span>
      </div>

      <!-- Submit -->
      <button type="submit" :disabled="loading">
        {{ loading ? 'Se salvează...' : 'Adaugă Programare' }}
      </button>
    </form>

    <!-- Mesaje de eroare generale -->
    <div v-if="generalError" class="general-error">
      {{ generalError }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgramariView',
  data() {
    return {
      loading: false,
      newProgramare: {
        data: '',
        ora: '',
        nume: '',
        prenume: '',
        email: '',
        telefon: '',
        observatii: '',
        persoana_id: null,
        serviciu_id: null
      },
      errors: {},
      generalError: ''
    }
  },
  computed: {
    todayDate() {
      return new Date().toISOString().split('T')[0];
    }
  },
  methods: {
    formatTelefon() {
      // Formatează automat telefonul
      let telefon = this.newProgramare.telefon.replace(/\D/g, '');

      if (telefon.startsWith('40') && telefon.length === 12) {
        telefon = '0' + telefon.slice(2);
      }

      if (telefon.length === 10 && telefon.startsWith('0')) {
        this.newProgramare.telefon = telefon;
      }
    },

    validateForm() {
      this.errors = {};
      this.generalError = '';

      // Validare date obligatorii
      if (!this.newProgramare.data) {
        this.errors.data = 'Data este obligatorie';
      }

      if (!this.newProgramare.ora) {
        this.errors.ora = 'Ora este obligatorie';
      }

      // Validare data nu e în trecut
      if (this.newProgramare.data) {
        const dataSelectata = new Date(this.newProgramare.data);
        const dataCurenta = new Date();
        dataCurenta.setHours(0, 0, 0, 0);

        if (dataSelectata < dataCurenta) {
          this.errors.data = 'Data nu poate fi în trecut';
        }
      }

      // Validare email
      if (this.newProgramare.email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.newProgramare.email)) {
          this.errors.email = 'Email invalid';
        }
      }

      // Validare telefon
      if (this.newProgramare.telefon) {
        const telefonCuratat = this.newProgramare.telefon.replace(/\D/g, '');
        const telefonRegex = /^0[0-9]{9}$/;

        if (!telefonRegex.test(telefonCuratat)) {
          this.errors.telefon = 'Telefonul trebuie să fie în format românesc (10 cifre, începe cu 0)';
        }
      }

      // Returnează true dacă nu există erori
      return Object.keys(this.errors).length === 0;
    },

    cleanPayload(payload) {
      // Transformă stringurile goale în null
      return Object.keys(payload).reduce((cleaned, key) => {
        const value = payload[key];
        cleaned[key] = (value === '' || value === undefined) ? null : value;
        return cleaned;
      }, {});
    },

    async adaugaProgramare() {
      try {
        // 1. Validare frontend
        if (!this.validateForm()) {
          return;
        }

        this.loading = true;

        // 2. Curățare date
        const cleanedPayload = this.cleanPayload(this.newProgramare);

        console.log('Sending payload:', cleanedPayload);

        // 3. Trimite către backend
        const response = await axios.post('/api/programari', cleanedPayload);

        console.log('Response:', response.data);

        // 4. Succes
        this.showMessage({
          text: '✅ Programare creată cu succes!',
          type: 'success'
        });

        // 5. Resetare formular
        this.resetForm();

        // 6. Reîncărcare listă (dacă e necesar)
        await this.incarcaProgramari();

      } catch (error) {
        console.error('Error creating appointment:', error);

        // 7. Gestionare erori
        if (error.response?.status === 422) {
          // Eroare de validare de la backend
          const backendErrors = error.response.data.detail;

          if (Array.isArray(backendErrors)) {
            // Erori multiple
            backendErrors.forEach(err => {
              const fieldName = err.loc?.[1];
              if (fieldName) {
                this.errors[fieldName] = err.msg;
              }
            });
          } else {
            // Eroare singulară
            this.generalError = backendErrors;
          }

        } else if (error.response?.data?.detail) {
          // Alte erori de la backend
          this.generalError = error.response.data.detail;

        } else {
          // Erori de rețea sau altele
          this.generalError = 'Eroare la conectarea cu serverul';
        }

        // Afișează eroarea în sistemul de mesaje
        this.showMessage({
          text: this.generalError || 'Eroare la crearea programării',
          type: 'error'
        });

      } finally {
        this.loading = false;
      }
    },

    resetForm() {
      this.newProgramare = {
        data: '',
        ora: '',
        nume: '',
        prenume: '',
        email: '',
        telefon: '',
        observatii: '',
        persoana_id: null,
        serviciu_id: null
      };
      this.errors = {};
    }
  }
}
</script>

<style scoped>
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 2px solid #ddd;
  border-radius: 4px;
}

.form-group input.error {
  border-color: #dc3545;
}

.error {
  color: #dc3545;
  font-size: 12px;
  margin-top: 5px;
  display: block;
}

.general-error {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}
</style>
```

### **✅ Checklist pentru Corectare 422:**

1. **Verifică** payload-ul trimis către API
2. **Validează** datele în frontend înainte de trimitere
3. **Transformă** stringurile goale în `null`
4. **Verifică** formatul datelor (dată, oră, email, telefon)
5. **Asigură-te** că toate câmpurile obligatorii sunt completate
6. **Loghează** request-ul pentru debugging: `console.log(payload)`
7. **Consultă** documentația API: `http://localhost:5000/docs`

---

## 🚨 **3. Eroarea: `Connection closed` la Baza de Date SQLite**

### **Când apare?**
Când backend-ul încearcă să acceseze baza de date dar conexiunea este închisă. De obicei apare la pornirea aplicației sau la primul request.

### **De ce apare?**
De obicei apare când:
- Baza de date nu există
- Baza de date este coruptă
- Permisiuniile sunt incorecte
- Tortoise ORM nu este inițializat corect

**Metafora:** E ca și cum ai încerca să intri într-o casă, dar ușa este încuiată sau cheia nu se potrivește!

### **Verificare și Diagnosticare:**

#### **Pasul 1: Verifică dacă baza de date există**

```bash
# Intră în containerul Docker
docker-compose exec backend bash

# Verifică fișierele din directorul bazei de date
ls -la /app/db/

# Ar trebui să vezi:
# -rw-r--r-- 1 root root  8192 Dec 15 10:30 programari.db
# -rw-r--r-- 1 root root 32768 Dec 15 10:30 programari.db-wal
# -rw-r--r-- 1 root root  4096 Dec 15 10:30 programari.db-shm
```

#### **Pasul 2: Verifică conexiunea la baza de date**

```python
# Test conexiune direct în container
docker-compose exec backend python -c "
import sqlite3
import os

# Verifică calea către baza de date
db_path = '/app/db/programari.db'
print(f'DB path exists: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    try:
        # Încearcă să conectezi
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verifică tabelele
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
        tables = cursor.fetchall()
        print(f'Tabele în baza de date: {tables}')

        # Închide conexiunea
        conn.close()
        print('✅ Conexiune reușită!')

    except Exception as e:
        print(f'❌ Eroare conexiune: {e}')
else:
    print('❌ Fișierul bazei de date nu există!')
"
```

### **Soluția 1: Recrearea Bazei de Date**

```bash
# Recrează baza de date cu date inițiale
docker-compose exec backend python -c "
import asyncio
from tortoise import Tortoise
from db.models import Persoane, Servicii, Programari
import datetime

async def recreate_database():
    try:
        # 1. Conectează-te la baza de date
        await Tortoise.init(
            db_url='sqlite://db/programari.db',
            modules={'models': ['db.models']}
        )

        print('🔗 Conectat la baza de date')

        # 2. Generează tabelele (dacă nu există)
        await Tortoise.generate_schemas()
        print('📊 Scheme generate')

        # 3. Verifică dacă există deja date
        persoane_count = await Persoane.all().count()
        servicii_count = await Servicii.all().count()

        print(f'👥 Persoane existente: {persoane_count}')
        print(f'🛠️ Servicii existente: {servicii_count}')

        # 4. Adaugă date de test (dacă nu există)
        if persoane_count == 0:
            print('➕ Adăugare persoane de test...')
            await Persoane.create(nume='Popescu', prenume='Ion')
            await Persoane.create(nume='Ionescu', prenume='Maria')
            await Persoane.create(nume='Georgescu', prenume='Gheorghe')
            print('✅ Persoane adăugate')

        if servicii_count == 0:
            print('➕ Adăugare servicii de test...')
            await Servicii.create(descriere='Consultație generală')
            await Servicii.create(descriere='Control de rutină')
            await Servicii.create(descriere='Tratament specializat')
            print('✅ Servicii adăugate')

        # 5. Verifică finală
        persoane_final = await Persoane.all()
        servicii_final = await Servicii.all()

        print(f'🎉 Baza de date recreată cu succes!')
        print(f'   - Persoane: {len(persoane_final)}')
        print(f'   - Servicii: {len(servicii_final)}')

        # Afișează datele
        print('📋 Persoane:')
        for persoana in persoane_final:
            print(f'   - {persoana.nume} {persoana.prenume}')

        print('🛠️ Servicii:')
        for serviciu in servicii_final:
            print(f'   - {serviciu.descriere}')

    except Exception as e:
        print(f'❌ Eroare la recrearea bazei de date: {e}')
        raise
    finally:
        await Tortoise.close_connections()

# Rulează funcția
asyncio.run(recreate_database())
"
```

### **Soluția 2: Verificarea Configurării Tortoise**

**Verifică `main.py`:**
```python
# ✅ CONFIGURARE CORECTĂ
from tortoise.contrib.fastapi import register_tortoise

# Înregistrează Tortoise ORM
register_tortoise(
    app,
    db_url="sqlite://db/programari.db",  # Corect: relativ la container
    modules={"models": ["db.models"]},
    generate_schemas=True,  # Generează tabelele automat
    add_exception_handlers=True,  # Adaugă handlere de erori
)
```

**Verifică `db/config.py` (dacă există):**
```python
# ✅ CONFIGURARE CORECTĂ
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db/programari.db"
    },
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        }
    }
}
```

### **Soluția 3: Verificarea Permisiunilor Docker**

```bash
# Verifică permisiunile pe fișierul DB
docker-compose exec backend ls -la /app/db/

# Dacă permisiunile sunt incorecte, repară:
docker-compose exec backend chown -R root:root /app/db/
docker-compose exec backend chmod -R 644 /app/db/*.db
```

### **Soluția 4: Recrearea Volumelor Docker**

```bash
# Oprește serviciile
docker-compose down

# Șterge volumele (ATENȚIE - vei pierde datele!)
docker volume rm services_backend_db

# Pornește din nou serviciile
docker-compose up -d --build

# Verifică dacă funcționează
curl http://localhost:5000/
```

### **Soluția 5: Verificarea Volume Mount în `docker-compose.yml`**

```yaml
# ✅ CONFIGURARE CORECTĂ
version: '3.8'

services:
  backend:
    build: ./services/backend
    ports:
      - "5000:5000"
    volumes:
      # ✅ CORECT - Mapează directorul DB local în container
      - ./services/backend/db:/app/db
    environment:
      - DATABASE_URL=sqlite:///app/db/programari.db
    working_dir: /app
```

### **Exemplu de Script de Recuperare Completă:**

```bash
#!/bin/bash
# recover_database.sh - Script pentru recuperarea bazei de date

echo "🔧 Începem recuperarea bazei de date..."

# 1. Oprește serviciile
echo "⏹️ Oprim serviciile..."
docker-compose down

# 2. Curăță fișierele DB corupte
echo "🧹 Curățăm fișierele vechi..."
if [ -f "./services/backend/db/programari.db" ]; then
    mv "./services/backend/db/programari.db" "./services/backend/db/programari.db.backup.$(date +%Y%m%d_%H%M%S)"
fi

rm -f ./services/backend/db/*.db-wal
rm -f ./services/backend/db/*.db-shm

# 3. Creează directorul DB dacă nu există
mkdir -p ./services/backend/db

# 4. Pornește serviciile
echo "🚀 Pornim serviciile..."
docker-compose up -d --build

# 5. Așteaptă 5 secunde pentru startup
echo("⏳ Așteptăm startup-ul...")
sleep 5

# 6. Recrează baza de date
echo("📊 Recreăm baza de date...")
docker-compose exec backend python -c "
import asyncio
from tortoise import Tortoise
from db.models import Persoane, Servicii

async def init():
    await Tortoise.init(
        db_url='sqlite://db/programari.db',
        modules={'models': ['db.models']}
    )
    await Tortoise.generate_schemas()

    # Adaugă date de test
    if await Persoane.all().count() == 0:
        await Persoane.create(nume='Popescu', prenume='Ion')
        await Persoane.create(nume='Ionescu', prenume='Maria')

    if await Servicii.all().count() == 0:
        await Servicii.create(descriere='Consultație')
        await Servicii.create(descriere='Control')

    print('✅ Baza de date inițializată!')
    await Tortoise.close_connections()

asyncio.run(init())
"

# 7. Verifică statusul
echo("🔍 Verificăm statusul...")
if curl -s http://localhost:5000/ > /dev/null; then
    echo("✅ Serverul rulează corect!")
else
    echo("❌ Serverul nu rulează!")
    exit 1
fi

echo("🎉 Recuperare completă!")
```

### **✅ Checklist pentru Corectare Conexiune BD:**

1. **Verifică** dacă fișierul `programari.db` există
2. **Verifică** permisiunile fișierelor
3. **Verifică** configurarea `docker-compose.yml`
4. **Verifică** configurarea Tortoise în `main.py`
5. **Recrează** baza de date cu scriptul de mai sus
6. **Testează** conexiunea cu un request simplu
7. **Consultă** log-urile backend: `docker-compose logs -f backend`

---

## 🔧 **4. Eroarea: `ModuleNotFoundError: No module named 'src.auth.users'`**

### **Când apare?**
Când Python nu poate găsi modulele necesare în structura de directoare.

### **De ce apare?**
Lipsa fișierelor `__init__.py` sau structură incorectă de importuri.

### **Soluția rapidă:**

```bash
# Creează fișierele __init__.py lipsă
touch services/backend/src/__init__.py
touch services/backend/src/auth/__init__.py
touch services/backend/src/crud/__init__.py
touch services/backend/src/routes/__init__.py
touch services/backend/src/schemas/__init__.py

# Restart services
docker-compose restart backend
```

---

## 🌐 **5. Eroarea: `CORS policy: No 'Access-Control-Allow-Origin' header`**

### **Când apare?**
Când frontend-ul (Vue.js) încearcă să facă request către backend dar este blocat de politica CORS.

### **De ce apare?**
Backend-ul nu este configurat să permită request-uri de la originea frontend-ului.

### **Soluția:**

```python
# În main.py - asigură-te că ai CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",   # Frontend URL
        "http://127.0.0.1:8080"   # Alternative URL
    ],
    allow_credentials=True,    # Pentru cookie-uri
    allow_methods=["*"],       # Toate metodele
    allow_headers=["*"],       # Toate header-ele
)
```

---

## 📝 **Sfaturi Generale pentru Debugging Eficient**

### **1. Folosește Console.log Extensiv**

```javascript
// În Vue.js - Debugging request-uri
async login() {
  console.log('🔐 Începem login...');
  console.log('Username:', this.username);

  try {
    console.log('📤 Trimit request către /api/users/login');
    const response = await axios.post('/api/users/login', {
      username: this.username,
      password: this.password
    });

    console.log('📥 Răspuns primit:', response.data);
    console.log('✅ Login successful!');

  } catch (error) {
    console.error('❌ Eroare login:', error);
    console.error('Status:', error.response?.status);
    console.error('Data:', error.response?.data);
    console.error('Headers:', error.response?.headers);
  }
}
```

### **2. Folosește Developer Tools în Browser**

1. **Tab-ul Console:** Erori JavaScript
2. **Tab-ul Network:** Request-uri HTTP
3. **Tab-ul Application:** Cookie-uri și localStorage

### **3. Verifică Log-urile Backend**

```bash
# Vezi log-urile în timp real
docker-compose logs -f backend

# Caută erori specifice
docker-compose logs backend | grep -i error
docker-compose logs backend | grep -i exception
```

### **4. Testează API-ul Direct**

```bash
# Test endpoint de sănătate
curl http://localhost:5000/

# Test cu payload
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

### **5. Folosește Postman sau Insomnia**

- Importă API documentation: `http://localhost:5000/docs`
- Testează fiecare endpoint separat
- Verifică request/response headers
- Salvează request-uri pentru debugging rapid

### **🔍 Structura de Debuging Eficient:**

1. **Izolează problema** - Identifică exact ce nu funcționează
2. **Verifică inputs** - Datele primite sunt corecte?
3. **Verifică process** - Logica internă funcționează?
4. **Verifică outputs** - Răspunsurile sunt corecte?
5. **Verifică integration** - Comunicația între componente?

---

## 🎯 **Concluzii - Devino un Expert în Debugging**

### **Mindset-ul Corect pentru Debugging:**

1. **Fii metodic** - Urmează pași logici
2. **Documentează** - Notează ce ai încercat
3. **Izolează** - Găsește problema exactă
4. **Testează soluțiile** - Verifică că funcționează
5. **Învață din erori** - Fiecare eroare e o oportunitate

### **Instrumente Esențiale:**

- **Developer Tools** - Browser debugging
- **Console.log** - JavaScript debugging
- **Print statements** - Python debugging
- **API Documentation** - `http://localhost:5000/docs`
- **Docker logs** - Server debugging
- **Postman/Insomnia** - API testing

### **Cele Mai Comune Erori și Soluții Rapide:**

1. **`$root.$on` nu există** → Folosește `provide/inject`
2. **`422 Unprocessable`** → Validare date frontend/backend
3. **`Connection closed`** → Recrează baza de date
4. **`ModuleNotFoundError`** → Adaugă `__init__.py`
5. **`CORS error`** → Configurează CORS middleware

### **Următorii Pași:**

1. **Setează debugging tools** - Configurează browser și IDE
2. **Creează checklist** - Pentru probleme comune
3. **Documentează soluții** - Pentru viitorul tău
4. **Practică constant** - Debugging e o artă ce se învață

**Felicitări!** Acum ai cunoștințele necesare pentru a depăși majoritatea problemelor de programare. Fiecare eroare rezolvată te face un dezvoltator mai bun! 💪

**Amintește:** Nu există programatori perfecti, dar există programatori care știu cum să rezolve problemele! 🚀