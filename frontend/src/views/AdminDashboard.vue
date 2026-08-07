<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const token = localStorage.getItem('token')
const activeTab = ref('companies') // 'companies', 'drives', 'students'

const stats = ref({})
const companies = ref([])
const drives = ref([])
const students = ref([])

const companySearch = ref('')
const studentSearch = ref('')

const fetchStats = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/admin/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) stats.value = await res.json()
}

const fetchCompanies = async () => {
  const res = await fetch(`http://127.0.0.1:5000/api/admin/companies?q=${companySearch.value}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) companies.value = await res.json()
}

const fetchDrives = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/admin/drives', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) drives.value = await res.json()
}

const fetchStudents = async () => {
  const res = await fetch(`http://127.0.0.1:5000/api/admin/students?q=${studentSearch.value}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) students.value = await res.json()
}

const updateCompanyStatus = async (cId, status) => {
  await fetch(`http://127.0.0.1:5000/api/admin/company/${cId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ status })
  })
  fetchCompanies()
  fetchStats()
}

const toggleCompanyBlacklist = async (cId, currentStatus) => {
  await fetch(`http://127.0.0.1:5000/api/admin/company/${cId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ blacklisted: !currentStatus })
  })
  fetchCompanies()
}

const updateDriveStatus = async (dId, status) => {
  await fetch(`http://127.0.0.1:5000/api/admin/drive/${dId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ status })
  })
  fetchDrives()
  fetchStats()
}

const toggleStudentBlacklist = async (sId) => {
  await fetch(`http://127.0.0.1:5000/api/admin/student/${sId}/blacklist`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  fetchStudents()
}

onMounted(() => {
  fetchStats()
  fetchCompanies()
  fetchDrives()
  fetchStudents()
})
</script>

<template>
  <div class="page-container">
    <Navbar />

    <main class="main-content">
      <h2 class="fw-bold text-dark mb-4">Good to see you!</h2>

      <!-- Metrics Row -->
      <div class="d-flex justify-content-between mb-4">
          <div class="stats-circle card p-3 border-0 shadow-sm">
            <small class="text-muted fw-semibold">Students</small>
            <h3 class="fw-bold text-primary m-0">{{ stats.total_students || 0 }}</h3>
         </div>
          <div class="stats-circle card p-3 border-0 shadow-sm">
            <small class="text-muted fw-semibold">Companies</small>
            <h3 class="fw-bold text-success m-0">{{ stats.total_companies || 0 }}</h3>
        </div>
          <div class="stats-circle card p-3 border-0 shadow-sm">
            <small class="text-muted fw-semibold">Job Drives</small>
            <h3 class="fw-bold text-info m-0">{{ stats.total_drives || 0 }}</h3>
        </div>
          <div class="stats-circle card p-3 border-0 shadow-sm">
            <small class="text-muted fw-semibold">Applications</small>
            <h3 class="fw-bold text-warning m-0">{{ stats.total_applications || 0 }}</h3>
        </div>
      </div>

      <!-- Management Navigation Tabs -->
      <div class="btns mr-2 mb-3">
        <button class="btn btn-sm" :class="activeTab === 'companies' ? 'btn-primary' : 'btn-outline-primary'"
          @click="activeTab = 'companies'">Manage Companies</button>
        <button class="btn btn-sm" :class="activeTab === 'drives' ? 'btn-primary' : 'btn-outline-primary'"
          @click="activeTab = 'drives'">Manage Drives</button>
        <button class="btn btn-sm" :class="activeTab === 'students' ? 'btn-primary' : 'btn-outline-primary'"
          @click="activeTab = 'students'">Manage Students</button>
      </div>

      <!-- Companies Tab -->
      <div v-if="activeTab === 'companies'" class="card p-3 border-0 shadow-sm">
        <div class="d-flex justify-content-between mb-3">
          <h5 class="fw-bold m-0">Company Approvals & Management</h5>
          <input type="text" v-model="companySearch" @input="fetchCompanies" class="form-control form-control-sm w-25"
            placeholder="Search company name..." />
        </div>
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>{{ c.company_id }}</td>
              <td class="fw-semibold">{{ c.name }}</td>
              <td>{{ c.email }}</td>
              <td>
                <span class="badge" :class="c.status === 'Approved' ? 'bg-success' : 'bg-warning'">{{ c.status }}</span>
                <span v-if="c.blacklisted" class="badge bg-danger ms-1">Blacklisted</span>
              </td>
              <td>
                <button v-if="c.status !== 'Approved'" @click="updateCompanyStatus(c.id, 'Approved')"
                  class="btn btn-sm btn-outline-success me-2">Approve</button>
                <button v-if="c.status == 'Pending'" @click="updateCompanyStatus(c.id, 'Rejected')"
                  class="btn btn-sm btn-outline-danger me-2">Reject</button>
                <button @click="toggleCompanyBlacklist(c.id, c.blacklisted)" class="btn btn-sm btn-outline-dark">
                  {{ c.blacklisted ? 'Whitelist' : 'Blacklist' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Drives Tab -->
      <div v-if="activeTab === 'drives'" class="card p-3 border-0 shadow-sm">
        <h5 class="fw-bold mb-3">Placement Drive Approvals</h5>
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Role</th>
              <th>Package</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.drive_id }}</td>
              <td class="fw-semibold">{{ d.company_name }}</td>
              <td>{{ d.role }}</td>
              <td>{{ d.package }}</td>
              <td>
                <span class="badge" :class="d.status === 'Approved' ? 'bg-success' : 'bg-warning'">{{ d.status }}</span>
              </td>
              <td>
                <button v-if="d.status !== 'Approved'" @click="updateDriveStatus(d.id, 'Approved')"
                  class="btn btn-sm btn-outline-success me-1">Approve</button>
                <button v-if="d.status !== 'Rejected'" @click="updateDriveStatus(d.id, 'Rejected')"
                  class="btn btn-sm btn-outline-danger me-1">Reject</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Students Tab -->
      <div v-if="activeTab === 'students'" class="card p-3 border-0 shadow-sm">
        <div class="d-flex justify-content-between mb-3">
          <h5 class="fw-bold m-0">Student Management</h5>
          <input type="text" v-model="studentSearch" @input="fetchStudents" class="form-control form-control-sm w-25"
            placeholder="Search student..." />
        </div>
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>CGPA</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td>{{ s.student_id }}</td>
              <td class="fw-semibold">{{ s.name }}</td>
              <td>{{ s.email }}</td>
              <td>{{ s.cgpa }}</td>
              <td>
                <span :class="s.blacklisted ? 'badge bg-danger' : 'badge bg-success'">
                  {{ s.blacklisted ? 'Blacklisted' : 'Active' }}
                </span>
              </td>
              <td>
                <button @click="toggleStudentBlacklist(s.id)" class="btn btn-sm"
                  :class="s.blacklisted ? 'btn-outline-success' : 'btn-outline-dark'">
                  {{ s.blacklisted ? 'Whitelist' : 'Blacklist' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
.stats-circle{
  width:120px;
  height:120px;
  border-radius: 50%;
  text-align: center;
  display:flex;
  flex-direction: column;
  justify-content: center;
}

.stats-circle:hover {
    background-color: aliceblue;
}

.btns{
  width: 100%;
}
.btns .btn{
  width: 10%;
  margin-right: 4px;
}
</style>