import { createRouter, createWebHistory } from 'vue-router'
import LiveDashboard from '../views/LiveDashboard.vue'
import SimDashboard from '../views/SimDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'live',
      component: LiveDashboard, // Matches Figure A.1
    },
    {
      path: '/simulation',
      name: 'simulation',
      component: SimDashboard, // Matches Figure A.5
    },
  ],
})

export default router
