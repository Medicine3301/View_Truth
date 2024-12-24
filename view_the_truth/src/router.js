import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './components/Home.vue'
import Register from './components/Register.vue'
import Userprofile from './components/Userprofile.vue'
import Community from './components/community.vue'
import Post from './components/post.vue'
import News from './components/newhome.vue'
import Newspage from './components/newspage.vue'

const routes = [
    { path: '/', component: Home, name: 'home' },
    { path: '/register', component: Register, name: 'register' },
    { path: '/news', component: News, name: 'news' },
    { path: '/newspage/:id', component: Newspage, name: 'newspage' },
    { path: '/userprofile/:id', component: Userprofile, name: 'userprofile' },
    { path: '/community/:id', component: Community, name: 'community' },
    { path: '/post/:id', component: Post, name: 'post' },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router
