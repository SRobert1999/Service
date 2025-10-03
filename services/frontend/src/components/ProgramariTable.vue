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
          <th>PersoanaID</th>
          <th>ServiciuID</th>
          <th>Data</th>
          <th>Observatii</th>
          <th>Nume</th>
          <th>Prenume</th>
          <th>Email</th>
          <th>Telefon</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in programari" :key="p.id">
          <td>{{ p.id }}</td>
          <td>{{ p.persoana_id }}</td>
          <td>{{ p.serviciu_id }}</td>
          <td>{{ p.data }}</td> <!-- afișează direct data -->
          <td>{{ p.observatii }}</td>
          <td>{{ p.nume }}</td>
          <td>{{ p.prenume }}</td>
          <td>{{ p.email }}</td>
          <td>{{ p.telefon }}</td>
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
  data() {
    return {
      programari: []
    };
  },
  methods: {
    async fetchProgramari() {
      try {
        console.error("Test");
        const res = await axios.get("/programari");
        this.programari = res.data;
      } catch (err) {
        console.error("Eroare la preluarea programărilor:", err);
      }
    }
  },
  mounted() {
    this.fetchProgramari();
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
</style>
