<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard-container">
    <!-- 左侧边栏 -->
    <div class="sidebar custom-scrollbar">
      <Logo />
      <el-menu
        class="sidebar-menu"
        :default-active="currentView"
        background-color="var(--primary-color)"
        text-color="var(--white)"
        active-text-color="var(--white)"
        :default-openeds="openedMenus"
        @open="handleSubMenuOpen"
        @close="handleSubMenuClose"
      >
        <!-- 首页单独展示 -->
        <el-menu-item index="home" @click="currentView = 'home'">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <!-- 客户类别 -->
        <el-sub-menu index="client-category" v-if="showClientCategory">
          <template #title>
            <el-icon><User /></el-icon>
            <span>客户</span>
          </template>
          <el-menu-item 
            v-if="user.role_name === '员工' || user.role_name === '管理员'"
            index="clients-list"
            @click="currentView = 'clients-list'"
          >
            <el-icon><User /></el-icon>
            <span>客户档案</span>
          </el-menu-item>
          <el-menu-item 
            index="health-records"
            @click="currentView = 'health-records'"
          >
            <el-icon><Files /></el-icon>
            <span>健康档案</span>
          </el-menu-item>
          <el-menu-item
            index="care-plan"
            @click="currentView = 'care-plan'"
          >
            <el-icon><List /></el-icon>
            <span>护理计划</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 预约类别 -->
        <el-sub-menu index="appointment-category" v-if="showAppointmentCategory">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>预约</span>
          </template>
          <el-menu-item
            index="appointment-management"
            @click="currentView = 'appointment-management'"
          >
            <el-icon><Calendar /></el-icon>
            <span>预约管理</span>
          </el-menu-item>
          <el-menu-item 
            index="service-management"
            @click="currentView = 'service-management'"
          >
            <el-icon><List /></el-icon>
            <span>服务管理</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 排班类别 -->
        <el-sub-menu index="schedule-category" v-if="showScheduleCategory">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>排班</span>
          </template>
          <el-menu-item 
            v-if="user.role_name === '员工' || user.role_name === '管理员'"
            index="staff-schedule"
            @click="currentView = 'staff-schedule'"
          >
            <el-icon><Calendar /></el-icon>
            <span>排班管理</span>
          </el-menu-item>
          <el-menu-item 
            v-if="user.role_name === '管理员'"
            index="shift-templates"
            @click="currentView = 'shift-templates'"
          >
            <el-icon><Document /></el-icon>
            <span>排班模板</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 膳食类别 -->
        <el-sub-menu index="diet-category" v-if="showDietCategory">
          <template #title>
            <el-icon><Bowl /></el-icon>
            <span>膳食</span>
          </template>
          <el-menu-item
            index="diet-management"
            @click="currentView = 'diet-management'"
          >
            <el-icon><Bowl /></el-icon>
            <span>膳食管理</span>
          </el-menu-item>
          <el-menu-item 
            v-if="user.role_name === '员工' || user.role_name === '管理员'"
            index="recipe-management"
            @click="currentView = 'recipe-management'"
          >
            <el-icon><Food /></el-icon>
            <span>食谱管理</span>
          </el-menu-item>
          <el-menu-item
            v-if="user.role_name === '员工' || user.role_name === '管理员'"
            index="ingredient-management"
            @click="currentView = 'ingredient-management'"
          >
            <el-icon><List /></el-icon>
            <span>食材管理</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 系统类别 -->
        <el-sub-menu index="system-category" v-if="user.role_name === '管理员'">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统</span>
          </template>
          <el-menu-item 
            index="user-management"
            @click="currentView = 'user-management'"
          >
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </div>

    <!-- 右侧主要内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <div class="top-bar">
        <div class="user-info">
          <div class="avatar-container">
            <el-avatar :size="36" :icon="User" class="user-avatar">
              {{ user.last_name ? user.last_name.charAt(0) : (user.username ? user.username.charAt(0).toUpperCase() : 'U') }}
            </el-avatar>
          </div>
          <div class="user-details">
            <span class="username">{{ user.last_name }}{{ user.first_name || (user.username || '') }}</span>
            <RoleBadge :role-name="user.role_name" />
          </div>
        </div>
        <div class="user-menu">
          <div class="notification-wrapper">
            <el-button 
              class="notification-btn" 
              @click="currentView = 'notifications'"
            >
              <el-icon><Bell /></el-icon>
              <span>通知</span>
            </el-button>
            <div v-if="hasUnreadNotifications" class="notification-badge"></div>
          </div>
          <el-dropdown @command="handleCommand">
            <el-button type="primary">
              个人资料
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item 
                  v-if="user.role_name === '客户'"
                  command="customer-file"
                >
                  客户档案
                </el-dropdown-item>
                <el-dropdown-item command="change-password">密码修改</el-dropdown-item>
                <el-dropdown-item command="logout" divided>登出</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 内容展示区 -->
      <div class="content-area custom-scrollbar">
        <component :is="currentComponent" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, provide } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { House, User, Files, ArrowDown, Calendar, List, Food, Bowl, Bell, Document, Setting } from '@element-plus/icons-vue';
import Logo from '../components/Logo.vue';
import RoleBadge from '../components/RoleBadge.vue';
import UserProfile from '../components/UserProfile.vue';
import ChangePassword from '../components/ChangePassword.vue';
import ClientProfile from '../components/ClientProfile.vue';
import ClientsList from '../components/ClientsList.vue';
import HealthRecords from '../components/HealthRecords.vue';
import StaffSchedule from '../components/StaffSchedule.vue';
import ServiceManagement from '../components/ServiceManagement.vue';
import AppointmentManagement from '../components/AppointmentManagement.vue';
import CarePlan from '../components/CarePlan.vue';
import IngredientManagement from '../components/IngredientManagement.vue';
import RecipeManagement from '../components/RecipeManagement.vue';
import DietManagement from '../components/DietManagement.vue';
import UserManagement from '../components/UserManagement.vue';
import Notifications from '../components/Notifications.vue';
import ShiftTemplates from '../components/ShiftTemplates.vue';
import Home from '../components/Home.vue';
import http from '../utils/axios';

const router = useRouter();
const user = ref({});
const currentView = ref('home');
const hasUnreadNotifications = ref(false);
let notificationPolling = null;

// 记录展开的菜单
const openedMenus = ref([]);

// 提供未读通知状态给子组件
provide('hasUnreadNotifications', hasUnreadNotifications);

// 根据当前视图计算要显示的组件
const currentComponent = computed(() => {
  switch (currentView.value) {
    case 'home':
      return Home;
    case 'profile':
      return UserProfile;
    case 'change-password':
      return ChangePassword;
    case 'customer-file':
      return user.value.role_name === '客户' ? ClientProfile : 'div';
    case 'clients-list':
      if (user.value.role_name === '员工' || user.value.role_name === '管理员') {
        return ClientsList;
      }
      return null;
    case 'health-records':
      return HealthRecords;
    case 'staff-schedule':
      if (user.value.role_name === '员工' || user.value.role_name === '管理员') {
        return StaffSchedule;
      }
      return null;
    case 'service-management':
      return ServiceManagement;
    case 'appointment-management':
      return AppointmentManagement;
    case 'care-plan':
      return CarePlan;
    case 'ingredient-management':
      return IngredientManagement;
    case 'recipe-management':
      return RecipeManagement;
    case 'diet-management':
      return DietManagement;
    case 'user-management':
      return UserManagement;
    case 'notifications':
      return Notifications;
    case 'shift-templates':
      return ShiftTemplates;
    default:
      return 'div';
  }
});

// 获取通知列表（全局轮询）
const fetchNotifications = async () => {
  try {
    const response = await http.get('/notifications/');
    // 检查是否有未读通知
    hasUnreadNotifications.value = response.data.some(notification => !notification.is_read);
  } catch (error) {
    console.error('获取通知失败:', error);
  }
};

// 启动全局通知轮询
const startNotificationPolling = () => {
  fetchNotifications(); // 立即获取一次
  
  // 每分钟轮询一次
  notificationPolling = setInterval(() => {
    fetchNotifications();
  }, 60000); // 60秒 = 1分钟
};

// 停止全局通知轮询
const stopNotificationPolling = () => {
  if (notificationPolling) {
    clearInterval(notificationPolling);
    notificationPolling = null;
  }
};

// 清除本地存储的所有数据
const clearLocalStorage = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  sessionStorage.clear();
};

// 处理顶部下拉菜单命令
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      currentView.value = 'profile';
      break;
    case 'customer-file':
      currentView.value = 'customer-file';
      break;
    case 'change-password':
      currentView.value = 'change-password';
      break;
    case 'logout':
      try {
        const response = await http.post('/users/logout/');
        if (response.status === 200) {
          clearLocalStorage();
          ElMessage.success('登出成功');
          router.push('/login');
        }
      } catch (error) {
        console.error('登出失败:', error);
        clearLocalStorage();
        ElMessage.warning('登出请求失败，已清除本地数据');
        router.push('/login');
      }
      break;
  }
};

// 计算是否显示客户类别
const showClientCategory = computed(() => {
  // 如果用户是客户，则只要能看到健康档案或护理计划就显示
  if (user.value.role_name === '客户') {
    return true;
  }
  // 如果用户是员工或管理员，则能看到客户档案、健康档案或护理计划就显示
  return user.value.role_name === '员工' || user.value.role_name === '管理员';
});

// 计算是否显示预约类别
const showAppointmentCategory = computed(() => {
  // 所有用户都能看到预约管理
  // 员工和管理员还能看到服务管理
  return true;
});

// 计算是否显示排班类别
const showScheduleCategory = computed(() => {
  // 员工和管理员可以看到排班管理
  // 只有管理员可以看到排班模板
  return user.value.role_name === '员工' || user.value.role_name === '管理员';
});

// 计算是否显示膳食类别
const showDietCategory = computed(() => {
  // 所有用户都能看到膳食管理
  // 员工和管理员还能看到食谱管理和食材管理
  return true;
});

// 菜单展开状态变化处理
const handleSubMenuOpen = (index) => {
  if (!openedMenus.value.includes(index)) {
    openedMenus.value.push(index);
    localStorage.setItem('openedMenus', JSON.stringify(openedMenus.value));
  }
};

// 菜单关闭状态变化处理
const handleSubMenuClose = (index) => {
  const idx = openedMenus.value.indexOf(index);
  if (idx !== -1) {
    openedMenus.value.splice(idx, 1);
    localStorage.setItem('openedMenus', JSON.stringify(openedMenus.value));
  }
};

onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
    console.log('当前用户角色:', user.value.role_name);
    // 启动通知轮询
    startNotificationPolling();
    
    // 恢复之前保存的菜单状态
    const storedMenus = localStorage.getItem('openedMenus');
    if (storedMenus) {
      try {
        openedMenus.value = JSON.parse(storedMenus);
      } catch (e) {
        console.error('解析保存的菜单状态失败:', e);
        openedMenus.value = [];
      }
    }
  } else {
    router.push('/login');
  }
});

onUnmounted(() => {
  // 停止通知轮询
  stopNotificationPolling();
});
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  min-width: 240px;
  max-width: 240px;
  background-color: var(--primary-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
  transition: scrollbar-color 0.3s ease;
}

.sidebar:hover,
.sidebar:focus,
.sidebar:active {
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

/* 自定义滚动条样式 - Webkit浏览器 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background-color: transparent;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.sidebar:hover::-webkit-scrollbar-thumb,
.sidebar:focus::-webkit-scrollbar-thumb,
.sidebar:active::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.sidebar-menu {
  border-right: none;
  margin-top: var(--spacing-large);
  background-color: transparent;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  height: 100vh;
  overflow: hidden;
}

.top-bar {
  height: 64px;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-light);
  padding: 0 var(--spacing-large);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 90;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-base);
  background-color: #f9fafc;
  border-radius: 50px;
  padding: 6px 16px 6px 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.user-info:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: #f0f7ff;
}

.avatar-container {
  margin-right: var(--spacing-mini);
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-color), #7eb9ff);
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
}

.user-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.username {
  font-size: var(--font-size-medium);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
  line-height: 1.2;
}

/* 添加对RoleBadge组件的样式修正 */
:deep(.role-badge) {
  width: fit-content;
  min-width: 48px;
  max-width: 55px;
  text-align: center;
  white-space: nowrap;
  flex-shrink: 0;
  padding: 2px 8px;
}

.content-area {
  flex: 1;
  padding: var(--spacing-large);
  background-color: var(--bg-color);
  overflow-y: auto;
  height: calc(100vh - 60px);
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
  transition: scrollbar-color 0.3s ease;
}

.content-area:hover,
.content-area:focus,
.content-area:active {
  scrollbar-color: var(--primary-color) transparent;
}

/* 自定义内容区滚动条样式 - Webkit浏览器 */
.content-area::-webkit-scrollbar {
  width: 6px;
}

.content-area::-webkit-scrollbar-track {
  background: transparent;
}

.content-area::-webkit-scrollbar-thumb {
  background-color: transparent;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.content-area:hover::-webkit-scrollbar-thumb,
.content-area:focus::-webkit-scrollbar-thumb,
.content-area:active::-webkit-scrollbar-thumb {
  background-color: rgba(75, 147, 224, 0.3);
}

.content-area::-webkit-scrollbar-thumb:hover {
  background-color: rgba(75, 147, 224, 0.5);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--spacing-medium);
}

.notification-wrapper {
  position: relative;
  display: inline-block;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--danger-color);
  z-index: 1;
  box-shadow: 0 0 0 2px var(--white);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

.notification-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-mini);
  background-color: var(--bg-color);
  border-color: var(--border-color);
  color: var(--text-regular);
  border-radius: 20px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.notification-btn:hover {
  background-color: #f0f7ff;
  color: var(--primary-color);
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  gap: var(--spacing-small);
  height: 50px;
  line-height: 50px;
  margin: var(--spacing-mini) var(--spacing-small);
  border-radius: var(--border-radius);
  transition: all var(--transition-duration);
  padding-left: 20px !important;
}

:deep(.el-sub-menu .el-menu-item) {
  padding-left: 40px !important;
  min-width: auto;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: var(--white) !important;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-menu-item .el-icon) {
  margin-right: var(--spacing-small);
}

:deep(.el-sub-menu__title) {
  display: flex;
  align-items: center;
  gap: var(--spacing-small);
  height: 50px;
  line-height: 50px;
  margin: var(--spacing-mini) var(--spacing-small);
  border-radius: var(--border-radius);
  transition: all var(--transition-duration);
  padding-left: 20px !important;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-sub-menu__title .el-icon) {
  margin-right: var(--spacing-small);
}

:deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: var(--white) !important;
}

:deep(.el-menu) {
  width: 100%;
  max-height: calc(100vh - 60px);
  overflow-y: auto;
  border-right: none;
}

:deep(.el-dropdown) {
  margin-left: var(--spacing-mini);
}

:deep(.el-dropdown .el-button) {
  border-radius: 20px;
  padding: 8px 16px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, var(--primary-color), #7eb9ff);
  border: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.el-dropdown .el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

:deep(.el-dropdown .el-icon) {
  margin-left: 4px;
  transition: transform 0.3s ease;
}

:deep(.el-dropdown:hover .el-icon) {
  transform: rotate(180deg);
}

:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 6px;
}

:deep(.el-dropdown-menu__item) {
  border-radius: 4px;
  margin: 2px 0;
  padding: 8px 16px;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f0f7ff;
}
</style>