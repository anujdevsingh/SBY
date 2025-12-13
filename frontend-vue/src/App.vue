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
        <ul class="navbar-nav ms-auto">
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
          <li class="nav-item" v-if="authStore.isAuthenticated">
            <button class="btn btn-link nav-link" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container">
    <router-view></router-view>
  </div>

  <ChatWidget />
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import ChatWidget from './components/ChatWidget.vue'

const authStore = useAuthStore()
const router = useRouter()

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
</style>
