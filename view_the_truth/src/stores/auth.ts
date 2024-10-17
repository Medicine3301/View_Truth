import { defineStore } from 'pinia'
import axios from 'axios'
import { message } from 'ant-design-vue'

interface UserState {
    isAuthenticated: boolean
    userInfo: {
        id?: number
        name?: string
        email?: string
        sex?: string
        birthday?: string
    } | null
    token: string | null
}

export const useAuthStore = defineStore('auth', {
    state: (): UserState => ({
        isAuthenticated: false,
        userInfo: null,
        token: null
    }),

    getters: {
        getUserInfo: (state) => state.userInfo,
        getIsAuthenticated: (state) => state.isAuthenticated
    },

    actions: {
        async login(username: string, password: string) {
            try {
                const response = await axios.post('/api/login', {
                    username,
                    password
                })

                if (response.data.success) {
                    this.userInfo = response.data.user
                    this.token = response.data.token
                    this.isAuthenticated = true

                    // 儲存 token 到 localStorage
                    localStorage.setItem('token', response.data.token)

                    message.success('登入成功')
                    return true
                }
            } catch (error: any) {
                message.error(error.response?.data?.message || '登入失敗')
                return false
            }
        },

        async register(userData: {
            name: string
            email: string
            passwd: string
            sex: string
            birthday: string
        }) {
            try {
                const response = await axios.post('/api/register', userData)

                if (response.data.success) {
                    message.success('註冊成功')
                    return true
                }
            } catch (error: any) {
                message.error(error.response?.data?.message || '註冊失敗')
                return false
            }
        },

        async checkAuth() {
            const token = localStorage.getItem('token')
            if (!token) return false

            try {
                const response = await axios.get('/api/check-auth', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                })

                if (response.data.success) {
                    this.userInfo = response.data.user
                    this.isAuthenticated = true
                    this.token = token
                    return true
                }
            } catch (error) {
                this.logout()
                return false
            }
        },

        logout() {
            this.userInfo = null
            this.isAuthenticated = false
            this.token = null
            localStorage.removeItem('token')
            message.success('已登出')
        }
    }
})