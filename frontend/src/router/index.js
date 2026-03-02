import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Admin from '../views/Admin.vue'
import Track from '../views/Track.vue'
import Account from '../views/Account.vue'
import Privacy from '../views/Privacy.vue'
import Offer from '../views/Offer.vue'
import { getToken } from '../authToken'

const routes = [
  { path: '/', component: Home },
  { path: '/admin', component: Admin },
  {
    path: '/track',
    name: 'Track',
    component: Track
  },
  {
    path: '/account',
    name: 'account',
    component: Account
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: Privacy
  },
  {
    path: '/offer',
    name: 'offer',
    component: Offer
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 🔐 Глобальная защита роутов
router.beforeEach((to, from, next) => {
  const token = getToken()

  // какие страницы требуют авторизации
  const protectedRoutes = ['/track']

  if (protectedRoutes.includes(to.path) && !token) {
    return next('/account')
  }

  next()
})

router.onError((error) => {
  console.error('Router error:', error)
})

export default router
