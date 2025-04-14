import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import Home from './components/Home.vue'
import Register from './components/Register.vue'
import Userprofile from './components/Userprofile.vue'
import Community from './components/community.vue'
import Post from './components/post.vue'
import News from './components/newhome.vue'
import Newspage from './components/newspage.vue'
import AdminUserManagement from './components/AdminUserManagement.vue'

const routes = [
    { 
        path: '/', 
        component: Home, 
        name: 'home',
        meta: { requiresAuth: false }
    },
    { 
        path: '/register', 
        component: Register, 
        name: 'register',
        meta: { requiresAuth: false }
    },
    { 
        path: '/news', 
        component: News, 
        name: 'news',
        meta: { requiresAuth: false }
    },
    { 
        path: '/newspage/:id', 
        component: Newspage, 
        name: 'newspage',
        meta: { requiresAuth: false }
    },
    { 
        path: '/userprofile/:id', 
        component: Userprofile, 
        name: 'userprofile',
        meta: { requiresAuth: true }
    },
    { 
        path: '/community/:id', 
        component: Community, 
        name: 'community',
        meta: { requiresAuth: true }
    },
    { 
        path: '/post/:id', 
        component: Post, 
        name: 'post',
        meta: { requiresAuth: true }
    },
    { 
        path: '/adminusermanagement', 
        component: AdminUserManagement, 
        name: 'adminusermanagement',
        meta: { requiresAuth: true, requiresAdmin: true }
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 修改全局路由守衛
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    const token = localStorage.getItem('token') || authStore.tokenState.accessToken

    if (to.meta.requiresAuth) {
        if (!token) {
            notification.error({
                message: '請先登入',
                description: '此頁面需要登入才能訪問',
                duration: 3
            });
            return next('/')
        }

        try {
            const isAuthenticated = await authStore.checkAuth()
            
            if (!isAuthenticated) {
                notification.error({
                    message: '認證失敗',
                    description: '請重新登入',
                    duration: 3
                });
                return next('/')
            }

            // 檢查管理員權限
            if (to.meta.requiresAdmin && authStore.userState.user?.role !== 'admin') {
                notification.error({
                    message: '權限不足',
                    description: '此頁面需要管理員權限',
                    duration: 3
                });
                return next('/')
            }

            return next()
        } catch (error) {
            console.error('Route guard error:', error)
            return next('/')
        }
    }
    
    next()
})

export default router
