<template>
  <div>
    <h2 class="fw-bold mb-4 text-primary">Admin Dashboard</h2>

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
    </ul>

    <div class="tab-content" id="pills-tabContent">
      <!-- Users Logic -->
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
                    <button @click="approveUser(user.id)" class="btn btn-sm btn-success me-2">Approve</button>
                    <button @click="rejectUser(user.id)" class="btn btn-sm btn-outline-danger">Reject</button>
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

      <!-- Txns Logic -->
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
                <button class="btn btn-primary" @click="fetchTransactions">Apply</button>
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
                        <a v-if="tx.screenshot_path" :href="getFileUrl(tx.screenshot_path)" target="_blank" class="btn btn-sm btn-light">View</a>
                        <span v-else class="text-muted small">—</span>
                    </td>
                    <td class="small text-muted" style="max-width: 160px;">{{ tx.admin_note || '—' }}</td>
                    <td>
                      <span class="badge" :class="statusClass(tx.status)">{{ tx.status.toUpperCase() }}</span>
                    </td>
                    <td>
                        <button @click="updateTxStatus(tx.id, 'approved')" class="btn btn-sm btn-success me-2">Approve</button>
                        <button @click="updateTxStatus(tx.id, 'rejected')" class="btn btn-sm btn-outline-danger">Reject</button>
                    </td>
                 </tr>
                 <tr v-if="pendingTxns.length === 0">
                    <td colspan="7" class="text-center py-4 text-muted">No transactions match your filters</td>
                </tr>
               </tbody>
             </table>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { UPLOAD_BASE_URL } from '../services/api'

const stats = ref({})
const pendingUsers = ref([])
const pendingTxns = ref([])
const statusFilter = ref('pending')
const search = ref('')

const fetchData = async () => {
    try {
        const [statsRes, usersRes, txnsRes] = await Promise.all([
            api.get('/admin/stats'),
            api.get('/admin/users?pending=true'),
            api.get('/transactions/admin/all', {
                params: {
                    status: statusFilter.value || undefined,
                    q: search.value || undefined
                }
            })
        ])
        stats.value = statsRes.data
        pendingUsers.value = usersRes.data
        pendingTxns.value = txnsRes.data
    } catch (err) {
        console.error("Failed to load admin data", err)
    }
}

const fetchTransactions = async () => {
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
    }
}

const approveUser = async (id) => {
    if(!confirm("Approve this user?")) return
    await api.post(`/admin/users/${id}/approve`)
    fetchData()
}

const rejectUser = async (id) => {
    if(!confirm("Reject (and delete) this user?")) return
    await api.post(`/admin/users/${id}/reject`)
    fetchData()
}

const updateTxStatus = async (id, status) => {
    if(!confirm(`Mark transaction as ${status}?`)) return
    const note = prompt('Add note (optional):') || ''
    await api.post(`/transactions/${id}/status`, { status, note })
    fetchData()
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

const statCards = computed(() => ([
  { label: 'Total Donations', value: `₹ ${stats.value.total_donations || 0}`, valueClass: 'text-success' },
  { label: 'Pending Users', value: stats.value.pending_users || 0, valueClass: 'text-warning' },
  { label: 'Pending Txns', value: stats.value.pending_transactions || 0, valueClass: 'text-warning' },
  { label: 'Total Users', value: stats.value.total_users || 0, valueClass: '' }
]))

onMounted(fetchData)
</script>
