import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/funds',
    name: 'Funds',
    component: () => import('@/views/FundList.vue')
  },
  {
    path: '/funds/:id',
    name: 'FundDetail',
    component: () => import('@/views/FundDetail.vue')
  },
  {
    path: '/holdings',
    name: 'Holdings',
    component: () => import('@/views/HoldingList.vue')
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
