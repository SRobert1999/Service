<template>
  <div class="home">
    <!-- ETAPA 1: Iconițe Jobs - Vizibile permanent -->
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

    <!-- ETAPA 2: Selecție Persoană - Apare după alegerea job-ului -->
    <div v-if="selectedJob && !selectedPersoana" class="persoane-section">
      <h2>Selectați persoana pentru {{ selectedJob.nume }}</h2>
      
      <div v-if="loadingPersoane" class="loading">
        Se încarcă persoanele...
      </div>
      
      <div v-else-if="persoane.length === 0" class="no-data">
        <p>Nu există persoane disponibile pentru acest serviciu.</p>
      </div>
      
      <div v-else class="persoane-grid">
        <div
          v-for="persoana in persoane"
          :key="persoana.id"
          @click="selectPersoana(persoana)"
          class="persoana-card"
        >
          <div class="persoana-avatar">👤</div>
          <h3>{{ persoana.nume }} {{ persoana.prenume }}</h3>
          <button class="btn-select">Selectează</button>
        </div>
      </div>
      
      <button @click="backToJobs" class="btn-back">
        ← Înapoi la categorii
      </button>
    </div>

    <!-- ETAPA 3: Formular + Tabel - Apare după alegerea persoanei -->
    <div v-if="selectedPersoana" class="content-section">
      <div class="header">
        <h2>
          Programare pentru {{ selectedPersoana.nume }} {{ selectedPersoana.prenume }}
          <span class="subtitle">({{ selectedJob.nume }})</span>
        </h2>
        <button @click="backToPersoane" class="btn-change">
          Schimbă persoana
        </button>
      </div>

      <!-- Formular -->
      <div class="form-section">
        <h3>Adaugă programare nouă</h3>
        <div class="form">
          <!-- Date client -->
          <label>Nume client:</label>
          <input v-model="newProgramare.nume" placeholder="Nume" />
          
          <label>Prenume client:</label>
          <input v-model="newProgramare.prenume" placeholder="Prenume" />
          
          <label>Email:</label>
          <input v-model="newProgramare.email" type="email" placeholder="Email" />
          
          <label>Telefon:</label>
          <input v-model="newProgramare.telefon" placeholder="+40712345678" />
          
          <!-- Data cu V-Calendar -->
          <label>Data programarii:</label>
          <div class="calendar-wrapper">
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
            
            <!-- Legendă -->
            <div class="legend">
              <div class="legend-item">
                <span class="dot dot-today"></span> Azi
              </div>
              <div class="legend-item">
                <span class="dot dot-available"></span> Disponibil
              </div>
              <div class="legend-item">
                <span class="dot dot-partial"></span> Parțial ocupat
              </div>
              <div class="legend-item">
                <span class="dot dot-full"></span> Complet ocupat
              </div>
            </div>
          </div>
          
          <!-- Ora -->
          <label>Ora programării:</label>
          <input 
            v-model="newProgramare.ora" 
            type="time"
            step="1800"
          />
          
          <!-- Serviciu -->
          <label>Serviciu:</label>
          <select v-model.number="newProgramare.serviciu_id">
            <option disabled value="">Selectează un serviciu</option>
            <option 
              v-for="s in servicii" 
              :key="s.id" 
              :value="s.id"
            >
              {{ s.descriere }}
            </option>
          </select>
          
          <!-- Observații -->
          <label>Observații:</label>
          <textarea 
            v-model="newProgramare.observatii" 
            placeholder="Observații opționale"
            rows="4"
          ></textarea>

          <div class="form-actions">
            <button @click="adaugaProgramare" class="btn-submit">
              Adaugă programare
            </button>
            <button @click="resetForm" class="btn-reset">
              Resetează formular
            </button>
          </div>
        </div>
      </div>

      <!-- Tabel Programări -->
      <div class="table-section">
        <h3>Programări existente pentru {{ selectedPersoana.nume }}</h3>
        <ProgramariTable 
          :refresh="refreshTable" 
          :jobId="selectedJobId"
          :persoanaId="selectedPersoana.id"
        />
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
      // ETAPA 1: Jobs
      jobs: [],
      selectedJob: null,
      selectedJobId: null,
      loading: true,
      
      // ETAPA 2: Persoane
      persoane: [],
      selectedPersoana: null,
      loadingPersoane: false,
      
      // ETAPA 3: Formular
      servicii: [],
      programariExistente: [],
      loadingProgramari: false,
      
      newProgramare: {
        nume: '',
        prenume: '',
        email: '',
        telefon: '',
        data: null,  // V-Calendar folosește Date object
        ora: '',
        observatii: '',
        persoana_id: '',
        serviciu_id: ''
      },
      
      refreshTable: false,
      capacitateMaxima: 8  // 8 programari pe zi
    };
  },
  
  computed: {
    // Data minimă = azi (nu poți rezerva în trecut)
    minDate() {
      return new Date();
    },
    
    // Atribute pentru calendar (culori, dots)
    calendarAttributes() {
      const attrs = [];
      
      // 1. Marchează azi cu albastru
      attrs.push({
        key: 'today',
        highlight: {
          color: 'blue',
          fillMode: 'light'
        },
        dates: new Date()
      });
      
      // 2. Marchează zilele cu programări
      const programariPeZi = this.programariExistente.reduce((acc, p) => {
        // Convertește data din string YYYY-MM-DD în Date
        const dataStr = typeof p.data === 'string' ? p.data : p.data.toString();
        acc[dataStr] = (acc[dataStr] || 0) + 1;
        return acc;
      }, {});
      
      Object.keys(programariPeZi).forEach(dataStr => {
        const numarProgramari = programariPeZi[dataStr];
        const data = new Date(dataStr);
        
        if (numarProgramari >= this.capacitateMaxima) {
          // Zi complet ocupată - dot roșu
          attrs.push({
            key: `full-${dataStr}`,
            dot: {
              color: 'red',
              class: 'dot-full'
            },
            dates: data
          });
        } else if (numarProgramari > this.capacitateMaxima / 2) {
          // Zi parțial ocupată - dot portocaliu
          attrs.push({
            key: `partial-${dataStr}`,
            dot: {
              color: 'orange',
              class: 'dot-partial'
            },
            dates: data
          });
        } else {
          // Zi disponibilă - dot verde
          attrs.push({
            key: `available-${dataStr}`,
            dot: {
              color: 'green',
              class: 'dot-available'
            },
            dates: data
          });
        }
      });
      
      return attrs;
    },
    
    // Zilele complet disable (nu pot fi selectate)
    disabledDates() {
      const disabled = [];
      
      // 1. Disable zilele complet ocupate
      const programariPeZi = this.programariExistente.reduce((acc, p) => {
        const dataStr = typeof p.data === 'string' ? p.data : p.data.toString();
        acc[dataStr] = (acc[dataStr] || 0) + 1;
        return acc;
      }, {});
      
      Object.keys(programariPeZi).forEach(dataStr => {
        if (programariPeZi[dataStr] >= this.capacitateMaxima) {
          disabled.push(new Date(dataStr));
        }
      });
      
      return disabled;
    }
  },
  
  async mounted() {
    await this.loadJobs();
  },
  
  watch: {
    // Reîncarcă programările când se schimbă persoana
    selectedPersoana(newVal) {
      if (newVal) {
        this.loadProgramari();
      }
    }
  },
  
  methods: {
    // ========== ETAPA 1: JOBS ==========
    
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
      this.selectedJob = job;
      this.selectedJobId = job.id;
      this.selectedPersoana = null;
      this.loadPersoane();
    },
    
    backToJobs() {
      this.selectedJob = null;
      this.selectedJobId = null;
      this.selectedPersoana = null;
      this.persoane = [];
      this.resetForm();
    },
    
    // ========== ETAPA 2: PERSOANE ==========
    
    async loadPersoane() {
      this.loadingPersoane = true;
      try {
        const url = `/persoane?job_id=${this.selectedJobId}`;
        const response = await axios.get(url);
        this.persoane = response.data;
        console.log(`Loaded ${this.persoane.length} persoane for job_id:`, this.selectedJobId);
      } catch (error) {
        console.error('Error loading persoane:', error);
        this.showMessage({
          text: 'Eroare la încărcarea persoanelor!',
          type: 'error'
        });
      } finally {
        this.loadingPersoane = false;
      }
    },
    
    selectPersoana(persoana) {
      this.selectedPersoana = persoana;
      this.newProgramare.persoana_id = persoana.id;
      this.loadServicii();
      this.loadProgramari();
      this.refreshTable = !this.refreshTable;
    },
    
    backToPersoane() {
      this.selectedPersoana = null;
      this.programariExistente = [];
      this.resetForm();
    },
    
    // ========== ETAPA 3: FORMULAR ==========
    
    async loadServicii() {
      try {
        const url = `/servicii?job_id=${this.selectedJobId}`;
        const response = await axios.get(url);
        this.servicii = response.data;
        console.log(`Loaded ${this.servicii.length} servicii for job_id:`, this.selectedJobId);
      } catch (error) {
        console.error('Error loading servicii:', error);
        this.showMessage({
          text: 'Eroare la încărcarea serviciilor!',
          type: 'error'
        });
      }
    },
    
    async loadProgramari() {
      if (!this.selectedPersoana) return;
      
      this.loadingProgramari = true;
      try {
        const url = `/programari?persoana_id=${this.selectedPersoana.id}`;
        const response = await axios.get(url);
        this.programariExistente = response.data;
        console.log(`Loaded ${this.programariExistente.length} programări for persoana:`, this.selectedPersoana.id);
      } catch (error) {
        console.error('Error loading programari:', error);
      } finally {
        this.loadingProgramari = false;
      }
    },
    
    async adaugaProgramare() {
      try {
        // Validare
        if (!this.newProgramare.data || !this.newProgramare.ora) {
          this.showMessage({
            text: 'Vă rugăm completați data și ora!',
            type: 'error'
          });
          return;
        }
        
        if (!this.newProgramare.serviciu_id) {
          this.showMessage({
            text: 'Vă rugăm selectați un serviciu!',
            type: 'error'
          });
          return;
        }
        
        // Convertește Date object în string YYYY-MM-DD
        const dataStr = this.newProgramare.data instanceof Date
          ? this.newProgramare.data.toISOString().split('T')[0]
          : this.newProgramare.data;
        
        const payload = {
          data: dataStr,
          ora: this.newProgramare.ora,
          nume: this.newProgramare.nume || null,
          prenume: this.newProgramare.prenume || null,
          email: this.newProgramare.email || null,
          telefon: this.newProgramare.telefon || null,
          observatii: this.newProgramare.observatii || null,
          persoana_id: this.selectedPersoana.id,
          serviciu_id: this.newProgramare.serviciu_id
        };
        
        await axios.post('/programari', payload);
        
        this.showMessage({ 
          text: 'Programare adăugată cu succes!', 
          type: 'success' 
        });
        
        this.resetForm();
        this.loadProgramari(); // Reîncarcă pentru calendar
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
        data: null,
        ora: '',
        observatii: '',
        persoana_id: this.selectedPersoana ? this.selectedPersoana.id : '',
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

/* ===== ETAPA 1: JOBS ===== */
.hero-section {
  text-align: center;
  padding: 40px 20px;
}

.loading,
.no-jobs,
.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1rem;
}

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

/* ===== ETAPA 2: PERSOANE ===== */
.persoane-section {
  padding: 40px 20px;
  border-top: 2px solid #e1e8ed;
  margin-top: 20px;
}

.persoane-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin: 30px 0;
}

.persoana-card {
  background: white;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.persoana-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #42b983;
}

.persoana-avatar {
  font-size: 4rem;
  margin-bottom: 15px;
}

.persoana-card h3 {
  margin: 15px 0;
  font-size: 1.2rem;
}

.btn-select {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-select:hover {
  background: #3aa876;
  transform: scale(1.05);
}

/* ===== ETAPA 3: FORMULAR + CALENDAR ===== */
.content-section {
  padding: 30px 20px;
  border-top: 2px solid #e1e8ed;
  margin-top: 30px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h2 {
  margin: 0;
}

.subtitle {
  font-size: 0.8em;
  color: #666;
  font-weight: normal;
}

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
}

/* Calendar Styling */
.calendar-wrapper {
  margin-bottom: 20px;
}

.calendar-input {
  width: 100%;
  max-width: 500px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  background: white;
  transition: border-color 0.3s ease;
}

.calendar-input:hover {
  border-color: #42b983;
}

.calendar-input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

/* Legendă Calendar */
.legend {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #666;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.dot-today {
  background: #3b82f6;
}

.dot-available {
  background: #10b981;
}

.dot-partial {
  background: #f59e0b;
}

.dot-full {
  background: #ef4444;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.btn-submit,
.btn-reset,
.btn-back,
.btn-change {
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit {
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3);
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.4);
}

.btn-reset {
  background: #f0f0f0;
  color: #333;
}

.btn-reset:hover {
  background: #e0e0e0;
}

.btn-back,
.btn-change {
  background: #6c757d;
  color: white;
  margin-top: 20px;
}

.btn-back:hover,
.btn-change:hover {
  background: #5a6268;
}

/* Table Section */
.table-section {
  margin-top: 40px;
}

/* Responsive */
@media (max-width: 768px) {
  .jobs-grid,
  .persoane-grid {
    grid-template-columns: 1fr;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form input,
  .form textarea,
  .form select,
  .calendar-input {
    max-width: 100%;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
  
  .legend {
    justify-content: center;
  }
}
</style>
