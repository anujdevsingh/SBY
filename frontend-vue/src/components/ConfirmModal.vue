<template>
  <Teleport to="body">
    <div
      v-if="isVisible"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0,0,0,0.5);"
      @click.self="handleCancel"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">{{ title }}</h5>
            <button type="button" class="btn-close" @click="handleCancel"></button>
          </div>
          <div class="modal-body py-4">
            <p class="mb-0 text-muted">{{ message }}</p>
            <div v-if="showInput" class="mt-3">
              <input
                v-model="inputValue"
                type="text"
                class="form-control"
                :placeholder="inputPlaceholder"
              />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-light" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button
              type="button"
              class="btn"
              :class="confirmButtonClass"
              @click="handleConfirm"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure you want to proceed?' },
  confirmText: { type: String, default: 'Confirm' },
  cancelText: { type: String, default: 'Cancel' },
  variant: { type: String, default: 'primary' }, // primary, success, danger
  showInput: { type: Boolean, default: false },
  inputPlaceholder: { type: String, default: 'Enter value...' }
})

const emit = defineEmits(['confirm', 'cancel', 'update:visible'])

const isVisible = ref(props.visible)
const inputValue = ref('')

watch(() => props.visible, (val) => {
  isVisible.value = val
  if (val) inputValue.value = ''
})

const confirmButtonClass = computed(() => {
  return `btn-${props.variant}`
})

const handleConfirm = () => {
  emit('confirm', inputValue.value)
  emit('update:visible', false)
  isVisible.value = false
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
  isVisible.value = false
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
</style>
