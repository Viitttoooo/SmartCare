// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/global.css'  // 导入全局样式
import './assets/styles/components.css'  // 导入组件通用样式

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.mount('#app');