import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  // Role Dashboards (Placeholders for next milestone)
  { path: '/admin/dashboard', component: () => import('@/views/AdminDashboard.vue'), meta: { role: 'admin' } },
  // { path: '/company/dashboard', component: () => import('@/views/CompanyDashboard.vue'), meta: { role: 'company' } },
  // { path: '/student/dashboard', component: () => import('@/views/StudentDashboard.vue'), meta: { role: 'student' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (to.meta.role) {
    if (!token) return next('/login');
    if (to.meta.role !== userRole) return next('/');
  }
  next();
});

export default router;