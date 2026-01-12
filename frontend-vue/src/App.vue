<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center fw-bold text-primary" to="/">
        <img src="@/assets/ngo-logo.jpeg" alt="Sahyog Bima Yojna" class="brand-logo me-2" />
        <span>Sahyog Bima Yojna</span>
      </router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          <li class="nav-item" v-if="!authStore.isAuthenticated">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!authStore.isAuthenticated">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item" v-if="authStore.isAuthenticated && !authStore.isAdmin">
             <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="authStore.isAdmin">
             <router-link class="nav-link" to="/admin">Dashboard</router-link>
          </li>
          <!-- Profile Button -->
          <li class="nav-item" v-if="authStore.isAuthenticated">
            <button class="btn btn-link nav-link d-flex align-items-center" @click="showProfile = true">
              <div class="nav-avatar me-2" :style="avatarStyle">
                <span v-if="!authStore.user?.photo_path && !authStore.user?.photo_data">{{ getInitials(authStore.user?.full_name) }}</span>
              </div>
              <span class="d-none d-md-inline">{{ authStore.user?.full_name?.split(' ')[0] }}</span>
            </button>
          </li>
          <li class="nav-item" v-if="authStore.isAuthenticated">
            <button class="btn btn-link nav-link text-danger" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container">
    <router-view></router-view>
  </div>

  <ChatWidget />
  <ToastNotification />
  <ProfileModal v-model:visible="showProfile" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import ChatWidget from './components/ChatWidget.vue'
import ToastNotification from './components/ToastNotification.vue'
import ProfileModal from './components/ProfileModal.vue'
import { UPLOAD_BASE_URL } from './services/api'

const authStore = useAuthStore()
const router = useRouter()
const showProfile = ref(false)

const avatarStyle = computed(() => {
  // Prefer Base64 photo_data, fallback to file path
  if (authStore.user?.photo_data) {
    return {
      backgroundImage: `url(${authStore.user.photo_data})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  if (authStore.user?.photo_path) {
    return {
      backgroundImage: `url(${UPLOAD_BASE_URL}/${authStore.user.photo_path})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return { backgroundColor: getAvatarColor(authStore.user?.full_name) }
})

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const getAvatarColor = (name) => {
  if (!name) return '#6c757d'
  const colors = ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#198754', '#20c997', '#0dcaf0']
  const index = name.charCodeAt(0) % colors.length
  return colors[index]
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
body {
  background-color: #f8f9fa;
  font-family: 'Inter', sans-serif;
}

.brand-logo {
  height: 36px;
  width: 36px;
  object-fit: contain;
}

.nav-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  border: 2px solid #e9ecef;
}
</style>
