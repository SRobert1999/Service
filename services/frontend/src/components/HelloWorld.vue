```vue
   <template>
     <div class="hello">
       <h1>{{ msg }}</h1>
       <div v-if="loading">Se încarcă...</div>
       <div v-else-if="error" class="error">{{ error }}</div>
       <div v-else class="api-status">
         <p><strong>Status API:</strong> {{ apiStatus }}</p>
         <p><strong>Mesaj:</strong> {{ apiMessage }}</p>
       </div>
     </div>
   </template>

   <script>
   import axios from 'axios';

   export default {
     name: 'HelloWorld',
     props: {
       msg: {
         type: String,
         default: 'Bun venit la Sistemul de Programări'
       }
     },
     data() {
       return {
         loading: true,
         error: null,
         apiStatus: '',
         apiMessage: ''
       };
     },
     async mounted() {
       try {
         // Testează conexiunea la backend
         const response = await axios.get('http://localhost:5000/');
         this.apiStatus = response.data.status;
         this.apiMessage = response.data.message;
       } catch (err) {
         this.error = 'Nu se poate conecta la backend: ' + err.message;
       } finally {
         this.loading = false;
       }
     }
   };
   </script>

   <style scoped>
   .hello {
     padding: 20px;
   }
   .error {
     color: red;
     padding: 10px;
     background-color: #fee;
     border-radius: 4px;
   }
   .api-status {
     padding: 10px;
     background-color: #efe;
     border-radius: 4px;
     margin-top: 10px;
   }
   </style>
   ```
