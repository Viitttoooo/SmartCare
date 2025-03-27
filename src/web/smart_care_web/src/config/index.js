// src/config/index.js
export default {
    // 开发环境API地址
    development: {
        baseURL: 'http://localhost:8000/api'
    },
    // 生产环境API地址
    production: {
        baseURL: 'https://api.example.com/api'  // 这里替换为实际的生产环境API地址
    },
    // 获取当前环境的配置
    get env() {
        return import.meta.env.MODE === 'production' ? this.production : this.development;
    },
    // 获取API基础URL
    get baseURL() {
        return this.env.baseURL;
    }
} 