import 'bootstrap/dist/css/bootstrap.css';
import { createApp } from "vue";
import axios from 'axios';

import App from './App.vue';
import router from './router';

// Import V-Calendar
import VCalendar from 'v-calendar';
import 'v-calendar/style.css';

const app = createApp(App);

axios.defaults.withCredentials = true;
axios.defaults.baseURL = "http://localhost:5000"; // the FastAPI backend

// Provide global message handler
app.provide('showMessage', (msg) => {
  console.log(msg.type + ':', msg.text);
});

// Use V-Calendar with Romanian locale
app.use(VCalendar, {
  locales: {
    'ro': {
      masks: {
        L: 'DD/MM/YYYY',
      }
    }
  }
});

app.use(router);
app.mount("#app");