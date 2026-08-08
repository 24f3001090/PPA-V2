<script setup>
defineProps({
  title: {
    type: String,
  },
  message: {
    type: String,
  },
  confirmText: {
    type: String,
  },
  confirmClass: {
    type: String,
  }
})

const emit = defineEmits(['confirm', 'close'])
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="card confirm-card shadow-lg border-0 p-4">
      <div class="d-flex align-items-center gap-3 mb-3">
        <div>
          <h5 class="fw-bold text-dark mb-2">{{ title }}</h5>
          <small class="text-muted">{{ message }}</small>
        </div>
      </div>

      <div class="d-flex justify-content-end gap-2 mt-3">
        <button type="button" class="btn btn-sm btn-light border" @click="emit('close')">
          Cancel
        </button>
        <button type="button" class="btn btn-sm" :class="confirmClass" @click="emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
}

.confirm-card {
  width: 90%;
  max-width: 420px;
  background: white;
  border-radius: 12px;
}

.warning-icon {
  font-size: 1.5rem;
  line-height: 1;
}
</style>