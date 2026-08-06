<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
const router = useRouter();
const role = ref('student');

const form = ref({
    name: '',
    email: '',
    password: '',
    level: 'UG',
    cgpa: ''
});

const resumeFile = ref(null);

const successMsg = ref('');
const errorMsg = ref('');

const handleFileUpload = (event) => {
    resumeFile.value = event.target.files[0];
};

const submitRegister = async () => {
    errorMsg.value = '';
    successMsg.value = '';

    const endpoint = role.value === 'student'
        ? 'http://127.0.0.1:5000/api/auth/register/student'
        : 'http://127.0.0.1:5000/api/auth/register/company';

    try {
        let requestBody;
        let headers = {};

        if (role.value === 'student') {
            const formData = new FormData();
            formData.append('name', form.value.name);
            formData.append('email', form.value.email);
            formData.append('password', form.value.password);
            formData.append('level', form.value.level);
            formData.append('cgpa', form.value.cgpa);

            if (resumeFile.value) {
                formData.append('resume', resumeFile.value);
            }

            requestBody = formData;
        } else {
            headers['Content-Type'] = 'application/json';
            requestBody = JSON.stringify(form.value);
        }

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: headers,
            body: requestBody
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.msg);

        successMsg.value = data.msg;
        setTimeout(() => router.push('/login'), 1500);
    } catch (err) {
        errorMsg.value = err.message;
    }
};
</script>

<template>
    <div class="page-layout bg-light">
        <Navbar />

        <main class="content-area">
            <div class="card auth-card shadow-sm border-0 p-4">
                <h4 class="fw-bold text-center mb-3">Create Account</h4>

                <div v-if="successMsg" class="alert alert-success p-2 small">{{ successMsg }}</div>
                <div v-if="errorMsg" class="alert alert-danger p-2 small">{{ errorMsg }}</div>

                <!-- Role Toggle Switch -->
                <div class="mb-3">
                    <label class="form-label fw-semibold small">I am registering as a:</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" value="student" v-model="role" id="roleStudent">
                        <label class="btn btn-outline-primary btn-sm" for="roleStudent">Student</label>

                        <input type="radio" class="btn-check" value="company" v-model="role" id="roleCompany">
                        <label class="btn btn-outline-primary btn-sm" for="roleCompany">Company</label>
                    </div>
                </div>

                <form @submit.prevent="submitRegister" enctype="multipart/form-data">
                    <div class="mb-2">
                        <label class="form-label small fw-semibold">
                            {{ role === 'student' ? 'Full Name' : 'Company Name' }}
                        </label>
                        <input type="text" v-model="form.name" class="form-control form-control-sm" required />
                    </div>

                    <div class="mb-2">
                        <label class="form-label small fw-semibold">Email Address</label>
                        <input type="email" v-model="form.email" class="form-control form-control-sm" required />
                    </div>

                    <div class="mb-2">
                        <label class="form-label small fw-semibold">Password</label>
                        <input type="password" v-model="form.password" class="form-control form-control-sm" required />
                    </div>

                    <!-- Student-Specific Fields -->
                    <div v-if="role === 'student'">
                        <div class="mb-2">
                            <label class="form-label small fw-semibold">Level</label>
                            <select v-model="form.level" class="form-select form-select-sm">
                                <option value="foundation">Foundation</option>
                                <option value="diploma">Diploma</option>
                                <option value="degree">Degree</option>
                            </select>
                        </div>

                        <div class="mb-2">
                            <label class="form-label small fw-semibold">CGPA</label>
                            <input type="number" step="0.01" min="0" max="10" v-model="form.cgpa"
                                class="form-control form-control-sm" placeholder="e.g. 8.5" required />
                        </div>

                        <div class="mb-2" v-if="role === 'student'">
                            <label class="form-label small fw-semibold">Upload Resume (PDF, DOC, JPG)</label>
                            <input type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" @change="handleFileUpload"
                                class="form-control form-control-sm" required />
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary btn-sm w-100 mt-3">Register</button>
                </form>
            </div>
        </main>

        <Footer />
    </div>
</template>

<style scoped>
.page-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.content-area {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.auth-card {
    width: 100%;
    max-width: 400px;
    border-radius: 10px;
}
</style>