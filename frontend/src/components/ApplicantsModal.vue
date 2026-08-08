<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
    driveId: {
        type: [Number, String],
        required: true
    },
    driveRole: {
        type: String,
        default: 'Drive'
    },
    isAdmin: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['close', 'open-student-modal', 'refresh-drives'])

const token = localStorage.getItem('token')
const applicants = ref([])
const isLoading = ref(true)

const fetchApplicants = async () => {
    isLoading.value = true
    const endpoint = props.isAdmin
        ? `http://127.0.0.1:5000/api/admin/drive/${props.driveId}/applicants`
        : `http://127.0.0.1:5000/api/company/drive/${props.driveId}/applicants`

    const res = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
        const data = await res.json()
        applicants.value = data.applicants || []
    }
    isLoading.value = false
}

const updateApplicantStatus = async (aId, status, intDate = null) => {
    const endpoint = props.isAdmin
        ? `http://127.0.0.1:5000/api/admin/application/${aId}`
        : `http://127.0.0.1:5000/api/company/application/${aId}`

    await fetch(endpoint, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status, int_date: intDate })
    })
    fetchApplicants()
}

const scheduleInterview = async (applicant) => {
    if (!applicant.temp_int_date) return
    await updateApplicantStatus(applicant.a_id, 'Interview Scheduled', applicant.temp_int_date)
}

onMounted(() => {
    fetchApplicants()
})
</script>

<template>
    <div class="modal-overlay" @click.self="emit('close')">
        <div class="card applicants-card shadow-lg border-0 p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="fw-bold text-dark m-0">
                    Applicants for <span class="text-primary">{{ driveRole }}</span>
                </h4>
                <button type="button" class="btn-close" @click="emit('close')"></button>
            </div>

            <hr class="my-2 mb-3" />

            <div v-if="isLoading" class="text-center py-4 text-muted">
                Loading applicants...
            </div>

            <div v-else-if="!applicants.length" class="text-center py-4 text-muted">
                No applications received for this drive yet.
            </div>

            <div v-else class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>CGPA</th>
                            <th>Status</th>
                            <th>Interview Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="a in applicants" :key="a.a_id">
                            <td>
                                <div class="fw-semibold">
                                    {{ a.name }}
                                    <button @click="emit('open-student-modal', a)"
                                        class="btn btn-sm btn-outline-primary p-1"
                                        title="View Student Details">
                                        View
                                    </button>
                                </div>
                                <small class="text-muted">{{ a.email }}</small>
                            </td>
                            <td>{{ a.cgpa }}</td>
                            <td>
                                <span class="badge" :class="{
                                    'bg-secondary': a.status === 'Applied',
                                    'bg-info': a.status === 'Shortlisted',
                                    'bg-warning text-dark': a.status === 'Interview Scheduled',
                                    'bg-success': a.status === 'Selected',
                                    'bg-danger': a.status === 'Rejected',
                                    'bg-dark': a.status === 'College Rejected'
                                }">
                                    {{ a.status }}
                                </span>
                            </td>
                            <td>
                                <span v-if="a.int_date" class="small fw-semibold text-dark">{{ a.int_date }}</span>
                                <span v-else class="text-muted small">N/A</span>
                            </td>
                            <td>
                                <!-- ADMIN Specific Control -->
                                <template v-if="isAdmin">
                                    <!-- Show 'College Reject' ONLY if the application is not already in a terminal state -->
                                    <button v-if="!['Selected', 'Rejected', 'College Rejected'].includes(a.status)"
                                        @click="updateApplicantStatus(a.a_id, 'College Rejected')"
                                        class="btn btn-sm btn-dark">
                                        Reject
                                    </button>

                                    <!-- Status feedback when in a final state -->
                                    <span v-else class="text-muted small">
                                        {{ a.status === 'Selected' ? 'Candidate Selected' : 'Decision Finalized' }}
                                    </span>
                                </template>

                                <!-- COMPANY Specific Pipeline Controls -->
                                <template v-else>
                                    <div v-if="a.status === 'Applied'" >
                                        <button @click="updateApplicantStatus(a.a_id, 'Shortlisted')"
                                            class="btn btn-outline-primary me-1">Shortlist</button>
                                        <button @click="updateApplicantStatus(a.a_id, 'Rejected')"
                                            class="btn btn-outline-danger">Reject</button>
                                    </div>

                                    <div v-else-if="a.status === 'Shortlisted'" class="d-flex align-items-center gap-1">
                                        <input type="date" v-model="a.temp_int_date"
                                            class="form-control form-control-sm" style="width: 130px;" />
                                        <button @click="scheduleInterview(a)"
                                            class="btn btn-sm btn-warning text-dark text-nowrap"
                                            :disabled="!a.temp_int_date">Schedule</button>
                                        <button @click="updateApplicantStatus(a.a_id, 'Rejected')"
                                            class="btn btn-sm btn-outline-danger">Reject</button>
                                    </div>

                                    <div v-else-if="a.status === 'Interview Scheduled'">
                                        <button @click="updateApplicantStatus(a.a_id, 'Selected', a.int_date)"
                                            class="btn btn-outline-success me-1">Select</button>
                                        <button @click="updateApplicantStatus(a.a_id, 'Rejected', a.int_date)"
                                            class="btn btn-outline-danger">Reject</button>
                                    </div>

                                    <span v-else class="text-muted small">Finalized</span>
                                </template>
                            </td>
                        </tr>
                    </tbody>
                </table>
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

.applicants-card {
    width: 95%;
    max-width: 850px;
    max-height: 85vh;
    overflow-y: auto;
    background: white;
    border-radius: 12px;
}
</style>