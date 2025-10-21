# 📗 Ghidul Dezvoltatorului Începător - Cum s-a Construit Sistemul de Programări

Bun venit în jurnalul de dezvoltare! Acest document explică pas cu pas cum am construit aplicația de programări online, cu exemple concrete de cod pe care le poți înțelege chiar dacă ești la început de drum.

---

## 🎯 **Pasul 1: Crearea Bazei de Date pentru Utilizatori**

### **Ce am construit?**
Am adăugat posibilitatea de a crea conturi de utilizator în sistemul nostru.

### **Cum arată codul?**

**1. Modelul Utilizator în Python (`db/models.py`):**
```python
class Users(Model):
    id = fields.IntField(pk=True)                    # ID unic pentru fiecare utilizator
    username = fields.CharField(max_length=50, unique=True)  # Numele de utilizator (unic!)
    password = fields.CharField(max_length=200)      # Parola (va fi criptată)
    email = fields.CharField(max_length=200, unique=True)    # Email (unic!)
    created_at = fields.DatetimeField(auto_now_add=True)      # Data creării automat
    modified_at = fields.DatetimeField(auto_now=True)         # Data modificării automat
```

**De ce e important?**
- `unique=True` înseamnă că nu pot exista doi utilizatori cu același nume sau email
- Parola nu se salvează în text clar, ci criptată (vom vedea mai jos cum)

**2. Rezolvarea erorilor de import:**
```python
# În main.py - am adăugat importul lipsă
from tortoise import Tortoise
```

### **💡 Ce înveți de aici?**
- **Baze de date**: Cum definești tabele și coloane
- **Unicitate**: Cum te asiguri că anumite date nu se repetă
- **Timestamps**: Cum înregistrezi automat când se creează/modifică ceva

---

## 🔐 **Pasul 2: Construirea Sistemului de Autentificare (Login & Register)**

### **Ce am construit?**
Un sistem complet de înregistrare și autentificare, similar cu cel de pe Facebook sau Google!

### **1. Configurarea Dependințelor (`requirements.txt`):**
```txt
fastapi==0.104.1
tortoise-orm==0.20.0
email-validator==1.3.1      # Pentru validarea email-urilor
python-multipart==0.0.5     # Pentru formular HTML
python-jose[cryptography]==3.3.0  # Pentru token-uri JWT
passlib[bcrypt]==1.7.4      # Pentru criptarea parolelor
```

### **2. Criptarea Parolelor (SUPER IMPORTANT!)**
Niciodată nu salvăm parolele în text clar! Le criptăm cu bcrypt:

**Backend - Funcția de criptare (`auth/users.py`):**
```python
from passlib.context import CryptContext

# Context pentru criptare
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Transformă parola în text clar într-un hash securizat"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifică dacă parola introdusă se potrivește cu hash-ul din baza de date"""
    return pwd_context.verify(plain_password, hashed_password)

# Exemplu:
# Parola: "parola123"
# Devine: "$2b$12$EixZaYVK1fsbw1ZfbX3MXe.VePOcXMRqZt7hdKZdVjF8/FrrT.H."
```

### **3. Cum Funcționează Login-ul:**

**Backend - Login Endpoint (`routes/users.py`):**
```python
@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Cautăm utilizatorul în baza de date
    user = await Users.get_or_none(username=form_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Utilizator inexistent")

    # 2. Verificăm parola (comparăm cu cea criptată)
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Parolă greșită")

    # 3. Creăm un token JWT (bilet de acces)
    access_token = create_access_token(data={"sub": user.username})

    # 4. Setăm un cookie securizat
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        httponly=True,      # JavaScript nu poate accesa cookie-ul (securitate!)
        max_age=1800,       # Expire după 30 minute
        samesite="Lax",     # Protecție CSRF
    )

    return {"message": "Login successful", "username": user.username}
```

**Frontend - Formular de Login (`LoginView.vue`):**
```html
<template>
  <div class="login-container">
    <h2>🔐 Autentificare</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Nume utilizator:</label>
        <input
          v-model="loginForm.username"
          type="text"
          placeholder="ex: john_doe"
          required
        >
      </div>

      <div class="form-group">
        <label>Parolă:</label>
        <input
          v-model="loginForm.password"
          type="password"
          placeholder="parola ta"
          required
        >
      </div>

      <button type="submit" class="login-btn">🚪 Intră în cont</button>
    </form>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      errorMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = '';  // Resetăm eroarea

      try {
        # Trimitem datele la backend
        const formData = new FormData();
        formData.append('username', this.loginForm.username);
        formData.append('password', this.loginForm.password);

        const response = await axios.post('/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        # Verificăm dacă suntem logați
        const userResponse = await axios.get('/users/whoami');

        # Afișăm mesaj de bun venit
        alert(`🎉 Bun venit, ${userResponse.data.username}!`);

        # Redirecționăm către pagina principală
        this.$router.push('/programari');

      } catch (error) {
        console.error('Eroare login:', error);
        this.errorMessage = 'Username sau parolă greșită!';
      }
    }
  }
}
</script>

<style>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background: white;
}

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
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

.login-btn:hover {
  background: #0056b3;
}

.error {
  color: red;
  text-align: center;
  margin-top: 10px;
}
</style>
```

### **💡 Ce înveți de aici?**
- **Securitate**: Criptarea paralelor (hashing)
- **JWT Tokens**: Bilete de acces pentru sesiuni
- **Cookie-uri**: Stocare securizată în browser
- **Frontend-Backend**: Cum comunică formularul cu serverul
- **Validare**: Cum afișăm erori utilizatorului

---

## 💾 **Pasul 3: Persistența Datelor (Să nu pierdem nimic!)**

### **Ce problemă am rezolvat?**
Imaginează-ți că scrii o lucrare importantă, dar la fiecare repornire a calculatorului, totul dispare. Așa se întâmpla și cu baza noastră de date!

### **Soluția Magică (în `docker-compose.yml`):**
```yaml
backend:
  build: ./services/backend
  volumes:
    # Leagă directorul local cu cel din container
    - ./services/backend/db:/app/db
```

**Ce înseamnă asta?**
- `./services/backend/db` = Directorul tău pe calculator
- `/app/db` = Directorul din containerul Docker
- `:` = Leagă cele două directoare împreună

**Rezultatul:** Acum orice salvăm în baza de date rămâne salvată chiar dacă repornim serverul!

### **Datele noastre valoroase:**
```sql
-- Persoane (cliienții noștri)
1. Stratulat Robert
2. Mihai Ciuc
3. Adrian Popa

-- Servicii (ce oferim)
1. Consultație - 150 RON
2. Aparat dentar - 300 RON
3. Control - 100 RON
```

---

## 🎨 **Pasul 4: Crearea Interfeței Complete (Partea Frumoasă!)**

### **Ce am construit?**
O pagină de login și înregistrare cu tab-uri, ca pe aplicațiile moderne!

### **Componenta Vue.js Completă (`LoginView.vue`):**

**Template-ul HTML:**
```html
<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>🏥 Sistem Programări Medicale</h1>

      <!-- Tab-uri pentru Login/Register -->
      <div class="tabs">
        <button
          @click="activeTab = 'login'"
          :class="{active: activeTab === 'login'}"
        >
          🔑 Autentificare
        </button>
        <button
          @click="activeTab = 'register'"
          :class="{active: activeTab === 'register'}"
        >
          ✏️ Înregistrare
        </button>
      </div>

      <!-- Formular de Login -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>👤 Nume utilizator:</label>
          <input
            v-model="loginForm.username"
            type="text"
            placeholder="ex: john_doe"
            required
          >
        </div>

        <div class="form-group">
          <label>🔒 Parolă:</label>
          <input
            v-model="loginForm.password"
            type="password"
            placeholder="parola ta"
            required
          >
        </div>

        <button type="submit" class="submit-btn">🚪 Intră în cont</button>
      </form>

      <!-- Formular de Înregistrare -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>👤 Nume utilizator:</label>
          <input
            v-model="registerForm.username"
            type="text"
            placeholder="alege un username unic"
            required
          >
        </div>

        <div class="form-group">
          <label>📧 Email:</label>
          <input
            v-model="registerForm.email"
            type="email"
            placeholder="ex: john@example.com"
            required
          >
        </div>

        <div class="form-group">
          <label>🔒 Parolă:</label>
          <input
            v-model="registerForm.password"
            type="password"
            placeholder="minim 6 caractere"
            required
          >
        </div>

        <div class="form-group">
          <label>🔒 Confirmă parola:</label>
          <input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="rescrie parola"
            required
          >
        </div>

        <button type="submit" class="submit-btn">✨ Creează cont nou</button>
      </form>

      <!-- Mesaje de eroare/succes -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeTab: 'login',  // Arată login-ul în mod implicit
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      message: '',
      messageType: ''
    }
  },
  methods: {
    async handleRegister() {
      this.clearMessages();

      // Validare: parolele trebuie să fie la fel
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.showMessage('Parolele nu sunt identice!', 'error');
        return;
      }

      if (this.registerForm.password.length < 6) {
        this.showMessage('Parola trebuie să aibă minim 6 caractere!', 'error');
        return;
      }

      try {
        // Trimitere date la backend
        const response = await axios.post('/register', this.registerForm);
        this.showMessage('✅ Cont creat cu succes! Te poți loga acum.', 'success');
        this.activeTab = 'login';  // Trecem la tab-ul de login
        this.clearRegisterForm();

      } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Eroare la creare cont!';
        this.showMessage(errorMsg, 'error');
      }
    },

    async handleLogin() {
      this.clearMessages();

      try {
        // Trimitem datele la backend
        const formData = new FormData();
        formData.append('username', this.loginForm.username);
        formData.append('password', this.loginForm.password);

        const response = await axios.post('/login', formData);

        // Verificăm dacă suntem logați
        const userResponse = await axios.get('/users/whoami');

        this.showMessage(`🎉 Bun venit, ${userResponse.data.username}!`, 'success');

        // Așteptăm puțin și redirecționăm
        setTimeout(() => {
          this.$router.push('/programari');
        }, 1500);

      } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Username sau parolă greșită!';
        this.showMessage(errorMsg, 'error');
      }
    },

    showMessage(text, type) {
      this.message = text;
      this.messageType = type;
    },

    clearMessages() {
      this.message = '';
      this.messageType = '';
    },

    clearRegisterForm() {
      this.registerForm = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      };
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  width: 100%;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.tabs {
  display: flex;
  margin-bottom: 30px;
}

.tabs button {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f8f9fa;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  transition: all 0.3s ease;
}

.tabs button.active {
  background: #007bff;
  color: white;
}

.auth-form {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.submit-btn:hover {
  background: #218838;
}

.message {
  padding: 12px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
  font-weight: 600;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
```

### **Configurarea Rutei (`router/index.js`):**
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ProgramariView from '../views/ProgramariView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/programari',
    name: 'programari',
    component: ProgramariView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView  // Noua rută pentru login!
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
```

### **💡 Ce înveți de aici?**
- **Componente Vue**: Cum structurezi o pagină web complexă
- **Tab-uri UI**: Cum faci interfață cu tab-uri
- **Formulare**: Cum preiei validezi date de la utilizatori
- **CSS Avansat**: Gradienturi, animații, design modern
- **Routing**: Cum navighezi între pagini
- **Stare componentă**: Cum gestionezi data într-o componentă Vue

---

## 🔧 **Pasul 5: Sistemul de Mesaje Globale (Notificări elegante)**

### **Ce am construit?**
Un sistem de notificări care apar în colțul ecranului, ca pe aplicațiile moderne!

### **Componenta GlobalMessage.vue:**
```html
<template>
  <transition name="slide">
    <div
      v-if="show"
      :class="['global-message', messageType]"
      @click="closeMessage"
    >
      <div class="message-icon">
        <span v-if="messageType === 'success'">✅</span>
        <span v-else-if="messageType === 'error'">❌</span>
        <span v-else-if="messageType === 'warning'">⚠️</span>
        <span v-else>ℹ️</span>
      </div>

      <div class="message-content">
        {{ message }}
      </div>

      <button class="close-btn" @click.stop="closeMessage">✕</button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'GlobalMessage',
  data() {
    return {
      show: false,
      message: '',
      messageType: 'info',
      timeoutId: null
    }
  },
  methods: {
    showMessage(messageData) {
      this.message = messageData.text;
      this.messageType = messageData.type || 'info';
      this.show = true;

      // Auto-hide după 4 secunde
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }

      this.timeoutId = setTimeout(() => {
        this.closeMessage();
      }, 4000);
    },

    closeMessage() {
      this.show = false;
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
        this.timeoutId = null;
      }
    }
  }
}
</script>

<style scoped>
.global-message {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  padding: 15px 20px;
  border-radius: 10px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.global-message:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.global-message.success {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border-left: 5px solid #1e7e34;
}

.global-message.error {
  background: linear-gradient(135deg, #dc3545, #fd7e14);
  color: white;
  border-left: 5px solid #c82333;
}

.global-message.warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  color: #212529;
  border-left: 5px solid #e0a800;
}

.global-message.info {
  background: linear-gradient(135deg, #17a2b8, #6f42c1);
  color: white;
  border-left: 5px solid #138496;
}

.message-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  font-weight: 500;
  line-height: 1.4;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: inherit;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Animații */
.slide-enter-active {
  transition: all 0.4s ease;
}

.slide-leave-active {
  transition: all 0.4s ease;
}

.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
```

### **Integrarea în App.vue:**
```html
<template>
  <div id="app">
    <header>
      <!-- Navigation -->
      <nav class="navbar">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">🏥 Programări Medicale</router-link>
        </div>

        <div class="nav-links">
          <router-link to="/programari" class="nav-link">Programări</router-link>

          <!-- Afisare pentru utilizatori autentificați -->
          <span v-if="currentUser" class="user-info">
            👋 Bună, {{ currentUser.username }}!
            <button @click="logout" class="logout-btn">🚪 Logout</button>
          </span>

          <!-- Afisare pentru vizitatori -->
          <router-link v-else to="/login" class="login-link">
            🔑 Autentificare
          </router-link>
        </div>
      </nav>
    </header>

    <main class="main-content">
      <router-view/>
    </main>

    <!-- Componenta pentru mesaje globale -->
    <GlobalMessage ref="globalMessage" />
  </div>
</template>

<script>
import axios from 'axios';
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
  provide() {
    return {
      showMessage: this.showMessage,
      updateUser: this.handleLogin
    };
  },
  async created() {
    await this.checkAuthStatus();
  },
  methods: {
    async checkAuthStatus() {
      try {
        const response = await axios.get('/users/whoami');
        this.currentUser = response.data;

        // Salvăm în localStorage pentru persistență
        localStorage.setItem('currentUser', JSON.stringify(response.data));
      } catch (error) {
        this.currentUser = null;
        localStorage.removeItem('currentUser');
      }
    },

    handleLogin(user) {
      this.currentUser = user;
      localStorage.setItem('currentUser', JSON.stringify(user));
    },

    async logout() {
      try {
        await axios.post('/logout');
        this.showMessage({
          text: '👋 Ai fost delogat cu succes!',
          type: 'success'
        });
      } catch (error) {
        console.error('Eroare logout:', error);
      } finally {
        this.currentUser = null;
        localStorage.removeItem('currentUser');
        this.$router.push('/');
      }
    },

    showMessage(messageData) {
      if (this.$refs.globalMessage) {
        this.$refs.globalMessage.showMessage(messageData);
      }
    }
  }
}
</script>
```

### **💡 Ce înveți de aici?**
- **Componente Reutilizabile**: Cum creezi componente globale
- **Animații CSS**: Transitions și transforms în Vue
- **Provide/Inject**: Cum împarți funcționalități între componente
- **localStorage**: Persistență date în browser
- **Design patterns**: Componente comunicante

---

## 🎯 **Pasul 6: Editare și Ștergere Programări (CRUD Complet)**

### **Ce am construit?**
Funcționalități complete de management al programărilor - doar pentru utilizatorii autentificați!

### **1. Backend - Endpoints Protejate**

**Endpoint pentru ștergere (`main.py`):**
```python
@app.delete("/programari/{programare_id}")
async def delete_programare(programare_id: int, current_user = Depends(get_current_user)):
    """
    Șterge o programare - DOAR pentru utilizatori autentificați
    """
    try:
        # Căutăm programarea în baza de date
        programare = await Programari.get_or_none(id=programare_id)

        if not programare:
            raise HTTPException(status_code=404, detail="Programarea nu există")

        # Ștergem programarea
        await programare.delete()

        return {
            "status": "success",
            "message": f"Programarea cu ID {programare_id} a fost ștearsă"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la ștergere: {str(e)}")
```

**Endpoint pentru editare (`main.py`):**
```python
@app.put("/programari/{programare_id}")
async def update_programare(programare_id: int, prog: ProgramareIn, current_user = Depends(get_current_user)):
    """
    Actualizează o programare - DOAR pentru utilizatori autentificați
    """
    try:
        # Căutăm programarea în baza de date
        programare = await Programari.get_or_none(id=programare_id)

        if not programare:
            raise HTTPException(status_code=404, detail="Programarea nu există")

        # Pregătim datele pentru actualizare
        update_data = {
            "data": prog.data,
            "ora": prog.ora,
            "nume": prog.nume,
            "prenume": prog.prenume,
            "email": prog.email,
            "telefon": prog.telefon,
            "observatii": prog.observatii,
            "persoana_id": prog.persoana_id,
            "serviciu_id": prog.serviciu_id
        }

        # Actualizăm programarea
        await programare.update_from_dict(update_data)
        await programare.save()

        return {
            "status": "success",
            "message": f"Programarea cu ID {programare_id} a fost actualizată"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la actualizare: {str(e)}")
```

### **2. Frontend - Tabel cu Acțiuni**

**ProgramariTable.vue - Versiune îmbunătățită:**
```html
<template>
  <div class="table-container">
    <h2>📋 Lista Programărilor</h2>

    <div class="table-responsive">
      <table class="appointments-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Ora</th>
            <th>Nume</th>
            <th>Prenume</th>
            <th>Serviciu</th>
            <th>Telefon</th>
            <th>Observații</th>
            <th v-if="currentUser" class="actions-column">🔧 Acțiuni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="programare in programari" :key="programare.id">
            <td>{{ programare.data }}</td>
            <td>{{ programare.ora }}</td>
            <td>{{ programare.nume || '-' }}</td>
            <td>{{ programare.prenume || '-' }}</td>
            <td>{{ getServiciuDescription(programare.serviciu_id) }}</td>
            <td>{{ programare.telefon || '-' }}</td>
            <td>{{ programare.observatii || '-' }}</td>

            <!-- Coloana de acțiuni - vizibilă doar pentru utilizatori autentificați -->
            <td v-if="currentUser" class="actions-cell">
              <button
                @click="editProgramare(programare)"
                class="action-btn edit-btn"
                title="Editează programarea"
              >
                ✏️ Editare
              </button>

              <button
                @click="deleteProgramare(programare.id)"
                class="action-btn delete-btn"
                title="Șterge programarea"
              >
                🗑️ Ștergere
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mesaj dacă nu există programări -->
    <div v-if="programari.length === 0" class="no-data">
      <p>📭 Nu există programări în sistem</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgramariTable',
  inject: ['showMessage'],
  data() {
    return {
      currentUser: null,
      programari: [],
      servicii: []
    }
  },
  async created() {
    await this.loadData();
    await this.checkAuthStatus();
  },
  methods: {
    async loadData() {
      try {
        // Încărcăm programările
        const programariResponse = await axios.get('/programari');
        this.programari = programariResponse.data;

        // Încărcăm serviciile pentru afișare
        const serviciiResponse = await axios.get('/servicii');
        this.servicii = serviciiResponse.data;

      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error);
        this.showMessage({
          text: 'Eroare la încărcarea programărilor',
          type: 'error'
        });
      }
    },

    async checkAuthStatus() {
      try {
        const response = await axios.get('/users/whoami');
        this.currentUser = response.data;
      } catch (error) {
        this.currentUser = null;
      }
    },

    getServiciuDescription(serviciuId) {
      const serviciu = this.servicii.find(s => s.id === serviciuId);
      return serviciu ? serviciu.descriere : 'N/A';
    },

    async deleteProgramare(programareId) {
      // Confirmare dialog
      const confirmed = confirm('🤔 Ești sigur că vrei să ștergi această programare?');

      if (!confirmed) {
        return;
      }

      try {
        // Trimitere request de ștergere
        await axios.delete(`/programari/${programareId}`);

        // Afișare mesaj succes
        this.showMessage({
          text: '✅ Programarea a fost ștearsă cu succes!',
          type: 'success'
        });

        // Reîncărcăm lista
        await this.loadData();

      } catch (error) {
        console.error('Eroare la ștergere:', error);
        const errorMsg = error.response?.data?.detail || 'Eroare la ștergerea programării';

        this.showMessage({
          text: `❌ ${errorMsg}`,
          type: 'error'
        });
      }
    },

    editProgramare(programare) {
      // Navigăm către pagina de editare cu datele programării
      this.$router.push({
        name: 'edit-programare',
        params: { id: programare.id },
        query: {
          data: JSON.stringify(programare),
          servicii: JSON.stringify(this.servicii)
        }
      });
    }
  }
}
</script>

<style scoped>
.table-container {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.table-responsive {
  overflow-x: auto;
}

.appointments-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.appointments-table th,
.appointments-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.appointments-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  position: sticky;
  top: 0;
}

.appointments-table tr:hover {
  background-color: #f8f9fa;
}

.actions-column {
  min-width: 200px;
}

.actions-cell {
  white-space: nowrap;
}

.action-btn {
  padding: 6px 12px;
  margin-right: 8px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.edit-btn:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
  transform: translateY(-1px);
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-style: italic;
}

/* Responsive pentru telefoane */
@media (max-width: 768px) {
  .actions-cell {
    display: block;
    margin-top: 10px;
  }

  .action-btn {
    display: block;
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>
```

### **3. Pagina de Editare Completă**

**EditProgramareView.vue:**
```html
<template>
  <div class="edit-container">
    <div class="edit-card">
      <div class="edit-header">
        <h1>✏️ Editare Programare</h1>
        <div class="programare-id">ID: {{ $route.params.id }}</div>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Se încarcă datele programării...</p>
      </div>

      <form v-else @submit.prevent="updateProgramare" class="edit-form">
        <!-- Informații persoană -->
        <div class="form-section">
          <h3>👤 Informații Persoană</h3>

          <div class="form-row">
            <div class="form-group">
              <label>Nume*</label>
              <input
                v-model="programare.nume"
                type="text"
                required
                placeholder="Ex: Popescu"
              >
            </div>

            <div class="form-group">
              <label>Prenume*</label>
              <input
                v-model="programare.prenume"
                type="text"
                required
                placeholder="Ex: Ion"
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>📧 Email</label>
              <input
                v-model="programare.email"
                type="email"
                placeholder="ex: ion.popescu@email.com"
              >
            </div>

            <div class="form-group">
              <label>📱 Telefon</label>
              <input
                v-model="programare.telefon"
                type="tel"
                placeholder="ex: 0723123456"
              >
            </div>
          </div>
        </div>

        <!-- Programare -->
        <div class="form-section">
          <h3>📅 Detalii Programare</h3>

          <div class="form-row">
            <div class="form-group">
              <label>Data*</label>
              <input
                v-model="programare.data"
                type="date"
                required
                :min="todayDate"
              >
            </div>

            <div class="form-group">
              <label>Ora*</label>
              <input
                v-model="programare.ora"
                type="time"
                required
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Persoană</label>
              <select v-model="programare.persoana_id">
                <option value="">Selectează persoana</option>
                <option
                  v-for="persoana in persoane"
                  :key="persoana.id"
                  :value="persoana.id"
                >
                  {{ persoana.nume }} {{ persoana.prenume }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Serviciu*</label>
              <select v-model="programare.serviciu_id" required>
                <option value="">Selectează serviciul</option>
                <option
                  v-for="serviciu in servicii"
                  :key="serviciu.id"
                  :value="serviciu.id"
                >
                  {{ serviciu.descriere }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Observații -->
        <div class="form-section">
          <h3>📝 Observații</h3>
          <div class="form-group">
            <label>Observații adiționale</label>
            <textarea
              v-model="programare.observatii"
              rows="3"
              placeholder="Note sau informații suplimentare..."
            ></textarea>
          </div>
        </div>

        <!-- Butoane acțiune -->
        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="saving">
            {{ saving ? 'Se salvează...' : '💾 Salvează modificările' }}
          </button>

          <button
            type="button"
            @click="goBack"
            class="cancel-btn"
          >
            ❌ Anulează
          </button>
        </div>
      </form>

      <!-- Mesaj de confirmare salvare -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'EditProgramareView',
  inject: ['showMessage'],
  data() {
    return {
      loading: true,
      saving: false,
      programare: {},
      persoane: [],
      servicii: [],
      message: '',
      messageType: ''
    }
  },
  computed: {
    todayDate() {
      return new Date().toISOString().split('T')[0];
    }
  },
  async created() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      try {
        this.loading = true;

        // Încărcăm datele din query parameters
        if (this.$route.query.data) {
          this.programare = JSON.parse(this.$route.query.data);
        }

        if (this.$route.query.servicii) {
          this.servicii = JSON.parse(this.$route.query.servicii);
        } else {
          // Dacă nu avem servicii în query, le încărcăm din API
          const serviciiResponse = await axios.get('/servicii');
          this.servicii = serviciiResponse.data;
        }

        // Încărcăm persoanele
        const persoaneResponse = await axios.get('/persoane');
        this.persoane = persoaneResponse.data;

      } catch (error) {
        console.error('Eroare la încărcare date:', error);
        this.showMessage({
          text: 'Eroare la încărcarea datelor',
          type: 'error'
        });
      } finally {
        this.loading = false;
      }
    },

    async updateProgramare() {
      this.saving = true;
      this.clearMessages();

      // Validare
      if (!this.programare.data || !this.programare.ora) {
        this.showMessage({
          text: 'Data și ora sunt obligatorii!',
          type: 'error'
        });
        this.saving = false;
        return;
      }

      try {
        const programareId = this.$route.params.id;

        // Trimitere date către backend
        const response = await axios.put(`/programari/${programareId}`, this.programare);

        // Afișare mesaj succes
        this.showMessage({
          text: '✅ Programarea a fost actualizată cu succes!',
          type: 'success'
        });

        // Redirecționare după 2 secunde
        setTimeout(() => {
          this.$router.push('/programari');
        }, 2000);

      } catch (error) {
        console.error('Eroare actualizare:', error);
        const errorMsg = error.response?.data?.detail || 'Eroare la actualizarea programării';

        this.showMessage({
          text: `❌ ${errorMsg}`,
          type: 'error'
        });
      } finally {
        this.saving = false;
      }
    },

    goBack() {
      this.$router.push('/programari');
    },

    showMessage(messageData) {
      // Injectăm mesajul în sistemul global
      if (typeof this.showMessage === 'function') {
        this.showMessage(messageData);
      } else {
        this.message = messageData.text;
        this.messageType = messageData.type;
      }
    },

    clearMessages() {
      this.message = '';
      this.messageType = '';
    }
  }
}
</script>

<style scoped>
.edit-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.edit-card {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 15px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.edit-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-header h1 {
  margin: 0;
  font-size: 24px;
}

.programare-id {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.edit-form {
  padding: 30px;
}

.form-section {
  margin-bottom: 35px;
}

.form-section h3 {
  color: #495057;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 18px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #e9ecef;
}

.submit-btn,
.cancel-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px;
}

.submit-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(40, 167, 69, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background: #545b62;
  transform: translateY(-2px);
}

.message {
  padding: 15px;
  margin: 20px 30px;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Responsive */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .submit-btn,
  .cancel-btn {
    width: 100%;
  }

  .edit-header {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
}
</style>
```

### **💡 Ce înveți de aici?**
- **CRUD Operations**: Create, Read, Update, Delete complete
- **Protected Routes**: Securitate endpoint-uri cu JWT
- **Formulare Complexe**: Validare și structură date
- **Responsive Design**: Design adaptiv pentru mobil
- **User Experience**: Confirmări dialog, loading states
- **Data Validation**: Validare frontend și backend
- **Navigation Management**: Routing cu parametri

---

## 🎉 **Rezumat Final - Ce am construit împreună!**

### **Aplicația Completă Conține:**

1. **🔐 Sistem de Autentificare Complet**
   - Înregistrare utilizatori noi
   - Login cu parole criptate
   - Token-uri JWT securizate
   - Logout și management sesiuni

2. **💾 Management Baze de Date**
   - Persistență date volum Docker
   - Relații între tabele
   - Structură organizațională

3. **🎨 Interfață Modernă Vue.js**
   - Design responsive și atractiv
   - Componente reutilizabile
   - Sistem de notificări elegante
   - Navigație fluidă

4. **🔧 Funcționalități Complete**
   - CRUD pentru programări
   - Editare și ștergere protejate
   - Validare date în timp real
   - Mesaje de succes/eroare

5. **🛡️ Securitate**
   - Criptare parole
   - Cookie-uri securizate
   - Protecție endpoint-uri
   - Validare input

### **📚 Tehnologii Învățate:**

- **Backend**: Python, FastAPI, Tortoise ORM, JWT, bcrypt
- **Frontend**: Vue.js 3, Vue Router, Axios, CSS3
- **Baze de date**: SQLite, modele relaționale
- **DevOps**: Docker, Docker Compose, volume persistente
- **Security**: Authentication, authorization, password hashing
- **Best Practices**: Code organization, error handling, validation

### **🚀 Următorii Pași Posibili:**

1. **Funcționalități Avansate**:
   - Email notifications
   - Calendar integration
   - SMS reminders
   - Payment processing

2. **Îmbunătățiri Tehnice**:
   - Testing (unit, integration)
   - Caching
   - Performance optimization
   - Database migrations

3. **Scalabilitate**:
   - Cloud deployment
   - Load balancing
   - Database scaling
   - Microservices architecture

---

## 🎓 **Felicitări!**

Ai parcurs un proces complet de dezvoltare web modernă, de la baza de date la interfața utilizator. Ai învățat:

- **Arhitectura MVC**: Separarea responsabilităților
- **RESTful APIs**: Design endpoints moderne
- **Frontend Modern**: Componente și reactivitate
- **Securitate Web**: Best practices actuale
- **DevOps**: Containerizare și deployment
- **Full-Stack Development**: Integrare completă frontend-backend

**Continuă să exersezi și să construiești proiecte noi!** 🚀