<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, watchEffect } from 'vue'

const router = useRouter()
const route = useRoute()

const token = ref(localStorage.getItem('token'))


watchEffect(() => {
  token.value = localStorage.getItem('token')
})

const goToLogin = () => router.push('/login')
const goToRegister = () => router.push('/register')

const handleLogout = () => {
  localStorage.clear()
  token.value = null
  router.push('/login')
}
</script>

<template>
  <header class="navbar-wrapper">
    <!-- Brand Logo and Title -->
    <router-link to="/" class="brand-link">
      <div class="brand-icon">🎓</div>
      <div>
        <h1 class="brand-title">Tenacious</h1>
        <span class="brand-subtitle">Placement Portal</span>
      </div>
    </router-link>

    <!-- Buttons -->
    <div class="d-flex gap-2">
      <template v-if="!token">
        <button v-if="route.path !== '/login'" @click="goToLogin" class="btn btn-outline-primary btn-sm px-3 fw-medium">
          Login
        </button>

        <button v-if="route.path !== '/register'" @click="goToRegister"
          class="btn btn-outline-primary btn-sm px-3 fw-medium">
          Register
        </button>
      </template>

      <template v-else>
        <button @click="handleLogout" class="btn btn-danger btn-sm px-3 fw-medium">
          Logout
        </button>
      </template>
    </div>
  </header>
</template>

<style scoped>
.navbar-wrapper {
  background: #ffffff;
  padding: 14px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand-icon {
  background: #2563eb;
  color: white;
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.1;
}

.brand-subtitle {
  font-size: 12px;
  color: #64748b;
}
</style>