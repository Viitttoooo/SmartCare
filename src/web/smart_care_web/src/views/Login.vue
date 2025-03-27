<!-- src/views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-container">
        <img src="../assets/logo-transparent.png" alt="Logo" class="logo-image" />
      </div>
      
      <!-- 登录表单 -->
      <div v-if="currentView === 'login'" class="form-container">
        <h2 class="form-title">欢迎回来</h2>
        <p class="form-subtitle">请输入您的账号信息进行登录</p>
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="loginRules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
              prefix-icon="User"
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              class="custom-input"
            />
          </el-form-item>
          
          <div class="forgot-password">
            <el-button type="text" @click="switchView('forgot')" class="text-button">
              忘记密码?
            </el-button>
          </div>
          
          <el-form-item>
            <el-button type="primary" @click="handleLogin" class="login-button">
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="divider">
          <span>没有账号?</span>
        </div>
        
        <el-button type="default" @click="switchView('register')" class="register-button">
          注册新账号
        </el-button>
      </div>
      
      <!-- 注册表单 -->
      <div v-if="currentView === 'register'" class="form-container">
        <div class="form-header">
          <el-button type="text" @click="switchView('login')" class="back-button">
            <el-icon><ArrowLeft /></el-icon> 返回登录
          </el-button>
          <h2 class="form-title">用户注册</h2>
          <p class="form-subtitle">创建您的账号</p>
        </div>
        
        <el-form 
          ref="registerFormRef" 
          :model="registerForm" 
          :rules="registerRules"
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请设置用户名"
              prefix-icon="User"
              class="custom-input"
            />
          </el-form-item>
          
          <div class="name-row">
            <el-form-item label="姓" prop="lastName" class="name-item">
              <el-input 
                v-model="registerForm.lastName" 
                placeholder="请输入姓"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item label="名" prop="firstName" class="name-item">
              <el-input 
                v-model="registerForm.firstName" 
                placeholder="请输入名"
                class="custom-input"
              />
            </el-form-item>
          </div>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email" 
              placeholder="请输入邮箱"
              prefix-icon="Message"
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请设置密码"
              prefix-icon="Lock"
              show-password
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码"
              prefix-icon="Lock"
              show-password
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleRegister" class="login-button">
              注册
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 忘记密码表单 -->
      <div v-if="currentView === 'forgot'" class="form-container">
        <div class="form-header">
          <el-button type="text" @click="switchView('login')" class="back-button">
            <el-icon><ArrowLeft /></el-icon> 返回登录
          </el-button>
          <h2 class="form-title">忘记密码</h2>
          <p class="form-subtitle">重置您的登录密码</p>
        </div>
        
        <div v-if="!resetRequested">
          <p class="tip-text">请输入您的用户名，我们将向管理员提交密码重置请求</p>
          <el-form 
            ref="forgotFormRef" 
            :model="forgotForm" 
            :rules="forgotRules"
            label-position="top"
            @submit.prevent="handleForgotPassword"
          >
            <el-form-item label="用户名" prop="username">
              <el-input 
                v-model="forgotForm.username" 
                placeholder="请输入用户名"
                prefix-icon="User"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleForgotPassword" class="login-button">
                提交重置请求
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div v-else class="reset-message">
          <el-icon class="success-icon"><SuccessFilled /></el-icon>
          <h3>请求已提交</h3>
          <p>该账号的重置密码请求已提交给管理员，请等待管理员批复或联系管理员</p>
          <el-button type="default" @click="switchView('login')" class="back-login-button">
            返回登录
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock, ArrowLeft, Message, SuccessFilled } from '@element-plus/icons-vue';
import http from '../utils/axios';

const router = useRouter();
const loginFormRef = ref(null);
const registerFormRef = ref(null);
const forgotFormRef = ref(null);
const currentView = ref('login'); // 'login', 'register', 'forgot'
const resetRequested = ref(false);

const loginForm = reactive({
  username: '',
  password: ''
});

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  firstName: '',
  lastName: '',
  email: ''
});

const forgotForm = reactive({
  username: ''
});

// 验证两次密码是否一致
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
};

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  firstName: [
    { required: true, message: '请输入名', trigger: 'blur' }
  ],
  lastName: [
    { required: true, message: '请输入姓', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
};

const forgotRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ]
};

// 切换视图
const switchView = (view) => {
  currentView.value = view;
  resetRequested.value = false;
};

// 检查登录状态
const checkLoginStatus = async () => {
  try {
    const response = await http.get('/api/users/info/');
    if (response.status === 200) {
      localStorage.setItem('user', JSON.stringify(response.data));
      router.push('/dashboard');
    }
  } catch (error) {
    // 静默处理错误，不显示任何提示
    localStorage.removeItem('user');
  }
};

// 登录处理
const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await http.post('/users/login/', {
          username: loginForm.username,
          password: loginForm.password
        });
        const userData = response.data;
        localStorage.setItem('user', JSON.stringify(userData));
        if (userData.token) {
          localStorage.setItem('token', userData.token);
        }
        
        router.push('/dashboard');
      } catch (error) {
        console.error('登录失败:', error);
        // 处理403错误和其他错误
        if (error.response) {
          if (error.response.status === 403 && error.response.data.error === "账号已被禁用") {
            ElMessage.error('账号已被禁用，请联系管理员');
          } else if (error.response.data && error.response.data.error) {
            ElMessage.error(error.response.data.error);
          } else {
            ElMessage.error('登录失败，请检查用户名和密码');
          }
        } else {
          ElMessage.error('登录失败，请稍后再试');
        }
      }
    }
  });
};

// 注册处理
const handleRegister = () => {
  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await http.post('/users/register/', {
          username: registerForm.username,
          password: registerForm.password,
          first_name: registerForm.firstName,
          last_name: registerForm.lastName,
          email: registerForm.email
        });
        
        ElMessage.success('注册成功，请登录');
        // 清空注册表单
        Object.keys(registerForm).forEach(key => {
          registerForm[key] = '';
        });
        // 切换到登录视图
        switchView('login');
      } catch (error) {
        console.error('注册失败:', error);
      }
    }
  });
};

// 忘记密码处理
const handleForgotPassword = () => {
  forgotFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await http.patch(`/users/put_reset/${forgotForm.username}/`);
        resetRequested.value = true;
        ElMessage.success('密码重置请求已提交');
      } catch (error) {
        console.error('密码重置请求失败:', error);
      }
    }
  });
};

onMounted(() => {
  checkLoginStatus();
});
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: linear-gradient(135deg, #4f46e5 0%, #7f5af8 100%);
  padding: 40px 20px 100px;
  overflow-y: auto;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.login-box {
  width: 450px;
  max-width: 100%;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin: 20px auto;
  animation: fade-in 0.5s ease-in-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(127, 90, 248, 0.4);
  border-radius: 10px;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(127, 90, 248, 0.6);
}

.logo-container {
  text-align: center;
  margin-bottom: 30px;
}

.logo-image {
  height: 120px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.logo-image:hover {
  transform: scale(1.05);
}

.form-container {
  animation: slide-up 0.4s ease-out;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-title {
  text-align: center;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
  font-size: 1.75rem;
}

.form-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 25px;
  font-size: 0.95rem;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  margin-top: 10px;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(79, 70, 229, 0.25);
}

.forgot-password {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.text-button {
  padding: 0;
  font-size: 14px;
  color: #5c67d2;
  transition: all 0.3s ease;
}

.text-button:hover {
  color: #7f5af8;
  transform: translateX(2px);
}

.form-header {
  position: relative;
  margin-bottom: 25px;
}

.back-button {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  color: #5c67d2;
}

.back-button .el-icon {
  margin-right: 4px;
}

.name-row {
  display: flex;
  gap: 12px;
}

.name-item {
  flex: 1;
}

.tip-text {
  color: #606266;
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
  line-height: 1.6;
}

.reset-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin: 30px 0;
}

.success-icon {
  font-size: 56px;
  color: #67c23a;
  margin-bottom: 16px;
}

.reset-message h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.reset-message p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

.back-login-button {
  margin-top: 10px;
}

.divider {
  position: relative;
  text-align: center;
  margin: 20px 0;
}

.divider::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 0;
  width: 40%;
  height: 1px;
  background-color: #e0e0e0;
}

.divider::after {
  content: "";
  position: absolute;
  top: 50%;
  right: 0;
  width: 40%;
  height: 1px;
  background-color: #e0e0e0;
}

.divider span {
  background-color: white;
  padding: 0 10px;
  position: relative;
  z-index: 1;
  color: #666;
  font-size: 0.9rem;
}

.register-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  transition: all 0.3s ease;
}

.register-button:hover {
  border-color: #5c67d2;
  color: #5c67d2;
}

.custom-input {
  border-radius: 8px;
}

:deep(.el-input__wrapper) {
  padding: 10px 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-checkbox__label) {
  color: #666;
}
</style>