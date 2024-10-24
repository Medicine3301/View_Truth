import { defineStore } from 'pinia'
import axios from 'axios'
import { notification } from 'ant-design-vue'

interface UserState {
    user: {
        uid: string
        una: string
        email: string
        role:string
        avatar?: string
    } | null
    isAuthenticated: boolean
}

interface RegisterUserData {
    name: string
    email: string
    password: string
    sex: string
    birthday: Date
}

export const useAuthStore = defineStore('auth', {
    state: (): UserState => ({
        user: null,
        isAuthenticated: false
    }),
    getters: {
        isAdmin(state): boolean {
            return state.user?.role === 'admin';
        }
    },
    actions: {
        async login(username: string, password: string) {
            try {
                const response = await axios.post('http://localhost:8000/api/login', {
                    username,
                    password
                })

                if (response.status === 200) {
                    this.user = response.data.user
                    this.isAuthenticated = true
                    localStorage.setItem('token', response.data.token)
                    notification.success({
                        message: '登入成功',
                        description: '歡迎回來！',
                        duration: 3
                    })
                    return true
                }
                return false
            } catch (error: any) {
                const errorMessage = error.response?.data?.error || '登入失敗，請稍後再試'
                notification.error({
                    message: '登入失敗',
                    description: errorMessage,
                    duration: 3
                })
                return false
            }
        },

        async register(userData: RegisterUserData) {
            try {
                const response = await axios.post('http://localhost:8000/api/register', userData)

                if (response.status === 201) {
                    notification.success({
                        message: '註冊成功',
                        description: '請登入以繼續',
                        duration: 3
                    })
                    return true
                }
                return false
            } catch (error: any) {
                const errorMessage = error.response?.data?.error || '註冊失敗，請稍後再試'
                notification.error({
                    message: '註冊失敗',
                    description: errorMessage,
                    duration: 3
                })
                return false
            }
        },

        logout() {
            this.user = null
            this.isAuthenticated = false
            localStorage.removeItem('token')
            notification.info({
                message: '已登出',
                description: '您已成功登出系統',
                duration: 3
            })
        },

        async checkAuth() {
            const token = localStorage.getItem('token')
            if (!token) {
                this.logout()
                return
            }

            try {
                const response = await axios.get('http://localhost:8000/api/verify', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                })

                if (response.status === 200) {
                    this.user = response.data.user
                    this.isAuthenticated = true
                } else {
                    this.logout()
                    notification.warn({
                        message: '會話過期',
                        description: '請重新登入',
                        duration: 3
                    })
                }
            } catch (error) {
                this.logout()
                notification.error({
                    message: '驗證失敗',
                    description: '請重新登入系統',
                    duration: 3
                })
            }
        },

        setupAxiosInterceptors() {
            axios.interceptors.request.use(
                config => {
                    const token = localStorage.getItem('token')
                    if (token) {
                        config.headers.Authorization = `Bearer ${token}`
                    }
                    return config
                },
                error => {
                    return Promise.reject(error)
                }
            )

            axios.interceptors.response.use(
                response => response,
                error => {
                    if (error.response?.status === 401) {
                        this.logout()
                        notification.error({
                            message: '會話過期',
                            description: '請重新登入系統',
                            duration: 3
                        })
                    }
                    return Promise.reject(error)
                }
            )
        }
    }
})