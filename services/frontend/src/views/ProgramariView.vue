
<template>
  <div class="programari">
    <div class="header">
      <h2>
        <span v-if="selectedJobName">Programări - {{ selectedJobName }}</span>
        <span v-else>Programări</span>
      </h2>
      <button @click="goBack" v-if="selectedJobName" class="btn-back">
        ← Schimbă categorie
      </button>
    </div>

    <button @click="showForm = !showForm">
      {{ showForm ? 'Închide formular' : 'Adaugă programare' }}
    </button>

    <div v-if="showForm" class="form">
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


      <button @click="adaugaProgramare">Trimite</button>
    </div>

    <ProgramariTable :refresh="refreshTable" />
  </div>
</template>

<script>
import ProgramariTable from "@/components/ProgramariTable.vue";
import axios from "axios";

export default {
  name: "ProgramariView",
  components: { ProgramariTable },
  inject: ['showMessage'],
  data() {
    return {
      showForm: false,
      persoane: [],
      servicii: [],
      selectedJobId: null,
      selectedJobName: null,
      newProgramare: {
        nume: "",
        prenume: "",
        email: "",
        telefon: "",
        data: "",
        ora: "",
        observatii: "",
        persoana_id: "",
        serviciu_id: ""
      },
      refreshTable: false
    };
  },
  async mounted() {
    // Check if we have job_id from query params
    const { job_id, job_name } = this.$route.query;
    if (job_id) {
      this.selectedJobId = parseInt(job_id);
      this.selectedJobName = job_name || 'Categoria selectată';
    }
    await this.loadData();
  },
  methods: {
    async loadData() {
      try {
        // Build URLs with job_id filter if available
        const persoaneUrl = this.selectedJobId ? `/persoane?job_id=${this.selectedJobId}` : '/persoane';
        const serviciiUrl = this.selectedJobId ? `/servicii?job_id=${this.selectedJobId}` : '/servicii';

        const [persResp, servResp] = await Promise.all([
          axios.get(persoaneUrl),
          axios.get(serviciiUrl)
        ]);
        this.persoane = persResp.data;
        this.servicii = servResp.data;
        console.log(`Loaded ${this.persoane.length} persoane and ${this.servicii.length} servicii for job_id:`, this.selectedJobId);
      } catch (err) {
        console.error("Eroare la încărcarea listelor:", err);
        this.showMessage({
          text: "Eroare la încărcarea datelor!",
          type: "error"
        });
      }
    },
    goBack() {
      this.$router.push('/select-job');
    },
    async adaugaProgramare() {
      try {
        // Validare minimă
        if (!this.newProgramare.data || !this.newProgramare.ora) {
          alert("Vă rugăm completați data și ora!");
          return;
        }

        // Curățim payload-ul - stringuri goale devin null
        const payload = {
          data: this.newProgramare.data,
          ora: this.newProgramare.ora,
          nume: this.newProgramare.nume || null,
          prenume: this.newProgramare.prenume || null,
          email: this.newProgramare.email || null,
          telefon: this.newProgramare.telefon || null,
          observatii: this.newProgramare.observatii || null,
          persoana_id: this.newProgramare.persoana_id || null,
          serviciu_id: this.newProgramare.serviciu_id || null
        };

        console.log("Sending payload:", payload);
        await axios.post("/programari", payload);

        // Show success message instead of alert
        this.showMessage({
          text: "Programare adăugată cu succes!",
          type: "success"
        });

        this.showForm = false;

        // reset
        this.newProgramare = {
          nume: "",
          prenume: "",
          email: "",
          telefon: "",
          data: "",
          ora: "",
          observatii: "",
          persoana_id: "",
          serviciu_id: ""
        };

        this.refreshTable = !this.refreshTable;

      } catch (err) {
        console.error("Error details:", err.response ? err.response.data : err);

        // Show more specific error message
        const errorMsg = err.response?.data?.detail ||
                        err.response?.data?.message ||
                        "Eroare la adăugare programare!";

        this.showMessage({
          text: errorMsg,
          type: "error"
        });
      }
    }
  }
};
</script>

<style>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h2 {
  margin: 0;
  color: #2c3e50;
}

.btn-back {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.btn-back:hover {
  background: #5a6268;
}

.form {
  margin: 15px 0;
}

.form input, .form textarea, .form select {
  display: block;
  margin-bottom: 10px;
  width: 300px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .form input, .form textarea, .form select {
    width: 100%;
    max-width: 300px;
  }
}
</style>
