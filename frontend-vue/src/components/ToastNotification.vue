<template>
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1100;">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast show align-items-center border-0 mb-2"
        :class="toastClass(toast.type)"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center">
            <span class="toast-icon me-2">{{ toastIcon(toast.type) }}</span>
            <span>{{ toast.message }}</span>
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="removeToast(toast.id)"
            aria-label="Close"
          ></button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()

const toastClass = (type) => {
  switch (type) {
    case 'success': return 'bg-success text-white'
    case 'error': return 'bg-danger text-white'
    case 'warning': return 'bg-warning text-dark'
    default: return 'bg-primary text-white'
  }
}

const toastIcon = (type) => {
  switch (type) {
    case 'success': return '✓'
    case 'error': return '✕'
    case 'warning': return '⚠'
    default: return 'ℹ'
  }
}
</script>

<style scoped>
.toast {
  min-width: 280px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
