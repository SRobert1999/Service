<template>
  <div class="programari">
    <h2>Programări</h2>

    <!-- Buton pentru afișarea formularului -->
    <button @click="showForm = !showForm">
      {{ showForm ? 'Închide formular' : 'Adaugă programare' }}
    </button>

    <!-- Formular pentru adăugarea unei programări -->
    <div v-if="showForm" class="form">
      <input v-model="newProgramare.nume" placeholder="Nume" />
      <input v-model="newProgramare.prenume" placeholder="Prenume" />
      <input v-model="newProgramare.email" placeholder="Email" />
      <input v-model="newProgramare.telefon" placeholder="Telefon" />
      <input v-model="newProgramare.data" type="date" placeholder="Data" />
      <input v-model="newProgramare.ora" type="time" placeholder="Ora" />
      <textarea v-model="newProgramare.observatii" placeholder="Observatii"></textarea>
      <button @click="adaugaProgramare">Trimite</button>
    </div>

    <!-- Tabelul cu programările existente -->
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
      newProgramare: {
        nume: "",
        prenume: "",
        email: "",
        telefon: "",
        data: "",
        ora: "",
        observatii: ""
      },
      refreshTable: false
    };
  },
  methods: {
    async adaugaProgramare() {
      try {
        // trimitem doar câmpurile necesare, ForeignKey poate fi null
        const payload = {
          ...this.newProgramare,
          persoana_id: null,  // optional, poate fi null pentru test
          serviciu_id: null   // optional, poate fi null pentru test
        };

        console.log("Trimitem programare:", payload);

        await axios.post("/programari", payload);

        alert("Programare adăugată!");
        this.showForm = false;

        // reset formular
        this.newProgramare = {
          nume: "",
          prenume: "",
          email: "",
          telefon: "",
          data: "",
          ora: "",
          observatii: ""
        };

        // forțăm reîncărcarea tabelului
        this.refreshTable = !this.refreshTable;

      } catch (err) {
        console.error(err.response ? 'test ' + err.response.data : err);
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
.form input, .form textarea {
  display: block;
  margin-bottom: 10px;
  width: 300px;
}
</style>
