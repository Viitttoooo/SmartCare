<template>
  <div class="user-management">
    <!-- 搜索和筛选区域 -->
    <div class="filter-container">
      <div class="filter-section">
        <div class="section-title">用户筛选</div>
        <div class="filter-content">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户ID/用户名/姓名"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="selectedRole"
            placeholder="用户身份"
            clearable
            class="role-filter"
          >
            <el-option
              v-for="role in roles"
              :key="role.role_id"
              :label="role.role_name"
              :value="role.role_name"
            />
          </el-select>
          <el-button type="primary" @click="showAddUserDialog">
            <el-icon><Plus /></el-icon>新增用户
          </el-button>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-content">
      <el-table :data="filteredUsers" style="width: 100%" @row-click="handleRowClick">
        <el-table-column prop="id" label="用户ID" width="100" />
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column label="姓名" width="120">
          <template #default="scope">
            {{ scope.row.last_name }}{{ scope.row.first_name }}
          </template>
        </el-table-column>
        <el-table-column prop="role_name" label="用户身份" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="light">
              {{ scope.row.is_active ? '已激活' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 用户详情弹窗 -->
    <el-dialog
      v-model="userDetailVisible"
      title="用户详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">{{ selectedUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ selectedUser.username }}</el-descriptions-item>
        <el-descriptions-item label="姓">{{ selectedUser.last_name }}</el-descriptions-item>
        <el-descriptions-item label="名">{{ selectedUser.first_name }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ selectedUser.email }}</el-descriptions-item>
        <el-descriptions-item label="用户身份">{{ selectedUser.role_name }}</el-descriptions-item>
        <el-descriptions-item label="最后登录时间">
          {{ formatDateTime(selectedUser.last_login) }}
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDateTime(selectedUser.date_joined) }}
        </el-descriptions-item>
        <el-descriptions-item label="账号状态">
          {{ selectedUser.is_active ? '已激活' : '已禁用' }}
        </el-descriptions-item>
        <el-descriptions-item label="密码重置申请">
          {{ selectedUser.is_reset ? '已申请' : '未申请' }}
        </el-descriptions-item>
      </el-descriptions>
      <div class="dialog-footer">
        <el-button
          :type="selectedUser.is_reset ? 'warning' : 'info'"
          :disabled="!selectedUser.is_reset"
          @click="handleResetPassword"
        >
          重置密码
        </el-button>
        <el-button
          :type="selectedUser.is_active ? 'danger' : 'success'"
          @click="handleToggleActive"
        >
          {{ selectedUser.is_active ? '禁用' : '激活' }}
        </el-button>
      </div>
    </el-dialog>

    <!-- 新增用户弹窗 -->
    <el-dialog
      v-model="addUserVisible"
      title="新增用户"
      width="500px"
    >
      <el-form :model="newUser" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="newUser.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓">
          <el-input v-model="newUser.last_name" />
        </el-form-item>
        <el-form-item label="名">
          <el-input v-model="newUser.first_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newUser.email" />
        </el-form-item>
        <el-form-item label="用户身份" required>
          <el-select v-model="newUser.role" placeholder="请选择用户身份">
            <el-option
              v-for="role in roles"
              :key="role.role_id"
              :label="role.role_name"
              :value="role.role_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addUserVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddUser">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Plus } from '@element-plus/icons-vue';
import http from '../utils/axios';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

dayjs.extend(utc);
dayjs.extend(timezone);

const users = ref([]);
const roles = ref([]);
const searchQuery = ref('');
const selectedRole = ref('');
const userDetailVisible = ref(false);
const addUserVisible = ref(false);
const selectedUser = ref({});

const newUser = ref({
  username: '',
  password: '123456',
  first_name: '',
  last_name: '',
  email: '',
  role: ''
});

// 获取所有用户
const fetchUsers = async () => {
  try {
    const response = await http.get('/api/users/');
    users.value = response.data;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    ElMessage.error('获取用户列表失败');
  }
};

// 获取所有角色
const fetchRoles = async () => {
  try {
    const response = await http.get('/api/roles/get/');
    roles.value = response.data;
  } catch (error) {
    console.error('获取角色列表失败:', error);
    ElMessage.error('获取角色列表失败');
  }
};

// 过滤后的用户列表
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const searchText = searchQuery.value.toLowerCase();
    const idMatch = String(user.id).includes(searchText);
    const usernameMatch = user.username.toLowerCase().includes(searchText);
    const nameMatch = (user.last_name + user.first_name).toLowerCase().includes(searchText);
    const roleMatch = !selectedRole.value || selectedRole.value === '' || user.role_name === selectedRole.value;
    
    return (idMatch || usernameMatch || nameMatch) && roleMatch;
  });
});

// 格式化时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '暂无记录';
  return dayjs(dateTime).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss');
};

// 处理行点击
const handleRowClick = (row) => {
  selectedUser.value = { ...row };
  userDetailVisible.value = true;
};

// 显示新增用户弹窗
const showAddUserDialog = () => {
  newUser.value = {
    username: '',
    password: '123456',
    first_name: '',
    last_name: '',
    email: '',
    role: ''
  };
  addUserVisible.value = true;
};

// 处理重置密码
const handleResetPassword = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要将该用户的密码重置为123456吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await http.patch(`/api/users/password_reset/${selectedUser.value.id}/`);
    ElMessage.success('密码重置成功');
    selectedUser.value.is_reset = false;
  } catch (error) {
    if (error !== 'cancel') {
      console.error('密码重置失败:', error);
      ElMessage.error('密码重置失败');
    }
  }
};

// 处理激活/禁用
const handleToggleActive = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要${selectedUser.value.is_active ? '禁用' : '激活'}该用户吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    const response = await http.patch(`/api/users/change_active/${selectedUser.value.id}/`);
    selectedUser.value = response.data;
    
    // 更新列表中的用户状态
    const index = users.value.findIndex(u => u.id === selectedUser.value.id);
    if (index !== -1) {
      users.value[index] = { ...users.value[index], ...response.data };
    }
    
    ElMessage.success(`用户${selectedUser.value.is_active ? '激活' : '禁用'}成功`);
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error);
      ElMessage.error('操作失败');
    }
  }
};

// 处理新增用户
const handleAddUser = async () => {
  if (!newUser.value.username || !newUser.value.password || newUser.value.role === '') {
    ElMessage.warning('请填写必填项');
    return;
  }
  
  try {
    await http.post('/api/users/register/admin/', newUser.value);
    ElMessage.success('新增用户成功');
    addUserVisible.value = false;
    fetchUsers(); // 刷新用户列表
  } catch (error) {
    console.error('新增用户失败:', error);
    ElMessage.error('新增用户失败');
  }
};

onMounted(() => {
  fetchUsers();
  fetchRoles();
});
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.filter-container {
  margin-bottom: 20px;
}

.filter-section {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 15px;
  color: #303133;
  margin-bottom: 16px;
  font-weight: 600;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background-color: #409EFF;
  border-radius: 2px;
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 280px;
}

.role-filter {
  width: 150px;
}

.users-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.dialog-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-descriptions) {
  padding: 20px;
}

:deep(.el-descriptions__cell) {
  padding: 12px 16px;
}
</style> 