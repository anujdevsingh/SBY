import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
    const addToast = (message, type = 'info', duration = 4000) => {
        const id = ++toastId
        toasts.value.push({ id, message, type })

        if (duration > 0) {
            setTimeout(() => {
                removeToast(id)
            }, duration)
        }
    }

    const removeToast = (id) => {
        const index = toasts.value.findIndex(t => t.id === id)
        if (index > -1) {
            toasts.value.splice(index, 1)
        }
    }

    const showSuccess = (message, duration = 4000) => addToast(message, 'success', duration)
    const showError = (message, duration = 5000) => addToast(message, 'error', duration)
    const showWarning = (message, duration = 4000) => addToast(message, 'warning', duration)
    const showInfo = (message, duration = 4000) => addToast(message, 'info', duration)

    return {
        toasts,
        addToast,
        removeToast,
        showSuccess,
        showError,
        showWarning,
        showInfo
    }
}
