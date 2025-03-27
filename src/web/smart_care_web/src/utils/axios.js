import axios from 'axios';
import config from '../config';
import router from '../router';
import { ElMessage } from 'element-plus';

// 创建axios实例
const instance = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 5000,
    withCredentials: true,  // 允许跨域请求携带cookie
    headers: {
        'Content-Type': 'application/json'
    }
});

// 获取CSRF Token的函数
const getCSRFToken = () => {
    // 从cookie中获取csrftoken
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// 请求拦截器
instance.interceptors.request.use(
    config => {
        // 确保所有请求都以 /api 开头
        if (!config.url.startsWith('/api/')) {
            config.url = `/api${config.url.startsWith('/') ? '' : '/'}${config.url}`;
        }

        // 为非GET请求添加CSRF Token
        if (config.method !== 'get') {
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            }
        }
        
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器
instance.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，清除本地存储并跳转到登录页
                    localStorage.removeItem('user');
                    router.push('/login');
                    break;
                case 403:
                    if (error.response.data.detail && error.response.data.detail.includes('CSRF')) {
                        // CSRF错误，尝试重新获取token并重试请求
                        const originalRequest = error.config;
                        const csrfToken = getCSRFToken();
                        if (csrfToken) {
                            originalRequest.headers['X-CSRFToken'] = csrfToken;
                            return instance(originalRequest);
                        }
                    }
                    // 如果是在登录页面收到403，说明已经登录
                    if (router.currentRoute.value.path === '/login') {
                        // 获取用户信息
                        instance.get('/api/users/info/')
                            .then(response => {
                                localStorage.setItem('user', JSON.stringify(response.data));
                                router.push('/dashboard');
                            })
                            .catch(() => {
                                // 如果获取用户信息失败，清除本地存储
                                localStorage.removeItem('user');
                            });
                    } else {
                        ElMessage.error('没有权限访问此资源');
                    }
                    break;
                default:
                    console.error('API请求错误:', error);
                    
                    // 判断是否为登录页面的checkLoginStatus请求
                    const isLoginPageCheckStatus = 
                        router.currentRoute.value.path === '/login' && 
                        error.config.url.includes('/api/users/info/');
                    
                    // 如果不是登录页面的checkLoginStatus请求，则显示错误信息
                    if (!isLoginPageCheckStatus) {
                        // 优先使用后端返回的错误信息
                        const errorMessage = error.response.data.error || 
                                             error.response.data.message || 
                                             error.response.data.detail || 
                                             '请求失败';
                        ElMessage.error(errorMessage);
                    }
            }
        }
        return Promise.reject(error);
    }
);

export default instance; 