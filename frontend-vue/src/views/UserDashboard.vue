<template>
  <div class="pb-5">
    <h2 class="fw-bold mb-4 text-primary">My Dashboard</h2>

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
                    <a v-if="tx.screenshot_path" :href="getFileUrl(tx.screenshot_path)" target="_blank" class="btn btn-sm btn-light">View</a>
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { UPLOAD_BASE_URL } from '../services/api'
import TransactionForm from '../components/TransactionForm.vue'

const transactions = ref([])
const summary = ref({ total_amount: 0, approved_count: 0 })

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
  }
}

const fetchSummary = async () => {
  try {
    const res = await api.get('/transactions/summary')
    summary.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const refreshData = () => {
  fetchTransactions()
  fetchSummary()
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
