// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Dashboard from '../views/Dashboard.vue';
import http from '../utils/axios';

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      // 尝试获取用户信息
      const response = await http.get('/api/users/info/');
      if (response.status === 200) {
        // 更新本地存储的用户信息
        localStorage.setItem('user', JSON.stringify(response.data));
        next();
      }
    } catch (error) {
      // 获取用户信息失败，重定向到登录页
      next('/login');
    }
  } else {
    next();
  }
});

export default router;