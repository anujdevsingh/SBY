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
        async register(formData) {
            try {
                // formData is now a FormData object with photo
                await api.post('/auth/register', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                })
                return true
            } catch (error) {
                throw error.response?.data?.error || 'Registration failed'
            }
        },
        async updateProfile(formData) {
            try {
                const response = await api.put('/auth/profile', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                })
                this.user = response.data.user
                localStorage.setItem('user', JSON.stringify(this.user))
                return response.data
            } catch (error) {
                throw error.response?.data?.error || 'Failed to update profile'
            }
        },
        async refreshUser() {
            try {
                const response = await api.get('/auth/me')
                this.user = response.data
                localStorage.setItem('user', JSON.stringify(this.user))
                return this.user
            } catch (error) {
                console.error('Failed to refresh user', error)
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
        }
    }
})
