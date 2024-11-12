import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './components/Home.vue'
import Register from './components/Register.vue'
import Userprofile from './components/userprofile.vue'
import Community from './components/community.vue'
import Post from './components/post.vue'
const routes = [
    { path: '/', component: Home, name: 'home' },
    { path: '/register', component: Register, name: 'rigister' },
    { path: '/userprofile/:id', component: Userprofile, name: 'userprofile' },
    { path: '/community/:id', component: Community, name: 'community' },
    { path: '/post/:id', component: Post, name: 'post' },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router

// Vue Router 配置：定义应用路由