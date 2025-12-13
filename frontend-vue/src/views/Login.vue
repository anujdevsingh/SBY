<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card border-0 shadow-sm p-4">
        <h3 class="fw-bold mb-4 text-center">Login</h3>
        <div v-if="pendingApproval" class="alert alert-warning">
          Your account is awaiting admin approval. We’ll notify you once it’s activated.
        </div>
        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input v-model="email" type="email" class="form-control" required>
          </div>
          <div class="mb-4">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2">Sign In</button>
        </form>
        <p class="mt-3 text-center text-muted">
          Don't have an account? <router-link to="/register">Register</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')
const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    if (authStore.isAdmin) {
        router.push('/admin')
    } else {
        router.push('/dashboard')
    }
  } catch (err) {
    const serverMsg = err?.response?.data?.error
    const msg = typeof serverMsg === 'string'
      ? serverMsg
      : err?.message || String(err)
    error.value = msg
  }
}

const pendingApproval = computed(() => {
  if (!error.value || typeof error.value !== 'string') return false
  return error.value.toLowerCase().includes('not approved')
})
</script>
