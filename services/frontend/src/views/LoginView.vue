<template>
  <div class="login">
    <div class="login-container">
      <h2>{{ isRegister ? 'Înregistrare' : 'Autentificare' }}</h2>

      <!-- Formular de Login -->
      <form v-if="!isRegister" @submit.prevent="login">
        <div class="form-group">
          <label for="username">Utilizator:</label>
          <input
            type="text"
            id="username"
            v-model="loginForm.username"
            required
            placeholder="Nume utilizator"
          />
        </div>

        <div class="form-group">
          <label for="password">Parolă:</label>
          <input
            type="password"
            id="password"
            v-model="loginForm.password"
            required
            placeholder="Parolă"
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Se procesează...' : 'Autentificare' }}
        </button>

        <p class="switch-form">
          Nu ai cont?
          <a href="#" @click.prevent="isRegister = true">Înregistrează-te</a>
        </p>
      </form>

      <!-- Formular de Înregistrare -->
      <form v-else @submit.prevent="register">
        <div class="form-group">
          <label for="reg-username">Utilizator:</label>
          <input
            type="text"
            id="reg-username"
            v-model="registerForm.username"
            required
            placeholder="Nume utilizator"
          />
        </div>

        <div class="form-group">
          <label for="reg-email">Email:</label>
          <input
            type="email"
            id="reg-email"
            v-model="registerForm.email"
            required
            placeholder="Email"
          />
        </div>

        <div class="form-group">
          <label for="reg-password">Parolă:</label>
          <input
            type="password"
            id="reg-password"
            v-model="registerForm.password"
            required
            placeholder="Parolă"
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label for="reg-confirm-password">Confirmă parola:</label>
          <input
            type="password"
            id="reg-confirm-password"
            v-model="registerForm.confirmPassword"
            required
            placeholder="Confirmă parola"
          />
        </div>

        <button type="submit" :disabled="loading || !passwordsMatch">
          {{ loading ? 'Se procesează...' : 'Înregistrare' }}
        </button>

        <p class="switch-form">
          Ai deja cont?
          <a href="#" @click.prevent="isRegister = false">Autentifică-te</a>
        </p>
      </form>

      <!-- Mesaje de eroare/succes -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>

      </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginView',
  inject: ['showMessage', 'updateUser'],
  data() {
    return {
      isRegister: false,
      loading: false,
      message: '',
      messageType: '',
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    };
  },
  computed: {
    passwordsMatch() {
      return this.registerForm.password === this.registerForm.confirmPassword;
    }
  },
  methods: {
    async login() {
      this.loading = true;
      this.message = '';

      try {
        // Folosim form-data conform așteptărilor backend-ului
        const formData = new FormData();
        formData.append('username', this.loginForm.username);
        formData.append('password', this.loginForm.password);

        const response = await axios.post('/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        this.showMessage('Autentificare reușită!', 'success');

        // Get user info after successful login
        try {
          const userResponse = await axios.get('/users/whoami');
          const user = userResponse.data;

          // Update user state in parent component
          this.updateUser(user);

          // Show success message using injected method
          this.showMessage({
            text: `Bun venit, ${user.username}!`,
            type: 'success'
          });

          // Redirect către programari după login reușit
          setTimeout(() => {
            this.$router.push('/programari');
          }, 1000);
        } catch (userError) {
          console.error('Error getting user info:', userError);
          // Still redirect even if we can't get user info
          setTimeout(() => {
            this.$router.push('/programari');
          }, 1000);
        }

      } catch (error) {
        console.error('Eroare login:', error);
        this.showMessage(
          error.response?.data?.detail || 'Eroare la autentificare',
          'error'
        );
      } finally {
        this.loading = false;
      }
    },

    async register() {
      if (!this.passwordsMatch) {
        this.showMessage('Parolele nu corespund!', 'error');
        return;
      }

      this.loading = true;
      this.message = '';

      try {
        const { confirmPassword, ...userData } = this.registerForm;

        await axios.post('/register', userData);

        this.showMessage('Înregistrare reușită! Te poți autentifica acum.', 'success');

        // Reset form și switch la login
        this.registerForm = {
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        };

        setTimeout(() => {
          this.isRegister = false;
        }, 2000);

      } catch (error) {
        console.error('Eroare înregistrare:', error);
        this.showMessage(
          error.response?.data?.detail || 'Eroare la înregistrare',
          'error'
        );
      } finally {
        this.loading = false;
      }
    },

    showMessage(text, type) {
      this.message = text;
      this.messageType = type;

      // Auto-hide mesaj după 5 secunde
      setTimeout(() => {
        this.message = '';
      }, 5000);
    },

    }
};
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

button {
  width: 100%;
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.switch-form {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

.switch-form a {
  color: #007bff;
  text-decoration: none;
}

.switch-form a:hover {
  text-decoration: underline;
}

.message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 4px;
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
</style>