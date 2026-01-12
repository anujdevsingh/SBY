import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
// Use relative path for uploads - works with Vite proxy in dev and can be overridden for production
export const UPLOAD_BASE_URL = import.meta.env.VITE_UPLOAD_BASE || '/uploads'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000, // 10 second timeout to prevent infinite loading
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercept requests to add token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Intercept responses to handle 401 (unauthorized) errors
// This happens when the token is invalid/expired (e.g., after backend restart)
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token is invalid - clear auth state and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Only redirect if not already on login/register page
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
