<template>
  <div class="card border-0 shadow-sm p-4">
    <h4 class="fw-bold mb-3">Submit Contribution Proof</h4>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <form @submit.prevent="submitTransaction">
      <div class="mb-3">
        <label class="form-label">Amount (₹)</label>
        <input v-model="amount" type="number" min="1" step="0.01" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Transaction Reference / UTR</label>
        <input v-model="refNum" type="text" class="form-control" placeholder="e.g. UPI123456" required>
      </div>
      <div class="mb-4">
        <label class="form-label">Screenshot Proof</label>
        <input type="file" @change="handleFileChange" class="form-control" accept="image/*" required>
      </div>
      <button type="submit" class="btn btn-primary w-100" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        Submit Verification
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const emit = defineEmits(['refresh'])

const amount = ref('')
const refNum = ref('')
const file = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleFileChange = (e) => {
  file.value = e.target.files[0]
}

const submitTransaction = async () => {
  if (!file.value) {
    error.value = 'Please upload a screenshot'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = ''
  
  const formData = new FormData()
  formData.append('amount', amount.value)
  formData.append('transaction_ref', refNum.value)
  formData.append('screenshot', file.value)
  
  try {
    await api.post('/transactions/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    success.value = 'Transaction submitted successfully! Waiting for approval.'
    amount.value = ''
    refNum.value = ''
    file.value = null
    // Reset file input manually if needed
    emit('refresh')
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to submit transaction'
  } finally {
    loading.value = false
  }
}
</script>
