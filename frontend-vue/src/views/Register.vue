<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
      <div class="card border-0 shadow-sm p-4">
        <h3 class="fw-bold mb-4 text-center">Create Account</h3>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
        
        <form @submit.prevent="handleRegister" v-if="!success">
          <!-- Photo Upload -->
          <div class="mb-4 text-center">
            <div class="position-relative d-inline-block">
              <div 
                class="photo-preview rounded-circle bg-light d-flex align-items-center justify-content-center mx-auto"
                :style="photoPreview ? { backgroundImage: `url(${photoPreview})` } : {}"
              >
                <span v-if="!photoPreview" class="text-muted fs-1">📷</span>
              </div>
              <label class="btn btn-sm btn-primary position-absolute bottom-0 end-0 rounded-circle photo-btn">
                <input 
                  ref="photoInput"
                  type="file" 
                  @change="handlePhotoChange" 
                  accept="image/*"
                  class="d-none"
                />
                +
              </label>
            </div>
            <small class="text-muted d-block mt-2">Upload your photo</small>
          </div>

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
          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Register Request
          </button>
        </form>
        <div v-else class="text-center">
           <div class="mb-3">
             <span class="display-4">✅</span>
           </div>
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
const photo = ref(null)
const photoPreview = ref(null)
const photoInput = ref(null)
const error = ref('')
const success = ref('')
const loading = ref(false)
const authStore = useAuthStore()

const handlePhotoChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    photo.value = file
    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      photoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleRegister = async () => {
  error.value = ''
  loading.value = true
  
  try {
    // Create FormData for multipart upload
    const formData = new FormData()
    formData.append('full_name', form.full_name)
    formData.append('email', form.email)
    formData.append('phone', form.phone)
    formData.append('password', form.password)
    if (photo.value) {
      formData.append('photo', photo.value)
    }
    
    await authStore.register(formData)
    success.value = 'Registration successful!'
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.photo-preview {
  width: 100px;
  height: 100px;
  border: 3px dashed #dee2e6;
  background-size: cover;
  background-position: center;
  transition: border-color 0.2s;
}

.photo-preview:hover {
  border-color: #0d6efd;
}

.photo-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: bold;
}
</style>
