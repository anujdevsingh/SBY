<template>
  <div class="pb-5">
    <!-- Beautiful Welcome Banner -->
    <div class="welcome-banner mb-4">
      <div class="welcome-content">
        <h2 class="welcome-greeting mb-1">{{ greeting }}, <span class="user-name">{{ userName }}</span>! 👋</h2>
        <p class="welcome-subtitle mb-0">Welcome to your personal dashboard. Here's an overview of your contributions.</p>
      </div>
      <div class="welcome-decoration"></div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading your dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
      <span class="me-2">⚠</span>
      <div>
        <strong>Error loading data:</strong> {{ error }}
        <button class="btn btn-link btn-sm p-0 ms-2" @click="refreshData">Retry</button>
      </div>
    </div>

    <template v-else>
      <!-- Stats Row -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100">
            <small class="text-muted text-uppercase fw-bold">Your approved total</small>
            <h3 class="fw-bold mt-2 mb-0">₹ {{ myApprovedTotal }}</h3>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100">
            <small class="text-muted text-uppercase fw-bold">Community donations</small>
            <h3 class="fw-bold text-success mt-2 mb-0">₹ {{ communityTotal }}</h3>
            <small class="text-muted">Approved contributions across all donors</small>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm p-3 h-100">
            <small class="text-muted text-uppercase fw-bold">Approved proofs</small>
            <h3 class="fw-bold mt-2 mb-0">{{ approvedCount }}</h3>
            <small class="text-muted">Number of your approved submissions</small>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Submit Form -->
        <div class="col-lg-5 mb-4">
          <TransactionForm @refresh="refreshData" />
        </div>

        <!-- Transaction List -->
        <div class="col-lg-7">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-0 py-3 d-flex align-items-center justify-content-between">
               <h5 class="fw-bold mb-0">Recent Contributions</h5>
               <span class="text-muted small">Latest first</span>
            </div>
            <div class="table-responsive">
              <table class="table align-middle mb-0">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-3 border-0">Date</th>
                    <th class="border-0">Amount</th>
                    <th class="border-0">Status</th>
                    <th class="border-0">Ref</th>
                    <th class="border-0">Proof</th>
                    <th class="border-0">Admin note</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tx in transactions" :key="tx.id">
                    <td class="ps-3 text-muted">{{ formatDate(tx.created_at) }}</td>
                    <td class="fw-bold">₹ {{ tx.amount }}</td>
                    <td>
                      <span class="badge" :class="statusClass(tx.status)">
                        {{ tx.status.toUpperCase() }}
                      </span>
                    </td>
                    <td class="small text-muted">{{ tx.transaction_ref }}</td>
                    <td>
                      <a v-if="tx.screenshot_data" :href="tx.screenshot_data" target="_blank" class="btn btn-sm btn-light">View</a>
                      <a v-else-if="tx.screenshot_path" :href="getFileUrl(tx.screenshot_path)" target="_blank" class="btn btn-sm btn-light">View</a>
                      <span v-else class="text-muted small">—</span>
                    </td>
                    <td class="small text-muted" style="max-width: 160px;">{{ tx.admin_note || '—' }}</td>
                  </tr>
                  <tr v-if="transactions.length === 0">
                    <td colspan="6" class="text-center py-4 text-muted">No transactions yet</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { UPLOAD_BASE_URL } from '../services/api'
import TransactionForm from '../components/TransactionForm.vue'
import { useToast } from '../composables/useToast'
import { useAuthStore } from '../stores/auth'

const { showError } = useToast()
const authStore = useAuthStore()

const transactions = ref([])
const summary = ref({ total_amount: 0, approved_count: 0 })
const isLoading = ref(true)
const error = ref(null)

// Greeting based on time of day
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
})

// Get user's first name for personalized greeting
const userName = computed(() => {
  const fullName = authStore.user?.full_name || 'User'
  return fullName.split(' ')[0]
})

const myApprovedTotal = computed(() =>
  transactions.value
    .filter(t => t.status === 'approved')
    .reduce((sum, t) => sum + t.amount, 0)
    .toFixed(2)
)

const approvedCount = computed(() =>
  transactions.value.filter(t => t.status === 'approved').length
)

const communityTotal = computed(() => Number(summary.value.total_amount || 0).toFixed(2))

const fetchTransactions = async () => {
  try {
    const res = await api.get('/transactions/')
    transactions.value = res.data
  } catch (err) {
    console.error(err)
    throw err
  }
}

const fetchSummary = async () => {
  try {
    const res = await api.get('/transactions/summary')
    summary.value = res.data
  } catch (err) {
    console.error(err)
    throw err
  }
}

const refreshData = async () => {
  isLoading.value = true
  error.value = null
  try {
    // Use Promise.allSettled to handle partial failures gracefully
    const results = await Promise.allSettled([fetchTransactions(), fetchSummary()])
    
    // Check for any rejections (but 401 errors will trigger redirect in interceptor)
    const failed = results.find(r => r.status === 'rejected')
    if (failed) {
      // If we get here (not redirected), show error
      const errMessage = failed.reason?.response?.data?.error || 'Failed to load dashboard data'
      // Only set error if it's not a 401 (which redirects)
      if (failed.reason?.response?.status !== 401) {
        error.value = errMessage
        showError(error.value)
      }
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load dashboard data'
    showError(error.value)
  } finally {
    isLoading.value = false
  }
}

const statusClass = (status) => {
  switch(status) {
    case 'approved': return 'bg-success'
    case 'rejected': return 'bg-danger'
    default: return 'bg-warning text-dark'
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

const getFileUrl = (path) => `${UPLOAD_BASE_URL}/${path}`

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.welcome-content {
  position: relative;
  z-index: 2;
}

.welcome-greeting {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.user-name {
  background: linear-gradient(to right, #ffecd2, #fcb69f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  color: rgba(255, 255, 255, 0.85);
  font-size: 1rem;
}

.welcome-decoration {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  z-index: 1;
}

.welcome-decoration::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}
</style>
