<template>
  <div class="text-center py-5">
    <div class="d-inline-flex align-items-center justify-content-center mb-4 hero-logo">
      <img src="@/assets/ngo-logo.jpeg" alt="Sahyog Bima Yojna logo" class="hero-img">
    </div>
    <h1 class="display-4 fw-bold text-primary mb-3">Welcome to Sahyog Bima Yojna</h1>
    <p class="lead text-muted mb-5">Empowering communities through transparent contributions.</p>
    <div>
      <router-link to="/register" class="btn btn-primary btn-lg px-5 me-3">Join & Contribute</router-link>
      <router-link to="/login" class="btn btn-outline-secondary btn-lg px-5">Login</router-link>
    </div>
  </div>
</template>

<style scoped>
.hero-logo {
  background: #fff;
  border-radius: 16px;
  padding: 12px 18px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
}
.hero-img {
  height: 120px;
  width: 120px;
  object-fit: contain;
}
</style>
