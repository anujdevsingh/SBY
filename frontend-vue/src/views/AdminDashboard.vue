<template>
  <div>
    <!-- Beautiful Welcome Banner for Admin -->
    <div class="welcome-banner admin-banner mb-4">
      <div class="welcome-content">
        <h2 class="welcome-greeting mb-1">{{ greeting }}, <span class="user-name">{{ userName }}</span>! 🛡️</h2>
        <p class="welcome-subtitle mb-0">Welcome to the Admin Control Panel. Manage users, transactions, and monitor platform activity.</p>
      </div>
      <div class="welcome-decoration"></div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading dashboard data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
      <span class="me-2">⚠</span>
      <div>
        <strong>Error loading data:</strong> {{ error }}
        <button class="btn btn-link btn-sm p-0 ms-2" @click="fetchData">Retry</button>
      </div>
    </div>

    <template v-else>
      <!-- Global Stats -->
      <div class="row mb-4 g-3">
        <div class="col-md-3" v-for="card in statCards" :key="card.label">
          <div class="card border-0 shadow-sm p-3 h-100">
            <small class="text-muted text-uppercase fw-bold">{{ card.label }}</small>
            <h3 :class="card.valueClass" class="fw-bold mt-2 mb-0">{{ card.value }}</h3>
            <small class="text-muted" v-if="card.helper">{{ card.helper }}</small>
          </div>
        </div>
      </div>

      <!-- Lists Tab -->
      <ul class="nav nav-pills mb-4" id="pills-tab" role="tablist">
        <li class="nav-item">
          <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#users" type="button">Pending Users</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" data-bs-toggle="pill" data-bs-target="#txns" type="button">Transactions</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" data-bs-toggle="pill" data-bs-target="#allUsers" type="button">All Users</button>
        </li>
      </ul>

      <div class="tab-content" id="pills-tabContent">
        <!-- Pending Users -->
        <div class="tab-pane fade show active" id="users" role="tabpanel">
          <div class="card border-0 shadow-sm">
            <div class="table-responsive">
              <table class="table align-middle mb-0">
                <thead class="bg-light">
                  <tr>
                     <th class="ps-3">Name</th>
                     <th>Email</th>
                     <th>Phone</th>
                     <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in pendingUsers" :key="user.id">
                    <td class="ps-3 fw-bold">{{ user.full_name }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.phone }}</td>
                    <td>
                      <button @click="confirmApproveUser(user)" class="btn btn-sm btn-success me-2" :disabled="actionLoading">
                        <span v-if="actionLoading === `approve-${user.id}`" class="spinner-border spinner-border-sm me-1"></span>
                        Approve
                      </button>
                      <button @click="confirmRejectUser(user)" class="btn btn-sm btn-outline-danger" :disabled="actionLoading">
                        <span v-if="actionLoading === `reject-${user.id}`" class="spinner-border spinner-border-sm me-1"></span>
                        Reject
                      </button>
                    </td>
                  </tr>
                  <tr v-if="pendingUsers.length === 0">
                      <td colspan="4" class="text-center py-4 text-muted">No pending user requests</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Transactions -->
        <div class="tab-pane fade" id="txns" role="tabpanel">
          <div class="card border-0 shadow-sm">
            <div class="card-body border-bottom pb-3">
              <div class="row g-2 align-items-end">
                <div class="col-md-4">
                  <label class="form-label mb-1">Status</label>
                  <select v-model="statusFilter" class="form-select">
                    <option value="">All</option>
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
                <div class="col-md-5">
                  <label class="form-label mb-1">Search (ref / name / email)</label>
                  <input v-model="search" type="text" class="form-control" placeholder="e.g. UTR, donor name, email">
                </div>
                <div class="col-md-3 d-grid">
                  <button class="btn btn-primary" @click="fetchTransactions" :disabled="txnLoading">
                    <span v-if="txnLoading" class="spinner-border spinner-border-sm me-1"></span>
                    Apply
                  </button>
                </div>
              </div>
            </div>
            <div class="table-responsive">
               <table class="table align-middle mb-0">
                 <thead class="bg-light">
                   <tr>
                      <th class="ps-3">User</th>
                      <th>Amount</th>
                      <th>Reference</th>
                      <th>Proof</th>
                      <th>User Note</th>
                      <th>Admin note</th>
                      <th>Status</th>
                      <th>Actions</th>
                   </tr>
                 </thead>
                 <tbody>
                   <tr v-for="tx in pendingTxns" :key="tx.id">
                      <td class="ps-3">
                          <div class="fw-bold">{{ tx.user_name }}</div>
                          <small class="text-muted d-block">ID: {{ tx.user_id }}</small>
                      </td>
                      <td class="fw-bold">₹ {{ tx.amount }}</td>
                      <td>{{ tx.transaction_ref }}</td>
                      <td>
                          <a v-if="tx.screenshot_data" :href="tx.screenshot_data" target="_blank" class="btn btn-sm btn-light">View</a>
                          <a v-else-if="tx.screenshot_path" :href="getFileUrl(tx.screenshot_path)" target="_blank" class="btn btn-sm btn-light">View</a>
                          <span v-else class="text-muted small">—</span>
                      </td>
                      <td class="small" style="max-width: 150px;">
                          <span v-if="tx.user_note" class="text-info" :title="tx.user_note">
                            💬 {{ tx.user_note.length > 50 ? tx.user_note.substring(0, 50) + '...' : tx.user_note }}
                          </span>
                          <span v-else class="text-muted">—</span>
                      </td>
                      <td class="small text-muted" style="max-width: 150px;">{{ tx.admin_note || '—' }}</td>
                      <td>
                        <span class="badge" :class="statusClass(tx.status)">{{ tx.status.toUpperCase() }}</span>
                      </td>
                      <td>
                          <button @click="confirmApproveTx(tx)" class="btn btn-sm btn-success me-2" :disabled="actionLoading">
                            <span v-if="actionLoading === `approve-tx-${tx.id}`" class="spinner-border spinner-border-sm me-1"></span>
                            Approve
                          </button>
                          <button @click="confirmRejectTx(tx)" class="btn btn-sm btn-outline-danger" :disabled="actionLoading">
                            <span v-if="actionLoading === `reject-tx-${tx.id}`" class="spinner-border spinner-border-sm me-1"></span>
                            Reject
                          </button>
                      </td>
                   </tr>
                   <tr v-if="pendingTxns.length === 0">
                      <td colspan="8" class="text-center py-4 text-muted">No transactions match your filters</td>
                  </tr>
                 </tbody>
               </table>
            </div>
          </div>
        </div>

        <!-- All Users -->
        <div class="tab-pane fade" id="allUsers" role="tabpanel">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-0 py-3">
              <h5 class="fw-bold mb-0">All Registered Users</h5>
            </div>
            <div class="table-responsive">
              <table class="table align-middle mb-0">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-3">User</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Status</th>
                    <th>Registered</th>
                    <th>Total Donated</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in allUsers" :key="user.id">
                    <td class="ps-3">
                      <div class="d-flex align-items-center">
                        <div 
                          class="avatar-circle me-2" 
                          :style="getUserAvatarStyle(user)"
                        >
                          <span v-if="!user.photo_path">{{ getInitials(user.full_name) }}</span>
                        </div>
                        <div>
                          <div class="fw-bold">{{ user.full_name }}</div>
                          <small class="text-muted">ID: {{ user.id }}</small>
                        </div>
                      </div>
                    </td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.phone || '—' }}</td>
                    <td>
                      <span class="badge" :class="user.is_approved ? 'bg-success' : 'bg-warning text-dark'">
                        {{ user.is_approved ? 'Approved' : 'Pending' }}
                      </span>
                      <span v-if="!user.is_active" class="badge bg-danger ms-1">Disabled</span>
                      <span v-if="user.is_admin" class="badge bg-primary ms-1">Admin</span>
                    </td>
                    <td class="text-muted small">{{ formatDate(user.created_at) }}</td>
                    <td class="fw-bold text-success">₹ {{ user.total_donated || 0 }}</td>
                  </tr>
                  <tr v-if="allUsers.length === 0">
                    <td colspan="6" class="text-center py-4 text-muted">No users found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Confirm Modal -->
    <ConfirmModal
      v-model:visible="confirmModal.visible"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :variant="confirmModal.variant"
      :confirm-text="confirmModal.confirmText"
      :show-input="confirmModal.showInput"
      :input-placeholder="confirmModal.inputPlaceholder"
      @confirm="confirmModal.onConfirm"
      @cancel="confirmModal.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { UPLOAD_BASE_URL } from '../services/api'
import { useToast } from '../composables/useToast'
import ConfirmModal from '../components/ConfirmModal.vue'
import { useAuthStore } from '../stores/auth'

const { showSuccess, showError } = useToast()
const authStore = useAuthStore()

// Greeting based on time of day
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
})

// Get user's first name for personalized greeting
const userName = computed(() => {
  const fullName = authStore.user?.full_name || 'Admin'
  return fullName.split(' ')[0]
})

const stats = ref({})
const pendingUsers = ref([])
const allUsers = ref([])
const pendingTxns = ref([])
const statusFilter = ref('pending')
const search = ref('')

const isLoading = ref(true)
const txnLoading = ref(false)
const actionLoading = ref(null)
const error = ref(null)

const confirmModal = ref({
  visible: false,
  title: '',
  message: '',
  variant: 'primary',
  confirmText: 'Confirm',
  showInput: false,
  inputPlaceholder: '',
  onConfirm: () => {},
  onCancel: () => {}
})

const fetchData = async () => {
    isLoading.value = true
    error.value = null
    try {
        const [statsRes, usersRes, allUsersRes, txnsRes] = await Promise.all([
            api.get('/admin/stats'),
            api.get('/admin/users?pending=true'),
            api.get('/admin/users'),
            api.get('/transactions/admin/all', {
                params: {
                    status: statusFilter.value || undefined,
                    q: search.value || undefined
                }
            })
        ])
        stats.value = statsRes.data
        pendingUsers.value = usersRes.data
        allUsers.value = allUsersRes.data
        pendingTxns.value = txnsRes.data
    } catch (err) {
        console.error("Failed to load admin data", err)
        error.value = err.response?.data?.error || 'Failed to load dashboard data'
        showError(error.value)
    } finally {
        isLoading.value = false
    }
}

const fetchTransactions = async () => {
    txnLoading.value = true
    try {
        const res = await api.get('/transactions/admin/all', {
            params: {
                status: statusFilter.value || undefined,
                q: search.value || undefined
            }
        })
        pendingTxns.value = res.data
    } catch (err) {
        console.error("Failed to load transactions", err)
        showError(err.response?.data?.error || 'Failed to load transactions')
    } finally {
        txnLoading.value = false
    }
}

const confirmApproveUser = (user) => {
  confirmModal.value = {
    visible: true,
    title: 'Approve User',
    message: `Are you sure you want to approve ${user.full_name}?`,
    variant: 'success',
    confirmText: 'Approve',
    showInput: false,
    inputPlaceholder: '',
    onConfirm: () => approveUser(user.id),
    onCancel: () => {}
  }
}

const confirmRejectUser = (user) => {
  confirmModal.value = {
    visible: true,
    title: 'Reject User',
    message: `Are you sure you want to reject and disable ${user.full_name}?`,
    variant: 'danger',
    confirmText: 'Reject',
    showInput: false,
    inputPlaceholder: '',
    onConfirm: () => rejectUser(user.id),
    onCancel: () => {}
  }
}

const approveUser = async (id) => {
    actionLoading.value = `approve-${id}`
    try {
        await api.post(`/admin/users/${id}/approve`)
        showSuccess('User approved successfully!')
        fetchData()
    } catch (err) {
        showError(err.response?.data?.error || 'Failed to approve user')
    } finally {
        actionLoading.value = null
    }
}

const rejectUser = async (id) => {
    actionLoading.value = `reject-${id}`
    try {
        await api.post(`/admin/users/${id}/reject`)
        showSuccess('User rejected and disabled')
        fetchData()
    } catch (err) {
        showError(err.response?.data?.error || 'Failed to reject user')
    } finally {
        actionLoading.value = null
    }
}

const confirmApproveTx = (tx) => {
  confirmModal.value = {
    visible: true,
    title: 'Approve Transaction',
    message: `Approve transaction of ₹${tx.amount} from ${tx.user_name}?`,
    variant: 'success',
    confirmText: 'Approve',
    showInput: true,
    inputPlaceholder: 'Add note (optional)',
    onConfirm: (note) => updateTxStatus(tx.id, 'approved', note),
    onCancel: () => {}
  }
}

const confirmRejectTx = (tx) => {
  confirmModal.value = {
    visible: true,
    title: 'Reject Transaction',
    message: `Reject transaction of ₹${tx.amount} from ${tx.user_name}?`,
    variant: 'danger',
    confirmText: 'Reject',
    showInput: true,
    inputPlaceholder: 'Add reason (optional)',
    onConfirm: (note) => updateTxStatus(tx.id, 'rejected', note),
    onCancel: () => {}
  }
}

const updateTxStatus = async (id, status, note = '') => {
    actionLoading.value = `${status === 'approved' ? 'approve' : 'reject'}-tx-${id}`
    try {
        await api.post(`/transactions/${id}/status`, { status, note })
        showSuccess(`Transaction ${status}!`)
        fetchData()
    } catch (err) {
        showError(err.response?.data?.error || `Failed to ${status} transaction`)
    } finally {
        actionLoading.value = null
    }
}

const getFileUrl = (path) => {
    return `${UPLOAD_BASE_URL}/${path}`
}

const statusClass = (status) => {
  switch(status) {
    case 'approved': return 'bg-success'
    case 'rejected': return 'bg-danger'
    default: return 'bg-warning text-dark'
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

const getUserAvatarStyle = (user) => {
  // Prefer Base64 photo_data, fallback to file path
  if (user.photo_data) {
    return {
      backgroundImage: `url(${user.photo_data})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  if (user.photo_path) {
    return {
      backgroundImage: `url(${UPLOAD_BASE_URL}/${user.photo_path})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return { backgroundColor: getAvatarColor(user.full_name) }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

const statCards = computed(() => ([
  { label: 'Total Donations', value: `₹ ${stats.value.total_donations || 0}`, valueClass: 'text-success' },
  { label: 'Pending Users', value: stats.value.pending_users || 0, valueClass: 'text-warning' },
  { label: 'Pending Txns', value: stats.value.pending_transactions || 0, valueClass: 'text-warning' },
  { label: 'Total Users', value: stats.value.total_users || 0, valueClass: '' }
]))

onMounted(fetchData)
</script>

<style scoped>
.welcome-banner {
  background: linear-gradient(135deg, #6B46C1 0%, #2563EB 100%);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(107, 70, 193, 0.3);
}

.admin-banner {
  background: linear-gradient(135deg, #1e3a5f 0%, #0d9488 100%);
  box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
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
  background: linear-gradient(to right, #fde68a, #f59e0b);
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

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 0.8rem;
}
</style>
