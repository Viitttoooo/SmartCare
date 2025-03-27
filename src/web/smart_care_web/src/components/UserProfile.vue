<template>
  <div class="user-profile">
    <h2>个人信息</h2>
    <div class="profile-content">
      <el-form ref="formRef" :model="userInfo" :disabled="!isEditing" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" />
        </el-form-item>
        <el-form-item label="名">
          <el-input v-model="userInfo.first_name" />
        </el-form-item>
        <el-form-item label="姓">
          <el-input v-model="userInfo.last_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" type="email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-input v-model="userInfo.role_name" disabled />
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleEditClick"
        >
          {{ isEditing ? '完成修改' : '修改信息' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import http from '../utils/axios';

const userInfo = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  role_name: ''
});

const isEditing = ref(false);
const formRef = ref(null);

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await http.get('/users/info/');
    userInfo.value = response.data;
    // 更新本地存储的用户信息
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
    localStorage.setItem('user', JSON.stringify({
      ...storedUser,
      ...response.data
    }));
  } catch (error) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败');
  }
};

// 更新用户信息
const updateUserInfo = async () => {
  try {
    const response = await http.patch('/users/update/', {
      username: userInfo.value.username,
      first_name: userInfo.value.first_name,
      last_name: userInfo.value.last_name,
      email: userInfo.value.email
    });
    
    // 更新本地数据
    userInfo.value = { ...userInfo.value, ...response.data };
    
    // 更新localStorage中的用户信息
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
    localStorage.setItem('user', JSON.stringify({
      ...storedUser,
      ...response.data
    }));

    ElMessage.success('信息更新成功');
    isEditing.value = false;
  } catch (error) {
    console.error('更新用户信息失败:', error);
    ElMessage.error('更新用户信息失败');
  }
};

// 处理编辑/保存按钮点击
const handleEditClick = () => {
  if (isEditing.value) {
    // 如果正在编辑，则保存更改
    updateUserInfo();
  } else {
    // 开始编辑
    isEditing.value = true;
  }
};

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.profile-content {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
}
</style> 