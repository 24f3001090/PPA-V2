<script setup>
import { ref } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'drive'
  },
  data: {
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
const localSkills = ref([...(props.data.skills || [])])

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

      <!-- Drive -->
      <template v-if="type === 'drive'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4 class="fw-bold text-dark m-0">{{ data.role }}</h4>
          <button type="button" class="btn-close" @click="emit('close')"></button>
        </div>

        <hr class="my-2" />

        <div class="row g-2 mb-3">
          <div class="col-6">
            <small class="text-muted d-block">Company</small>
            <span class="fw-semibold">{{ data.company_name || 'N/A' }}</span>
          </div>
          <div class="col-6">
            <small class="text-muted d-block">Package</small>
            <span class="fw-semibold text-success">{{ data.package }}</span>
          </div>
          <div class="col-6">
            <small class="text-muted d-block">Experience Required</small>
            <span class="fw-semibold">{{ data.experience || 'N/A' }}</span>
          </div>
          <div v-if="isEditable" class="col-6">
            <small class="text-muted d-block">Status</small>
            <span class="badge bg-primary">{{ data.status }}</span>
          </div>
        </div>

        <!-- Skills Section -->
        <div class="mb-3">
          <label class="form-label small fw-semibold text-muted">Required Skills</label>

          <div v-if="isEditable" class="d-flex gap-2 mb-2">
            <input type="text" v-model="newSkillInput" @keyup.enter.prevent="addSkill"
              class="form-control form-control-sm" placeholder="Add a new skill..." />
            <button type="button" @click="addSkill" class="btn btn-outline-primary btn-sm px-3 fw-bold">+</button>
          </div>

          <div class="d-flex flex-wrap gap-1">
            <span v-for="(skill, index) in localSkills" :key="index"
              class="badge bg-secondary d-flex align-items-center gap-1 py-1 px-2">
              {{ skill }}
              <span v-if="isEditable" @click="removeSkill(index)" class="ms-1 text-white-50 fw-bold"
                style="cursor: pointer;">
                &times;
              </span>
            </span>
          </div>
        </div>
      </template>

      <!-- Student -->
      <template v-else-if="type === 'student'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4 class="fw-bold text-dark m-0">{{ data.name }}</h4>
          <button type="button" class="btn-close" @click="emit('close')"></button>
        </div>

        <hr class="my-2" />

        <div class="row g-3 mb-3">
          <div class="col-6">
            <small class="text-muted d-block">Email Address</small>
            <span class="fw-semibold small">{{ data.email }}</span>
          </div>
          <div class="col-6">
            <small class="text-muted d-block">Student ID</small>
            <span class="fw-semibold">{{ data.student_id }}</span>
          </div>
          <div class="col-6">
            <small class="text-muted d-block">CGPA</small>
            <span class="fw-bold text-primary">{{ data.cgpa }}</span>
          </div>
          <div class="col-6">
            <small class="text-muted d-block">Course Level</small>
            <span class="fw-semibold">{{ data.level }}</span>
          </div>
          <div class="col-12" v-if="data.resume">
            <small class="text-muted d-block mb-1">Resume / CV</small>
            <a :href="`http://127.0.0.1:5000/api/resumes/${data.resume}`" target="_blank"
              class="btn btn-sm btn-outline-primary w-100">
              View Resume
            </a>
          </div>
        </div>
      </template>

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

.detail-card {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
}
</style>