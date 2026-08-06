<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';

const router = useRouter();

const role = ref('student');
const email = ref('');
const password = ref('');

const errorMsg = ref('');
const successMsg = ref('');

const handleLogin = async () => {
  errorMsg.value = '';
  successMsg.value = '';

  try {
    const res = await fetch('http://127.0.0.1:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        role: role.value
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.msg);

    localStorage.setItem('token', data.token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('userName', data.name);

    successMsg.value = "Login successful! Redirecting...";

    setTimeout(() => {
      if (data.role === 'admin') router.push('/admin/dashboard');
      else if (data.role === 'company') router.push('/company/dashboard');
      else router.push('/student/dashboard');
    }, 1000);

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
        <h4 class="fw-bold text-center mb-3">Portal Login</h4>

        <div v-if="successMsg" class="alert alert-success p-2 small">{{ successMsg }}</div>
        <div v-if="errorMsg" class="alert alert-danger p-2 small">{{ errorMsg }}</div>

        <div class="mb-3">
          <label class="form-label fw-semibold small">Select Role:</label>
          <div class="btn-group w-100" role="group">
            <input type="radio" class="btn-check" value="student" v-model="role" id="loginStudent">
            <label class="btn btn-outline-primary btn-sm" for="loginStudent">Student</label>

            <input type="radio" class="btn-check" value="company" v-model="role" id="loginCompany">
            <label class="btn btn-outline-primary btn-sm" for="loginCompany">Company</label>

            <input type="radio" class="btn-check" value="admin" v-model="role" id="loginAdmin">
            <label class="btn btn-outline-primary btn-sm" for="loginAdmin">Admin</label>
          </div>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-2">
            <label class="form-label small fw-semibold">Email Address</label>
            <input type="email" v-model="email" class="form-control form-control-sm" placeholder="name@example.com" required />
          </div>

          <div class="mb-3">
            <label class="form-label small fw-semibold">Password</label>
            <input type="password" v-model="password" class="form-control form-control-sm" required />
          </div>

          <button type="submit" class="btn btn-primary btn-sm w-100">Login</button>
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
  flex:1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 380px;
  border-radius: 10px;
}
</style>