<template>
  <div class="select-job">
    <div class="container">
      <h2>Selectați categoria dorită</h2>

      <div v-if="loading" class="loading">
        Se încarcă categoriile...
      </div>

      <div v-else-if="jobs.length === 0" class="no-jobs">
        <p>Nu există categorii disponibile.</p>
      </div>

      <div v-else class="jobs-grid">
        <div
          v-for="job in jobs"
          :key="job.id"
          @click="selectJob(job)"
          class="job-card"
        >
          <h3>{{ job.nume }}</h3>
          <div class="job-icon">📋</div>
        </div>
      </div>

      <div class="actions">
        <button @click="goBack" class="btn-back">
          Înapoi
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SelectJobView',
  inject: ['showMessage'],
  data() {
    return {
      jobs: [],
      loading: true
    };
  },
  async mounted() {
    await this.loadJobs();
  },
  methods: {
    async loadJobs() {
      try {
        const response = await axios.get('/jobs');
        this.jobs = response.data;
        console.log('Jobs loaded:', this.jobs);
      } catch (error) {
        console.error('Error loading jobs:', error);
        this.showMessage({
          text: 'Eroare la încărcarea categoriilor!',
          type: 'error'
        });
      } finally {
        this.loading = false;
      }
    },
    selectJob(job) {
      console.log('Selected job:', job);
      // Navigate to programari page with job_id
      this.$router.push({
        name: 'programari',
        query: { job_id: job.id, job_name: job.nume }
      });
    },
    goBack() {
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.select-job {
  min-height: 80vh;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.loading, .no-jobs {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #666;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.job-card {
  background: white;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #42b983;
  background: #f8fdfb;
}

.job-card h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
}

.job-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.actions {
  text-align: center;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-back:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .jobs-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  h2 {
    font-size: 1.5rem;
  }

  .job-card {
    padding: 20px 15px;
  }
}
</style>