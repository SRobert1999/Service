<template>
  <div class="home">
    <div class="hero-section">
      <h1>Sistem de Programări</h1>
      <p>Bine ați venit la sistemul nostru de programări online</p>

      <div class="actions">
        <button @click="goToProgramare" class="btn-primary">
          Fă o programare
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goToProgramare() {
      this.$router.push('/select-job');
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-section {
  text-align: center;
  padding: 40px;
  max-width: 600px;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 20px;
  font-weight: 300;
}

p {
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 40px;
  line-height: 1.6;
}

.actions {
  margin-top: 40px;
}

.btn-primary {
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  border: none;
  padding: 15px 40px;
  font-size: 1.1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3);
  font-weight: 500;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.4);
  background: linear-gradient(135deg, #3aa876, #2d8f62);
}

.btn-primary:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }

  p {
    font-size: 1rem;
  }

  .btn-primary {
    padding: 12px 30px;
    font-size: 1rem;
  }
}
</style>
