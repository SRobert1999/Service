<template>
  <div class="programari">
    <h2>Programări</h2>

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
  data() {
    return {
      showForm: false,
      persoane: [],
      servicii: [],
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
    await this.loadData();
  },
  methods: {
    async loadData() {
      try {
        const [persResp, servResp] = await Promise.all([
          axios.get("/persoane"),
          axios.get("/servicii")
        ]);
        this.persoane = persResp.data;
        this.servicii = servResp.data;
      } catch (err) {
        console.error("Eroare la încărcarea listelor:", err);
      }
    },
    async adaugaProgramare() {
      try {
        const payload = { ...this.newProgramare,
          persoana_id: this.newProgramare.persoana_id || null,
          serviciu_id: this.newProgramare.serviciu_id || null};

        await axios.post("/programari", payload);

        alert("Programare adăugată!");
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
        console.error(err.response ? err.response.data : err);
        alert("Eroare la adăugare programare!");
      }
    }
  }
};
</script>

<style>
.form {
  margin: 15px 0;
}
.form input, .form textarea, .form select {
  display: block;
  margin-bottom: 10px;
  width: 300px;
}
</style>