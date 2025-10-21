<template>
  <div class="edit-programare">
    <h2>Editare Programare #{{ programareId }}</h2>

    <div v-if="loading" class="loading">
      Se încarcă datele...
    </div>

    <form v-else @submit.prevent="saveProgramare" class="form">
      <!-- Date personale -->
      <input v-model="form.nume" placeholder="Nume" />
      <input v-model="form.prenume" placeholder="Prenume" />
      <input v-model="form.email" type="email" placeholder="Email" />
      <input v-model="form.telefon" placeholder="Telefon" />

      <!-- Data și ora -->
      <input v-model="form.data" type="date" placeholder="Data" />
      <input v-model="form.ora" type="time" placeholder="Ora" />

      <!-- Observații -->
      <textarea v-model="form.observatii" placeholder="Observații"></textarea>

      <!-- Select Persoană -->
      <label>Persoană:</label>
      <select v-model.number="form.persoana_id">
        <option value="">Nicio persoană selectată</option>
        <option v-for="p in persoane" :key="p.id" :value="p.id">
          {{ p.nume }} {{ p.prenume }}
        </option>
      </select>

      <!-- Select Servicii -->
      <label>Serviciu:</label>
      <select v-model.number="form.serviciu_id">
        <option value="">Niciun serviciu selectat</option>
        <option v-for="s in servicii" :key="s.id" :value="s.id">
          {{ s.descriere }}
        </option>
      </select>

      <div class="form-actions">
        <button type="submit" :disabled="saving">
          {{ saving ? 'Se salvează...' : 'Salvează modificările' }}
        </button>
        <button type="button" @click="goBack" class="btn-cancel">
          Anulează
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EditProgramareView",
  inject: ['showMessage'],
  data() {
    return {
      programareId: null,
      loading: true,
      saving: false,
      persoane: [],
      servicii: [],
      form: {
        nume: "",
        prenume: "",
        email: "",
        telefon: "",
        data: "",
        ora: "",
        observatii: "",
        persoana_id: "",
        serviciu_id: ""
      }
    };
  },
  async mounted() {
    this.programareId = this.$route.params.id;

    // Load data from query params if available
    const queryData = this.$route.query.data;
    const queryPersoane = this.$route.query.persoane;
    const queryServicii = this.$route.query.servicii;

    if (queryData) {
      try {
        const programare = JSON.parse(queryData);
        this.form = {
          nume: programare.nume || "",
          prenume: programare.prenume || "",
          email: programare.email || "",
          telefon: programare.telefon || "",
          data: programare.data || "",
          ora: programare.ora || "",
          observatii: programare.observatii || "",
          persoana_id: programare.persoana_id || "",
          serviciu_id: programare.serviciu_id || ""
        };
      } catch (e) {
        console.error("Eroare la parsarea datelor:", e);
      }
    }

    if (queryPersoane) {
      try {
        this.persoane = JSON.parse(queryPersoane);
      } catch (e) {
        console.error("Eroare la parsarea persoanelor:", e);
        await this.loadPersoane();
      }
    } else {
      await this.loadPersoane();
    }

    if (queryServicii) {
      try {
        this.servicii = JSON.parse(queryServicii);
      } catch (e) {
        console.error("Eroare la parsarea serviciilor:", e);
        await this.loadServicii();
      }
    } else {
      await this.loadServicii();
    }

    this.loading = false;
  },
  methods: {
    async loadPersoane() {
      try {
        const response = await axios.get("/persoane");
        this.persoane = response.data;
      } catch (error) {
        console.error("Eroare la încărcarea persoanelor:", error);
        this.showMessage({
          text: "Eroare la încărcarea persoanelor",
          type: "error"
        });
      }
    },
    async loadServicii() {
      try {
        const response = await axios.get("/servicii");
        this.servicii = response.data;
      } catch (error) {
        console.error("Eroare la încărcarea serviciilor:", error);
        this.showMessage({
          text: "Eroare la încărcarea serviciilor",
          type: "error"
        });
      }
    },
    async saveProgramare() {
      if (!this.form.data || !this.form.ora) {
        this.showMessage({
          text: "Vă rugăm completați data și ora!",
          type: "error"
        });
        return;
      }

      this.saving = true;

      try {
        // Curățăm payload-ul - stringuri goale devin null
        const payload = {
          data: this.form.data,
          ora: this.form.ora,
          nume: this.form.nume || null,
          prenume: this.form.prenume || null,
          email: this.form.email || null,
          telefon: this.form.telefon || null,
          observatii: this.form.observatii || null,
          persoana_id: this.form.persoana_id || null,
          serviciu_id: this.form.serviciu_id || null
        };

        await axios.put(`/programari/${this.programareId}`, payload);

        this.showMessage({
          text: "Programare actualizată cu succes!",
          type: "success"
        });

        // Redirect back to programari page
        setTimeout(() => {
          this.$router.push('/programari');
        }, 1500);

      } catch (error) {
        console.error("Error details:", error.response ? error.response.data : error);

        const errorMsg = error.response?.data?.detail ||
                        error.response?.data?.message ||
                        "Eroare la actualizarea programării!";

        this.showMessage({
          text: errorMsg,
          type: "error"
        });
      } finally {
        this.saving = false;
      }
    },
    goBack() {
      this.$router.push('/programari');
    }
  }
};
</script>

<style scoped>
.edit-programare {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form input, .form textarea, .form select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form textarea {
  min-height: 100px;
  resize: vertical;
}

.form select {
  cursor: pointer;
}

label {
  font-weight: 500;
  color: #333;
  margin-bottom: -10px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.form-actions button {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.form-actions button[type="submit"] {
  background-color: #28a745;
  color: white;
}

.form-actions button[type="submit"]:hover:not(:disabled) {
  background-color: #218838;
}

.form-actions button[type="submit"]:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.loading {
  text-align: center;
  padding: 20px;
  font-style: italic;
  color: #666;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}
</style>