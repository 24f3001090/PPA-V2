<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import DetailCard from '@/components/DetailCard.vue'

const token = localStorage.getItem('token')

const student = ref({})
const drives = ref([])
const applications = ref([])
const searchQuery = ref('')
const activeTab = ref('available')

const drivePicked = ref(null)
const alertMsg = ref('')
const errorMsg = ref('')

const fetchDashboardData = async () => {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/student/dashboard?q=${searchQuery.value}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.msg)

    student.value = data.student
    drives.value = data.drives
  } catch (err) {
    errorMsg.value = err.message
  }
}

const fetchApplications = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/student/applications', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) applications.value = await res.json()
}

const applyToDrive = async (dId) => {
  alertMsg.value = ''
  errorMsg.value = ''
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/student/apply/${dId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.msg)

    alertMsg.value = data.msg
    fetchDashboardData()
    fetchApplications()
  } catch (err) {
    errorMsg.value = err.message
  }
}

const openDetailModal = (drive) => {
  drivePicked.value = { ...drive }
}

onMounted(() => {
  fetchDashboardData()
  fetchApplications()
})
</script>

<template>
  <div class="page-container">
    <Navbar />

    <main class="main-content">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold text-dark m-0">Welcome, {{ student.name }}</h2>
          <small class="text-muted">CGPA: {{ student.cgpa }} | Course Level: {{ student.level }}</small>
        </div>
      </div>

      <div v-if="alertMsg" class="alert alert-success p-2 small mb-3">{{ alertMsg }}</div>
      <div v-if="errorMsg" class="alert alert-danger p-2 small mb-3">{{ errorMsg }}</div>

      <!-- Navigation Tabs -->
      <div class="btns mb-4">
        <button class="btn btn-sm" :class="activeTab === 'available' ? 'btn-primary' : 'btn-outline-primary'"
          @click="activeTab = 'available'">
          Available Drives
        </button>
        <button class="btn btn-sm" :class="activeTab === 'applied' ? 'btn-primary' : 'btn-outline-primary'"
          @click="activeTab = 'applied'">
          My Applications ({{ applications.length }})
        </button>
      </div>

      <!-- Available Drives Tab -->
      <div v-if="activeTab === 'available'" class="card p-3 border-0 shadow-sm">
        <div class="d-flex justify-content-between mb-3">
          <h5 class="fw-bold m-0">Approved Job Opportunities</h5>
          <input type="text" v-model="searchQuery" @input="fetchDashboardData" class="form-control form-control-sm w-25"
            placeholder="Search by role or company..." />
        </div>

        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Package</th>
              <th>Experience Required</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td class="fw-semibold">{{ d.company_name }}</td>
              <td>{{ d.role }}</td>
              <td class="text-success fw-bold">{{ d.package }}</td>
              <td>{{ d.experience }}</td>
              <td>
                <button @click="openDetailModal(d)" class="btn btn-sm btn-outline-info me-2">View</button>
                <button v-if="!d.already_applied" @click="applyToDrive(d.id)" class="btn btn-sm btn-primary">Apply
                  Now</button>
                <button v-else class="btn btn-sm btn-secondary" disabled>Applied</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- My Applications Tab -->
      <div v-if="activeTab === 'applied'" class="card p-3 border-0 shadow-sm">
        <h5 class="fw-bold mb-3">Applied Drive Tracking</h5>
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>App ID</th>
              <th>Company</th>
              <th>Role</th>
              <th>Package</th>
              <th>Track Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in applications" :key="a.a_id">
              <td>{{ a.application_id }}</td>
              <td class="fw-semibold">{{ a.company_name }}</td>
              <td>{{ a.role }}</td>
              <td class="text-success fw-bold">{{ a.package }}</td>
              <td><button @click="openTrackerModal(a)" class="btn btn-sm btn-outline-success">
                  Track Status
                </button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modals -->
      <DetailCard v-if="drivePicked" type="drive" :data="drivePicked" :isEditable="false"
        @close="drivePicked = null" />
    </main>

    <Footer />
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f4f7fa;
}

.main-content {
  flex: 1;
  padding: 32px 40px;
}
</style>