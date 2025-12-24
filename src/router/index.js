import { createRouter, createWebHistory } from 'vue-router'
import LiveDashboard from '../views/LiveDashboard.vue'
import SimDashboard from '../views/SimDashboard.vue'
import HistoryTrends from '../views/HistoryTrends.vue'

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
    {
      path: '/trends',
      name: 'trends',
      component: HistoryTrends, // Matches Figure A.4
    },
  ],
})

export default router
