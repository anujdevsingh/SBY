import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem('user')) || null,
        token: localStorage.getItem('token') || null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user?.is_admin,
    },
    actions: {
        async login(email, password) {
            try {
                const response = await api.post('/auth/login', { email, password })
                this.token = response.data.access_token
                this.user = response.data.user
                localStorage.setItem('token', this.token)
                localStorage.setItem('user', JSON.stringify(this.user))
                return true
            } catch (error) {
                throw error.response?.data?.error || 'Login failed'
            }
        },
        async register(userData) {
            try {
                await api.post('/auth/register', userData)
                return true
            } catch (error) {
                throw error.response?.data?.error || 'Registration failed'
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            // router.push('/login') handled in component usually
        }
    }
})
