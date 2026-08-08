<script setup>
import { computed } from 'vue'

const props = defineProps({
  application: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// Simple array of status strings
const steps = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected']

const isRejected = computed(() => {
  return ['Rejected', 'College Rejected'].includes(props.application.status)
})
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="card tracker-card shadow-lg border-0 p-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h5 class="fw-bold m-0">{{ application.role }}</h5>
          <small class="text-muted">{{ application.company_name }}</small>
        </div>
        <button type="button" class="btn-close" @click="emit('close')"></button>
      </div>

      <hr />

      <!-- Step Tracker Line -->
      <div class="py-4">
        <div class="d-flex justify-content-between align-items-center position-relative">
          <div class="tracker-line"></div>

          <!-- Step Circles -->
          <div 
            v-for="(step, index) in steps" 
            :key="step" 
            class="text-center position-relative step-node"
          >
            <!-- Show green tick IF active status matches step string -->
            <div 
              class="circle-step mx-auto d-flex align-items-center justify-content-center fw-bold"
              :class="{
                'active-tick': application.status === step,
                'rejected': isRejected && index === 0
              }"
            >
              <span v-if="application.status === step">✓</span>
              <span v-else-if="isRejected && index === 0">✕</span>
              <span v-else>{{ index + 1 }}</span>
            </div>

            <small class="d-block mt-2 fw-semibold text-muted">{{ step }}</small>
          </div>
        </div>
      </div>

      <!-- Rejection Banner -->
      <div v-if="isRejected" class="alert alert-danger p-2 small text-center mt-2">
        Application Status: <strong>{{ application.status }}</strong>
      </div>

      <!-- Interview Date Info -->
      <div v-if="application.int_date" class="alert alert-info p-2 small text-center mt-2">
        📅 Interview Scheduled On: <strong>{{ application.int_date }}</strong>
      </div>

      <div class="d-flex justify-content-end mt-3">
        <button class="btn btn-sm btn-secondary" @click="emit('close')">Close</button>
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
  z-index: 1050;
}

.tracker-card {
  width: 90%;
  max-width: 600px;
  background: white;
  border-radius: 12px;
}

.tracker-line {
  position: absolute;
  top: 20px;
  left: 10%;
  width: 80%;
  height: 4px;
  background-color: #e0e0e0;
  z-index: 1;
}

.step-node {
  z-index: 2;
  width: 25%;
}

.circle-step {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #6c757d;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

/* Green tick for active status */
.circle-step.active-tick {
  background-color: #198754;
  color: white;
  box-shadow: 0 0 0 4px rgba(25, 135, 84, 0.25);
}

.circle-step.rejected {
  background-color: #dc3545;
  color: white;
}
</style>