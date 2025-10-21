import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProgramariView from '../views/ProgramariView.vue'
import LoginView from '../views/LoginView.vue'
import EditProgramareView from '../views/EditProgramareView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },

  {
    path: '/programari',
    name: 'programari',
    component: ProgramariView
  },

  {
    path: '/programari/:id/edit',
    name: 'edit-programare',
    component: EditProgramareView
  },

  {
    path: '/login',
    name: 'login',
    component: LoginView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router