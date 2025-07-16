import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/gathering',
    name: 'Gathering',
    component: () => import('../views/Gathering.vue')
  },
  {
    path: '/crafting',
    name: 'Crafting',
    component: () => import('../views/Crafting.vue')
  },
  {
    path: '/fishing',
    name: 'Fishing',
    component: () => import('../views/Fishing.vue')
  },
  {
    path: '/goldsaucer',
    name: 'GoldSaucer',
    component: () => import('../views/GoldSaucer.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/Logs.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 