<template>
  <div class="card border-0 shadow-sm p-4">
    <h4 class="fw-bold mb-3">Submit Contribution Proof</h4>
    
    <form @submit.prevent="submitTransaction">
      <div class="mb-3">
        <label class="form-label">Amount (₹)</label>
        <input v-model="amount" type="number" min="1" step="0.01" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Transaction Reference / UTR</label>
        <input v-model="refNum" type="text" class="form-control" placeholder="e.g. UPI123456" required>
      </div>
      <div class="mb-3">
        <label class="form-label">Screenshot Proof</label>
        <input ref="fileInput" type="file" @change="handleFileChange" class="form-control" accept="image/*" required>
      </div>
      <div class="mb-4">
        <label class="form-label">Comment / Note <span class="text-muted fw-normal">(optional)</span></label>
        <textarea 
          v-model="userNote" 
          class="form-control" 
          rows="3" 
          maxlength="500"
          placeholder="Add any additional information for the admin (e.g., donation purpose, special notes...)"
        ></textarea>
        <small class="text-muted">{{ userNote.length }}/500 characters</small>
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
import { useToast } from '../composables/useToast'

const emit = defineEmits(['refresh'])
const { showSuccess, showError } = useToast()

const amount = ref('')
const refNum = ref('')
const userNote = ref('')
const file = ref(null)
const fileInput = ref(null)
const loading = ref(false)

const handleFileChange = (e) => {
  file.value = e.target.files[0]
}

const submitTransaction = async () => {
  if (!file.value) {
    showError('Please upload a screenshot')
    return
  }
  
  loading.value = true
  
  const formData = new FormData()
  formData.append('amount', amount.value)
  formData.append('transaction_ref', refNum.value)
  formData.append('screenshot', file.value)
  formData.append('user_note', userNote.value)
  
  try {
    await api.post('/transactions/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showSuccess('Transaction submitted successfully! Waiting for approval.')
    amount.value = ''
    refNum.value = ''
    userNote.value = ''
    file.value = null
    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    emit('refresh')
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to submit transaction')
  } finally {
    loading.value = false
  }
}
</script>
