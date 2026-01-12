<template>
  <div class="pb-5">
    <!-- Hero Section -->
    <div class="text-center py-5">
      <div class="d-inline-flex align-items-center justify-content-center mb-4 hero-logo">
        <img src="@/assets/ngo-logo.jpeg" alt="Sahyog Bima Yojna logo" class="hero-img">
      </div>
      <h1 class="display-4 fw-bold text-primary mb-3">Welcome to Sahyog Bima Yojna</h1>
      <p class="lead text-muted mb-5">Empowering communities through transparent contributions.</p>
      <div>
        <router-link to="/register" class="btn btn-primary btn-lg px-5 me-3">Join &amp; Contribute</router-link>
        <router-link to="/login" class="btn btn-outline-secondary btn-lg px-5">Login</router-link>
      </div>
    </div>

    <!-- Community Stats -->
    <div class="row justify-content-center mb-5 mt-4">
      <div class="col-md-8">
        <div class="card border-0 shadow-sm p-4 text-center bg-gradient-light">
          <div class="row">
            <div class="col-md-6 border-end">
              <small class="text-muted text-uppercase fw-bold">Total Community Donations</small>
              <h2 class="fw-bold text-success mb-0">₹ {{ communityStats.total_amount || 0 }}</h2>
            </div>
            <div class="col-md-6">
              <small class="text-muted text-uppercase fw-bold">Approved Contributions</small>
              <h2 class="fw-bold text-primary mb-0">{{ communityStats.approved_count || 0 }}</h2>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Donators Section -->
    <div class="py-5">
      <h2 class="text-center fw-bold mb-2">Our Top Supporters</h2>
      <p class="text-center text-muted mb-4">Recognizing our generous contributors</p>
      
      <div v-if="donatorsLoading" class="text-center py-4">
        <div class="spinner-border text-primary spinner-border-sm" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="topDonators.length === 0" class="text-center py-4">
        <p class="text-muted">Be the first to contribute!</p>
      </div>
      
      <div v-else class="row justify-content-center g-4">
        <div class="col-6 col-md-4 col-lg-2" v-for="(donor, index) in topDonators" :key="donor.id">
          <div class="card border-0 shadow-sm text-center p-3 h-100 donor-card">
            <div class="position-relative mx-auto mb-3">
              <div class="avatar-lg" :style="getDonorAvatarStyle(donor)">
                <span v-if="!donor.photo_path && !donor.photo_data">{{ getInitials(donor.name) }}</span>
              </div>
              <span v-if="index === 0" class="badge-rank bg-warning text-dark">🏆</span>
              <span v-else-if="index === 1" class="badge-rank bg-secondary text-white">🥈</span>
              <span v-else-if="index === 2" class="badge-rank bg-warning text-dark" style="opacity: 0.7;">🥉</span>
            </div>
            <h6 class="fw-bold mb-1 text-truncate">{{ donor.name }}</h6>
            <small class="text-success fw-bold">₹ {{ formatAmount(donor.total_donated) }}</small>
          </div>
        </div>
      </div>
    </div>

    <!-- About SBY NGO Section -->
    <div class="py-5 mt-4">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <div class="card border-0 shadow-sm overflow-hidden">
            <div class="row g-0">
              <div class="col-md-4 bg-primary d-flex align-items-center justify-content-center p-4">
                <div class="text-center text-white">
                  <img src="@/assets/ngo-logo.jpeg" alt="SBY Logo" class="about-logo mb-3">
                  <h4 class="fw-bold">Sahyog Bima Yojna</h4>
                  <p class="small mb-0 opacity-75">Established for Community Welfare</p>
                </div>
              </div>
              <div class="col-md-8">
                <div class="card-body p-4 p-md-5">
                  <h3 class="fw-bold text-primary mb-4">About Our NGO</h3>
                  
                  <div class="mb-4">
                    <h6 class="fw-bold text-uppercase text-muted mb-2">
                      <span class="text-primary me-2">🎯</span> Our Mission
                    </h6>
                    <p class="text-muted">
                      To provide financial security and support to our community members during times of need. 
                      We believe in collective care and transparent management of contributions.
                    </p>
                  </div>
                  
                  <div class="mb-4">
                    <h6 class="fw-bold text-uppercase text-muted mb-2">
                      <span class="text-primary me-2">👁️</span> Our Vision
                    </h6>
                    <p class="text-muted">
                      Building a self-sustaining community where every member has access to emergency 
                      financial support, ensuring no one faces hardship alone.
                    </p>
                  </div>
                  
                  <div class="mb-4">
                    <h6 class="fw-bold text-uppercase text-muted mb-2">
                      <span class="text-primary me-2">💡</span> What We Do
                    </h6>
                    <ul class="text-muted ps-3">
                      <li>Collect and manage community contributions transparently</li>
                      <li>Provide insurance coverage for registered members</li>
                      <li>Support families during medical emergencies</li>
                      <li>Maintain complete financial transparency</li>
                    </ul>
                  </div>
                  
                  <div class="d-flex gap-3 mt-4">
                    <router-link to="/register" class="btn btn-primary">
                      Join Now
                    </router-link>
                    <a href="mailto:support@sby.org" class="btn btn-outline-secondary">
                      Contact Us
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="py-5 mt-2">
      <h2 class="text-center fw-bold mb-2">How It Works</h2>
      <p class="text-center text-muted mb-5">Simple steps to join our community</p>
      
      <div class="row justify-content-center g-4">
        <div class="col-md-3">
          <div class="text-center">
            <div class="step-circle bg-primary text-white mb-3">1</div>
            <h6 class="fw-bold">Register</h6>
            <p class="text-muted small">Create your account and wait for admin approval</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="text-center">
            <div class="step-circle bg-primary text-white mb-3">2</div>
            <h6 class="fw-bold">Contribute</h6>
            <p class="text-muted small">Make your contribution and upload proof</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="text-center">
            <div class="step-circle bg-primary text-white mb-3">3</div>
            <h6 class="fw-bold">Get Protected</h6>
            <p class="text-muted small">Enjoy community support when you need it</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { UPLOAD_BASE_URL } from '../services/api'

const topDonators = ref([])
const communityStats = ref({ total_amount: 0, approved_count: 0 })
const donatorsLoading = ref(true)

const fetchTopDonators = async () => {
  donatorsLoading.value = true
  try {
    const res = await api.get('/transactions/top-donators')
    topDonators.value = res.data
  } catch (err) {
    console.error('Failed to load top donators', err)
  } finally {
    donatorsLoading.value = false
  }
}

const fetchCommunityStats = async () => {
  try {
    const res = await api.get('/transactions/summary')
    communityStats.value = res.data
  } catch (err) {
    console.error('Failed to load community stats', err)
  }
}

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

const formatAmount = (amount) => {
  return Number(amount).toLocaleString('en-IN')
}

const getDonorAvatarStyle = (donor) => {
  // Prefer Base64 photo_data, fallback to file path
  if (donor.photo_data) {
    return {
      backgroundImage: `url(${donor.photo_data})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  if (donor.photo_path) {
    return {
      backgroundImage: `url(${UPLOAD_BASE_URL}/${donor.photo_path})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return { backgroundColor: getAvatarColor(donor.name) }
}

onMounted(() => {
  fetchTopDonators()
  fetchCommunityStats()
})
</script>

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

.bg-gradient-light {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.avatar-lg {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.25rem;
}

.badge-rank {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
}

.donor-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.donor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.about-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 12px;
  background: white;
  padding: 8px;
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: bold;
}
</style>
