<template>
  <div>
    <h1>Lista programări</h1>

    <div v-if="programari.length === 0">
      <p>Nu există programări înregistrate.</p>
    </div>

    <table v-else border="1" cellpadding="5">
      <thead>
        <tr>
          <th>ID</th>
          <th>Persoană</th>
          <th>Serviciu</th>
          <th>Data</th>
          <th>Ora</th>
          <th>Observatii</th>
          <th>Nume</th>
          <th>Prenume</th>
          <th>Email</th>
          <th>Telefon</th>
          <th v-if="currentUser">Acțiuni</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in programari" :key="p.id">
          <td>{{ p.id }}</td>
          <td>{{ persoaneMap[p.persoana_id] || 'N/A' }}</td>
          <td>{{ serviciiMap[p.serviciu_id] || 'N/A' }}</td>
          <td>{{ p.data }}</td>
          <td>{{ p.ora }}</td>
          <td>{{ p.observatii }}</td>
          <td>{{ p.nume }}</td>
          <td>{{ p.prenume }}</td>
          <td>{{ p.email }}</td>
          <td>{{ p.telefon }}</td>
          <td v-if="currentUser" class="actions">
            <button @click="editProgramare(p)" class="btn-edit">Editare</button>
            <button @click="deleteProgramare(p.id)" class="btn-delete">Ștergere</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProgramariTable",
  props: {
    refresh: Boolean
  },
  inject: ['showMessage'],
  data() {
    return {
      programari: [],
      persoane: [],
      servicii: [],
      persoaneMap: {},
      serviciiMap: {},
      currentUser: null
    };
  },
  methods: {
    async fetchProgramari() {
      try {
        // Preia toate datele în paralel
        const [programariRes, persoaneRes, serviciiRes] = await Promise.all([
          axios.get("/programari"),
          axios.get("/persoane"),
          axios.get("/servicii")
        ]);

        this.programari = programariRes.data;
        this.persoane = persoaneRes.data;
        this.servicii = serviciiRes.data;

        console.log("Persoane:", this.persoane);
        console.log("Servicii:", this.servicii);
        console.log("Programari:", this.programari);

        // Creează maps pentru lookup rapid
        this.persoaneMap = {};
        this.persoane.forEach(p => {
          this.persoaneMap[p.id] = `${p.nume} ${p.prenume}`;
        });

        this.serviciiMap = {};
        this.servicii.forEach(s => {
          this.serviciiMap[s.id] = s.descriere;
        });

        console.log("PersoaneMap:", this.persoaneMap);
        console.log("ServiciiMap:", this.serviciiMap);

      } catch (err) {
        console.error("Eroare la preluarea datelor:", err);
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
    async deleteProgramare(programareId) {
      if (!confirm('Ești sigur că vrei să ștergi această programare?')) {
        return;
      }

      try {
        await axios.delete(`/programari/${programareId}`);
        this.showMessage({
          text: "Programare ștearsă cu succes!",
          type: "success"
        });
        // Reîncarcă lista de programări
        this.fetchProgramari();
      } catch (error) {
        console.error('Eroare la ștergere:', error);
        const errorMsg = error.response?.data?.detail || "Eroare la ștergerea programării!";
        this.showMessage({
          text: errorMsg,
          type: "error"
        });
      }
    },
    editProgramare(programare) {
      // Navigate to edit page with programare data
      this.$router.push({
        name: 'edit-programare',
        params: { id: programare.id },
        query: {
          data: JSON.stringify(programare),
          persoane: JSON.stringify(this.persoane),
          servicii: JSON.stringify(this.servicii)
        }
      });
    }
  },
  async mounted() {
    await this.fetchProgramari();
    await this.checkAuthStatus();
  },
  watch: {
    refresh() {
      this.fetchProgramari();
    }
  }
};
</script>

<style scoped>
table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 15px;
}

th, td {
  padding: 8px;
  text-align: left;
}

.actions {
  white-space: nowrap;
  width: 150px;
}

.btn-edit, .btn-delete {
  padding: 4px 8px;
  margin: 0 2px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-edit {
  background-color: #007bff;
  color: white;
}

.btn-edit:hover {
  background-color: #0056b3;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}
</style>
