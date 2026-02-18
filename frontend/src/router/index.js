import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Admin from '../views/Admin.vue'
import Track from '../views/Track.vue'
import Account from "../views/Account.vue"

const routes = [
  { path: '/', component: Home },
  { path: '/admin', component: Admin },
  {
  path: '/track',
  name: 'Track',
  component: Track
},
{
  path: "/account",
  name: "account",
  component: Account,
}

]

export default createRouter({
  history: createWebHistory(),
  routes
})