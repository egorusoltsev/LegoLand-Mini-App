import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Admin from '../views/Admin.vue'
import Track from '../views/Track.vue'


const routes = [
  { path: '/', component: Home },
  { path: '/admin', component: Admin },
  {
  path: '/track',
  name: 'Track',
  component: Track
}

]

export default createRouter({
  history: createWebHistory(),
  routes
})