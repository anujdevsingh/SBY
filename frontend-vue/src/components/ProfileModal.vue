<template>
  <Teleport to="body">
    <div
      v-if="isVisible"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0,0,0,0.5);"
      @click.self="handleClose"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 bg-primary text-white">
            <h5 class="modal-title fw-bold">My Profile</h5>
            <button type="button" class="btn-close btn-close-white" @click="handleClose"></button>
          </div>
          
          <div class="modal-body p-0">
            <div class="row g-0">
              <!-- Profile Photo Section -->
              <div class="col-md-4 bg-light p-4 text-center">
                <div class="position-relative d-inline-block mb-3">
                  <div 
                    class="profile-photo rounded-circle mx-auto"
                    :style="photoStyle"
                  >
                    <span v-if="!photoUrl" class="initials">{{ getInitials(form.full_name) }}</span>
                  </div>
                  <label v-if="isEditing" class="btn btn-sm btn-primary position-absolute bottom-0 end-0 rounded-circle edit-photo-btn">
                    <input 
                      type="file" 
                      @change="handlePhotoChange" 
                      accept="image/*"
                      class="d-none"
                    />
                    📷
                  </label>
                </div>
                
                <h5 class="fw-bold mb-1">{{ authStore.user?.full_name }}</h5>
                <p class="text-muted small mb-3">{{ authStore.user?.email }}</p>
                
                <div class="d-flex justify-content-center gap-2">
                  <span class="badge" :class="authStore.user?.is_approved ? 'bg-success' : 'bg-warning text-dark'">
                    {{ authStore.user?.is_approved ? 'Approved' : 'Pending' }}
                  </span>
                  <span v-if="authStore.user?.is_admin" class="badge bg-primary">Admin</span>
                </div>
                
                <div class="mt-4 text-muted small">
                  <div class="mb-1">Member since</div>
                  <div class="fw-bold">{{ formatDate(authStore.user?.created_at) }}</div>
                </div>
              </div>
              
              <!-- Profile Details Section -->
              <div class="col-md-8 p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <h6 class="fw-bold text-primary mb-0">Profile Details</h6>
                  <button 
                    v-if="!isEditing" 
                    class="btn btn-sm btn-outline-primary"
                    @click="startEditing"
                  >
                    ✏️ Edit
                  </button>
                </div>
                
                <form @submit.prevent="saveProfile">
                  <div class="mb-3">
                    <label class="form-label text-muted small mb-1">Full Name</label>
                    <input 
                      v-if="isEditing"
                      v-model="form.full_name" 
                      type="text" 
                      class="form-control" 
                      required
                    />
                    <div v-else class="form-control-plaintext fw-bold">{{ authStore.user?.full_name }}</div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label text-muted small mb-1">Email Address</label>
                    <div class="form-control-plaintext fw-bold">{{ authStore.user?.email }}</div>
                    <small class="text-muted">Email cannot be changed</small>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label text-muted small mb-1">Phone Number</label>
                    <input 
                      v-if="isEditing"
                      v-model="form.phone" 
                      type="tel" 
                      class="form-control"
                    />
                    <div v-else class="form-control-plaintext fw-bold">{{ authStore.user?.phone || '—' }}</div>
                  </div>
                  
                  <!-- Password Change Section -->
                  <div v-if="isEditing" class="border-top pt-3 mt-4">
                    <h6 class="fw-bold text-muted mb-3">Change Password (Optional)</h6>
                    <div class="mb-3">
                      <label class="form-label text-muted small mb-1">Current Password</label>
                      <input 
                        v-model="form.current_password" 
                        type="password" 
                        class="form-control"
                        placeholder="Enter current password"
                      />
                    </div>
                    <div class="mb-3">
                      <label class="form-label text-muted small mb-1">New Password</label>
                      <input 
                        v-model="form.new_password" 
                        type="password" 
                        class="form-control"
                        placeholder="Enter new password"
                      />
                    </div>
                  </div>
                  
                  <!-- Action Buttons -->
                  <div v-if="isEditing" class="d-flex gap-2 mt-4">
                    <button type="submit" class="btn btn-primary" :disabled="saving">
                      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                      Save Changes
                    </button>
                    <button type="button" class="btn btn-light" @click="cancelEditing">
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'
import { UPLOAD_BASE_URL } from '../services/api'

const props = defineProps({
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible'])

const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const isVisible = ref(props.visible)
const isEditing = ref(false)
const saving = ref(false)
const newPhoto = ref(null)
const newPhotoPreview = ref(null)

const form = reactive({
  full_name: '',
  phone: '',
  current_password: '',
  new_password: ''
})

watch(() => props.visible, (val) => {
  isVisible.value = val
  if (val) {
    resetForm()
  }
})

const photoUrl = computed(() => {
  if (newPhotoPreview.value) return newPhotoPreview.value
  if (authStore.user?.photo_path) {
    return `${UPLOAD_BASE_URL}/${authStore.user.photo_path}`
  }
  return null
})

const photoStyle = computed(() => {
  if (photoUrl.value) {
    return {
      backgroundImage: `url(${photoUrl.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return { backgroundColor: getAvatarColor(form.full_name || authStore.user?.full_name) }
})

const resetForm = () => {
  form.full_name = authStore.user?.full_name || ''
  form.phone = authStore.user?.phone || ''
  form.current_password = ''
  form.new_password = ''
  newPhoto.value = null
  newPhotoPreview.value = null
  isEditing.value = false
}

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  resetForm()
}

const handleClose = () => {
  emit('update:visible', false)
  isVisible.value = false
  resetForm()
}

const handlePhotoChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    newPhoto.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      newPhotoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const saveProfile = async () => {
  saving.value = true
  
  try {
    const formData = new FormData()
    formData.append('full_name', form.full_name)
    formData.append('phone', form.phone)
    
    if (form.current_password && form.new_password) {
      formData.append('current_password', form.current_password)
      formData.append('new_password', form.new_password)
    }
    
    if (newPhoto.value) {
      formData.append('photo', newPhoto.value)
    }
    
    await authStore.updateProfile(formData)
    showSuccess('Profile updated successfully!')
    isEditing.value = false
    newPhoto.value = null
    newPhotoPreview.value = null
  } catch (err) {
    showError(err)
  } finally {
    saving.value = false
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

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.modal {
  animation: fadeIn 0.2s ease;
}

.modal-dialog {
  animation: slideIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.profile-photo {
  width: 120px;
  height: 120px;
  border: 4px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-photo .initials {
  color: white;
  font-size: 2.5rem;
  font-weight: bold;
}

.edit-photo-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.form-control-plaintext {
  padding: 0.375rem 0;
}
</style>
