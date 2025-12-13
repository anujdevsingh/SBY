import api from './api'

export function searchPolicy(query, top_k = 5) {
  return api.post('/policy/search', { query, top_k })
}

