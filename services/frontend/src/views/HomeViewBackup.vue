<template>
  <div class="home">
    <!-- Iconițe Jobs - Vizibile tot timpul -->
    <div class="hero-section">
      <h1>Sistem de Programări</h1>
      <p>Selectați o categorie</p>

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
          :class="{ 'job-card-active': selectedJobId === job.id }"
        >
          <h3>{{ job.nume }}</h3>
          <div class="job-icon">📋</div>
        </div>
      </div>
    </div>

    <!-- Secțiunea Formular + Tabel - Apare sub iconițe când e selectat un job -->
    <div v-if="selectedJob" class="content-section">
      <div class="header">
        <h2>{{ selectedJob.nume }}</h2>
      </div>

      <!-- Formular -->
      <div class="form-section">
        <h3>Adaugă programare nouă</h3>
        <div class="form">
          <input v-model="newProgramare.nume" placeholder="Nume" />
          <input v-model="newProgramare.prenume" placeholder="Prenume" />
          <input v-model="newProgramare.email" placeholder="Email" />
          <input v-model="newProgramare.telefon" placeholder="Telefon" />
          <input v-model="newProgramare.data" type="date" placeholder="Data" />
          <input v-model="newProgramare.ora" type="time" placeholder="Ora" />
          <textarea v-model="newProgramare.observatii" placeholder="Observații"></textarea>

          <!-- Select Persoană -->
          <label>Persoană:</label>
          <select v-model.number="newProgramare.persoana_id">
            <option disabled value="">Selectează o persoană</option>
            <option v-for="p in persoane" :key="p.id" :value="p.id">
              {{ p.nume }} {{ p.prenume }}
            </option>
          </select>

          <!-- Select Servicii -->
          <label>Servicii:</label>
          <select v-model.number="newProgramare.serviciu_id">
            <option disabled value="">Selectează un serviciu</option>
            <option v-for="s in servicii" :key="s.id" :value="s.id">
              {{ s.descriere }}
            </option>
          </select>

          <div class="form-actions">
            <button @click="adaugaProgramare" class="btn-submit">
              Adaugă programare
            </button>
          </div>
        </div>
      </div>

      <!-- Tabel Programări -->
      <div class="table-section">
        <h3>Programări existente</h3>
        <ProgramariTable :refresh="refreshTable" :jobId="selectedJobId" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ProgramariTable from '@/components/ProgramariTable.vue';

export default {
  name: 'HomeView',
  components: { ProgramariTable },
  inject: ['showMessage'],

  data() {
    return {
      jobs: [],
      selectedJob: null,
      selectedJobId: null,
      loading: true,

      persoane: [],
      servicii: [],

      newProgramare: {
        nume: '',
        prenume: '',
        email: '',
        telefon: '',
        data: '',
        ora: '',
        observatii: '',
        persoana_id: '',
        serviciu_id: ''
      },

      refreshTable: false
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

    async selectJob(job) {
      this.selectedJob = job;
      this.selectedJobId = job.id;
      await this.loadFormData();
    },

    async loadFormData() {
      try {
        const [persoaneRes, serviciiRes] = await Promise.all([
          axios.get(`/persoane?job_id=${this.selectedJobId}`),
          axios.get(`/servicii?job_id=${this.selectedJobId}`)
        ]);

        this.persoane = persoaneRes.data;
        this.servicii = serviciiRes.data;

        console.log('Loaded persoane:', this.persoane);
        console.log('Loaded servicii:', this.servicii);

        this.refreshTable = !this.refreshTable;
      } catch (error) {
        console.error('Error loading form data:', error);
        this.showMessage({
          text: 'Eroare la încărcarea datelor!',
          type: 'error'
        });
      }
    },

    async adaugaProgramare() {
      try {
        if (!this.newProgramare.data || !this.newProgramare.ora) {
          this.showMessage({
            text: 'Vă rugăm completați data și ora!',
            type: 'error'
          });
          return;
        }

        if (!this.newProgramare.persoana_id || !this.newProgramare.serviciu_id) {
          this.showMessage({
            text: 'Vă rugăm selectați persoana și serviciul!',
            type: 'error'
          });
          return;
        }

        const payload = {
          data: this.newProgramare.data,
          ora: this.newProgramare.ora,
          nume: this.newProgramare.nume || null,
          prenume: this.newProgramare.prenume || null,
          email: this.newProgramare.email || null,
          telefon: this.newProgramare.telefon || null,
          observatii: this.newProgramare.observatii || null,
          persoana_id: this.newProgramare.persoana_id,
          serviciu_id: this.newProgramare.serviciu_id
        };

        await axios.post('/programari', payload);

        this.showMessage({
          text: 'Programare adăugată cu succes!',
          type: 'success'
        });

        this.resetForm();
        this.refreshTable = !this.refreshTable;

      } catch (err) {
        console.error('Error:', err);
        const errorMsg = err.response?.data?.detail || 'Eroare la adăugare!';
        this.showMessage({ text: errorMsg, type: 'error' });
      }
    },

    resetForm() {
      this.newProgramare = {
        nume: '',
        prenume: '',
        email: '',
        telefon: '',
        data: '',
        ora: '',
        observatii: '',
        persoana_id: '',
        serviciu_id: ''
      };
    }
  }
};
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1, h2, h3 {
  color: #2c3e50;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 40px 20px;
}

.loading,
.no-jobs {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1rem;
}

/* Jobs Grid */
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

.job-card-active {
  border-color: #42b983;
  background: linear-gradient(135deg, #f8fdfb, #e8f8f2);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.3);
  transform: scale(1.05);
}

.job-icon {
  font-size: 3rem;
  margin-top: 10px;
}

/* Content Section */
.content-section {
  padding: 30px 20px;
  border-top: 2px solid #e1e8ed;
  margin-top: 30px;
}

.header {
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
}

/* Form Section */
.form-section {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 40px;
}

.form label {
  display: block;
  margin-top: 15px;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.form input,
.form textarea,
.form select {
  display: block;
  width: 100%;
  max-width: 500px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form input:focus,
.form textarea:focus,
.form select:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.form textarea {
  resize: vertical;
  font-family: inherit;
  min-height: 80px;
}

.form-actions {
  margin-top: 25px;
}

.btn-submit {
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3);
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.4);
}

/* Table Section */
.table-section {
  margin-top: 40px;
}

/* Responsive */
@media (max-width: 768px) {
  .jobs-grid {
    grid-template-columns: 1fr;
  }

  .form input,
  .form textarea,
  .form select {
    max-width: 100%;
  }
}
</style>
