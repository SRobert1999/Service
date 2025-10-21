<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/programari">Programări</router-link> |

      <!-- Authentication UI -->
      <span v-if="currentUser" class="auth-info">
        Bună, {{ currentUser.username }}!
        <a href="#" @click.prevent="logout" class="logout-link">Logout</a>
      </span>

      <router-link v-else to="/login">Autentificare</router-link>
    </nav>

    <div class="main container">
      <router-view />
    </div>

    <!-- Global message component -->
    <GlobalMessage ref="globalMessage" />
  </div>
</template>

<script>
import axios from 'axios';
import GlobalMessage from '@/components/GlobalMessage.vue';

export default {
  name: 'App',
  components: {
    GlobalMessage
  },
  data() {
    return {
      currentUser: null,
      messageEmitter: null
    };
  },
  provide() {
    return {
      // Provide the message emitter to child components
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
        // Store in localStorage for persistence
        localStorage.setItem('currentUser', JSON.stringify(response.data));
      } catch (error) {
        // User is not authenticated
        this.currentUser = null;
        localStorage.removeItem('currentUser');
      }
    },

    handleLogin(user) {
      this.currentUser = user;
      localStorage.setItem('currentUser', JSON.stringify(user));
    },

    handleLogout() {
      this.currentUser = null;
      localStorage.removeItem('currentUser');
    },

    showMessage(messageData) {
      // Emit to GlobalMessage component through ref
      if (this.$refs.globalMessage) {
        this.$refs.globalMessage.showMessage(messageData);
      }
    },

    async logout() {
      try {
        await axios.post('/logout');
        this.handleLogout();
        // Redirect to home page
        this.$router.push('/');

        // Show success message
        this.showMessage({
          text: 'Ai fost delogat cu succes!',
          type: 'success'
        });
      } catch (error) {
        console.error('Logout error:', error);
        // Still clear local state even if server call fails
        this.handleLogout();
      }
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  margin-bottom: 20px;
}

nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #42b983;
}

nav a.router-link-active {
  font-weight: bold;
}

.auth-info {
  margin-left: 15px;
  font-size: 0.9rem;
  color: #333;
}

.logout-link {
  margin-left: 10px;
  color: #dc3545;
  text-decoration: none;
  font-weight: 500;
}

.logout-link:hover {
  text-decoration: underline;
  color: #c82333;
}
</style>