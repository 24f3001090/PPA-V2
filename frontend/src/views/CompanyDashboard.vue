<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import MetricCard from '@/components/MetricCard.vue'
import DetailCard from '@/components/DetailCard.vue'

const token = localStorage.getItem('token')

const stats = ref({})
const drives = ref([])
const availableSkills = ref([])

const newDrive = ref({
    role: '',
    package: '',
    experience: '',
    skills: []
})

const company_name = ref('')
const selectedDriveRole = ref('')
const selectedDriveId = ref(null)
const skillInput = ref('')
const applicants = ref([])

const selectedDriveForModal = ref(null)

const alertMsg = ref('')
const errorMsg = ref('')

const fetchDashboardData = async () => {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/company/dashboard', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.msg)

        stats.value = data.stats
        drives.value = data.drives
        availableSkills.value = data.available_skills
        company_name.value = data.company_name
    } catch (err) {
        errorMsg.value = err.message
    }
}

const handleCreateDrive = async () => {
    alertMsg.value = ''
    errorMsg.value = ''
    try {
        const res = await fetch('http://127.0.0.1:5000/api/company/drives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(newDrive.value)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.msg)

        alertMsg.value = data.msg
        newDrive.value = { role: '', package: '', experience: '', skill_ids: [] }
        fetchDashboardData()
    } catch (err) {
        errorMsg.value = err.message
    }
}

const addSkill = () => {
    const name = skillInput.value.trim()
    if (!name) return

    const isDuplicate = newDrive.value.skills.some(
        s => s.toLowerCase() === name.toLowerCase()
    )

    if (!isDuplicate) {
        newDrive.value.skills.push(name)
    }

    skillInput.value = ''
}


const removeSkill = (index) => {
    newDrive.value.skills.splice(index, 1)
}

const toggleDriveStatus = async (dId, currentStatus) => {
    const newStatus = currentStatus === 'Closed' ? 'Approved' : 'Closed'
    await fetch(`http://127.0.0.1:5000/api/company/drive/${dId}/status`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
    })
    fetchDashboardData()
}

const viewApplicants = async (dId) => {
    selectedDriveId.value = dId
    const res = await fetch(`http://127.0.0.1:5000/api/company/drive/${dId}/applicants`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
        const data = await res.json()
        selectedDriveRole.value = data.drive_role
        applicants.value = data.applicants
    }
}

const updateApplicant = async (aId, status, intDate = null) => {
    await fetch(`http://127.0.0.1:5000/api/company/application/${aId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status, int_date: intDate })
    })
    if (selectedDriveId.value) {
        viewApplicants(selectedDriveId.value)
    }
}

const openDetailModal = (drive) => {
    selectedDriveForModal.value = { ...drive }
}

const updateDriveSkillsOnServer = async (updatedSkills) => {
    selectedDriveForModal.value.skills = updatedSkills
    await fetch(`http://127.0.0.1:5000/api/company/drive/${selectedDriveForModal.value.id}/skills`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ skills: updatedSkills })
    })
    fetchDashboardData()
}

onMounted(() => {
    fetchDashboardData()
})
</script>

<template>
    <div class="page-container">
        <Navbar />

        <main class="main-content">
            <h2 class="fw-bold text-dark mb-4">Welcome {{ company_name }}</h2>

            <div v-if="alertMsg" class="alert alert-success p-2 small mb-3">{{ alertMsg }}</div>
            <div v-if="errorMsg" class="alert alert-danger p-2 small mb-3">{{ errorMsg }}</div>

            <!-- Metrics Row -->
            <div class="d-flex justify-content-between gap-3 mb-4">
                <MetricCard label="Job Drives Posted" :value="stats.total_drives" variant="primary" />
                <MetricCard label="Applications Received" :value="stats.total_applications" variant="info" />
                <MetricCard label="Shortlisted / Selected" :value="stats.shortlisted_count" variant="success" />
            </div>

            <div class="row g-4">
                <!-- Create Drive Form -->
                <div class="col-md-4">
                    <div class="card p-3 border-0 shadow-sm">
                        <h5 class="fw-bold mb-3">Post New Job Drive</h5>
                        <form @submit.prevent="handleCreateDrive">
                            <div class="mb-2">
                                <label class="form-label small fw-semibold">Job Role</label>
                                <input type="text" v-model="newDrive.role" class="form-control form-control-sm"
                                    placeholder="e.g. SDE-1" required />
                            </div>

                            <div class="mb-2">
                                <label class="form-label small fw-semibold">Package (LPA)</label>
                                <input type="text" v-model="newDrive.package" class="form-control form-control-sm"
                                    placeholder="e.g. 12 LPA" required />
                            </div>

                            <div class="mb-2">
                                <label class="form-label small fw-semibold">Experience Required</label>
                                <input type="text" v-model="newDrive.experience" class="form-control form-control-sm"
                                    placeholder="e.g. 0-2 Years" required />
                            </div>

                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Required Skills</label>

                                <div class="d-flex gap-2 mb-2">
                                    <input type="text" v-model="skillInput" @keyup.enter.prevent="addSkill"
                                        class="form-control form-control-sm"
                                        placeholder="Type skill (e.g. Python) and click + or press Enter" />

                                    <button type="button" @click="addSkill"
                                        class="btn btn-outline-primary btn-sm px-3 fw-bold"
                                        :disabled="!skillInput.trim()">
                                        +
                                    </button>
                                </div>

                                <!-- Selected Skills -->
                                <div class="d-flex flex-wrap gap-1" v-if="newDrive.skills.length">
                                    <span v-for="(skillName, index) in newDrive.skills" :key="index"
                                        class="badge bg-primary d-flex align-items-center gap-1 py-1 px-2">
                                        {{ skillName }}
                                        <span @click="removeSkill(index)" class="ms-1 text-white-50 fw-bold"
                                            style="cursor: pointer;">
                                            &times;
                                        </span>
                                    </span>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary btn-sm w-100">Create Drive</button>
                        </form>
                    </div>
                </div>



                <!-- Drive List -->
                <div class="col-md-8">
                    <div class="card p-3 border-0 shadow-sm mb-4">
                        <h5 class="fw-bold mb-3">Your Posted Drives</h5>
                        <table class="table table-hover align-middle">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Role</th>
                                    <th>Package</th>
                                    <th>Applicants</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="d in drives" :key="d.id">
                                    <td>{{ d.drive_id }}</td>
                                    <td class="fw-semibold">{{ d.role }}</td>
                                    <td>{{ d.package }}</td>
                                    <td>
                                        <span class="badge bg-secondary">{{ d.applicant_count }}</span>
                                    </td>
                                    <td>
                                        <span class="badge"
                                            :class="d.status === 'Approved' || d.status === 'Active' ? 'bg-success' : 'bg-warning'">
                                            {{ d.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <button @click="viewApplicants(d.id)"
                                            class="btn btn-sm btn-outline-primary me-3">Applicants</button>
                                        <button @click="openDetailModal(d)"
                                            class="btn btn-sm btn-outline-info me-3">View</button>
                                        <button @click="toggleDriveStatus(d.id, d.status)"
                                            class="btn btn-sm btn-outline-secondary">
                                            {{ d.status === 'Closed' ? 'Reopen' : 'Close' }}
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Applicants Table -->
                    <div v-if="selectedDriveId" class="card p-3 border-0 shadow-sm">
                        <h5 class="fw-bold mb-3">Applicants for: <span class="text-primary">{{ selectedDriveRole
                        }}</span></h5>

                        <p v-if="!applicants.length" class="text-muted small">No applications received yet for this
                            drive.</p>

                        <table v-else class="table table-hover align-middle">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>CGPA</th>
                                    <th>Status</th>
                                    <th>Schedule Interview</th>
                                    <th>Action Pipeline</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="a in applicants" :key="a.a_id">
                                    <td>
                                        <div class="fw-semibold">{{ a.student_name }}</div>
                                        <small class="text-muted">{{ a.student_email }}</small>
                                    </td>
                                    <td>{{ a.cgpa }}</td>
                                    <td>
                                        <span class="badge" :class="{
                                            'bg-info': a.status === 'Shortlisted',
                                            'bg-warning text-dark': a.status === 'Interviewed',
                                            'bg-success': a.status === 'Selected',
                                            'bg-danger': a.status === 'Rejected',
                                            'bg-dark': a.status === 'College Rejected',
                                            'bg-secondary': a.status === 'Applied' || a.status === 'Pending'
                                        }">
                                            {{ a.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <input type="date" :value="a.int_date"
                                            @change="(e) => updateApplicant(a.a_id, a.status, e.target.value)"
                                            class="form-control form-control-sm" style="max-width: 140px;" />
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button @click="updateApplicant(a.a_id, 'Shortlisted', a.int_date)"
                                                class="btn btn-outline-info" title="Shortlist">Shortlist</button>
                                            <button @click="updateApplicant(a.a_id, 'Interviewed', a.int_date)"
                                                class="btn btn-outline-warning text-dark"
                                                title="Mark Interviewed">Interviewed</button>
                                            <button @click="updateApplicant(a.a_id, 'Selected', a.int_date)"
                                                class="btn btn-outline-success" title="Select">Select</button>
                                            <button @click="updateApplicant(a.a_id, 'Rejected', a.int_date)"
                                                class="btn btn-outline-danger" title="Reject">Reject</button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <DetailCard v-if="selectedDriveForModal" :drive="selectedDriveForModal" :isEditable="true"
                @close="selectedDriveForModal = null" @update-skills="updateDriveSkillsOnServer" />
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