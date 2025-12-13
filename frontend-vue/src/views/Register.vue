<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
      <div class="card border-0 shadow-sm p-4">
        <h3 class="fw-bold mb-4 text-center">Create Account</h3>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
        
        <form @submit.prevent="handleRegister" v-if="!success">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.full_name" type="text" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Phone Number</label>
            <input v-model="form.phone" type="tel" class="form-control" required>
          </div>
          <div class="mb-4">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2">Register Request</button>
        </form>
        <div v-else class="text-center">
           <p>Your account request has been submitted. Please wait for admin approval.</p>
           <router-link to="/login" class="btn btn-outline-primary">Back to Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const form = reactive({
  full_name: '',
  email: '',
  phone: '',
  password: ''
})
const error = ref('')
const success = ref('')
const authStore = useAuthStore()

const handleRegister = async () => {
  error.value = ''
  try {
    await authStore.register(form)
    success.value = 'Registration successful!'
  } catch (err) {
    error.value = err
  }
}
</script>
