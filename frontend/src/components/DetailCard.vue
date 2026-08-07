<script setup>
import { ref } from 'vue'

const props = defineProps({
  drive: {
    type: Object,
    required: true
  },
  isEditable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'update-skills'])

const newSkillInput = ref('')
const localSkills = ref([...(props.drive.skills || [])])

const addSkill = () => {
  const name = newSkillInput.value.trim()
  if (!name) return

  const exists = localSkills.value.some(s => s.toLowerCase() === name.toLowerCase())
  if (!exists) {
    localSkills.value.push(name)
    emit('update-skills', localSkills.value)
  }
  newSkillInput.value = ''
}

const removeSkill = (index) => {
  localSkills.value.splice(index, 1)
  emit('update-skills', localSkills.value)
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="card detail-card shadow-lg border-0 p-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="fw-bold text-dark m-0">{{ drive.role }}</h4>
        <button type="button" class="btn-close" @click="emit('close')"></button>
      </div>

      <hr class="my-2" />

      <div class="row g-2 mb-3">
        <div class="col-6">
          <small class="text-muted d-block">Company</small>
          <span class="fw-semibold">{{ drive.company_name || 'N/A' }}</span>
        </div>
        <div class="col-6">
          <small class="text-muted d-block">Package</small>
          <span class="fw-semibold text-success">{{ drive.package }}</span>
        </div>
        <div class="col-6">
          <small class="text-muted d-block">Experience Required</small>
          <span class="fw-semibold">{{ drive.experience || 'N/A' }}</span>
        </div>
        <div class="col-6">
          <small class="text-muted d-block">Status</small>
          <span class="badge bg-primary">{{ drive.status }}</span>
        </div>
      </div>

      <!-- Skills Section -->
      <div class="mb-3">
        <label class="form-label small fw-semibold text-muted">Required Skills</label>
        
        <div v-if="isEditable" class="d-flex gap-2 mb-2">
          <input 
            type="text" 
            v-model="newSkillInput" 
            @keyup.enter.prevent="addSkill"
            class="form-control form-control-sm" 
            placeholder="Add a new skill..."
          />
          <button type="button" @click="addSkill" class="btn btn-outline-primary btn-sm px-3 fw-bold">+</button>
        </div>

        <div class="d-flex flex-wrap gap-1">
          <span 
            v-for="(skill, index) in localSkills" 
            :key="index" 
            class="badge bg-secondary d-flex align-items-center gap-1 py-1 px-2"
          >
            {{ skill }}
            <span 
              v-if="isEditable" 
              @click="removeSkill(index)" 
              class="ms-1 text-white-50 fw-bold" 
              style="cursor: pointer;"
            >
              &times;
            </span>
          </span>
        </div>
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
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.detail-card {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
}
</style>