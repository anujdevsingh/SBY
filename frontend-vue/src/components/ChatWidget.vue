<template>
  <div class="chat-widget">
    <button class="chat-fab" @click="open = !open">
      <span v-if="!open">Chat</span>
      <span v-else>&times;</span>
    </button>

    <div v-if="open" class="chat-panel shadow-sm">
      <div class="chat-header d-flex justify-content-between align-items-center">
        <strong>Policy Assistant</strong>
        <button class="btn btn-sm btn-link text-muted" @click="open = false">&times;</button>
      </div>
      <div class="chat-body">
        <div class="mb-2">
          <input
            v-model="query"
            @keyup.enter="doSearch"
            type="text"
            class="form-control form-control-sm"
            placeholder="Ask about policies..."
          />
        </div>
        <button class="btn btn-primary btn-sm w-100 mb-2" :disabled="loading || !query" @click="doSearch">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
          Search
        </button>
        <div class="small text-muted mb-2">Returns the most relevant policy snippets.</div>
        <div class="chat-results">
          <div v-if="error" class="alert alert-danger p-2">{{ error }}</div>
          <div v-if="results.length === 0 && !loading && !error" class="text-muted">No results yet.</div>
          <div v-for="(res, idx) in results" :key="idx" class="result-item">
            <div class="fw-bold small text-primary">{{ res.source || 'Policy' }}</div>
            <div class="small">{{ res.text }}</div>
            <div class="text-muted tiny">Score: {{ res.score?.toFixed(3) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { searchPolicy } from '../services/policy'

const open = ref(false)
const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref('')

const doSearch = async () => {
  if (!query.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await searchPolicy(query.value, 5)
    results.value = res.data || []
  } catch (err) {
    error.value = err.response?.data?.error || 'Search failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1050;
}
.chat-fab {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 12px 16px;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
}
.chat-panel {
  width: 320px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 12px;
  margin-bottom: 12px;
}
.chat-header {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 6px;
  margin-bottom: 8px;
}
.chat-body {
  max-height: 320px;
  overflow: auto;
}
.chat-results {
  max-height: 220px;
  overflow-y: auto;
}
.result-item {
  padding: 8px;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f8fafc;
}
.tiny {
  font-size: 0.75rem;
}
</style>

