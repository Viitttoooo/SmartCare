<template>
  <div class="notifications-container">
    <div class="notifications-header">
      <div class="section-title">我的通知</div>
      <el-button 
        v-if="notifications.length > 0 && hasUnread" 
        type="primary" 
        size="small" 
        @click="markAllAsRead"
      >
        全部标为已读
      </el-button>
    </div>
    
    <div class="notifications-content card-container custom-scrollbar">
      <el-empty v-if="notifications.length === 0" description="暂无通知" />
      
      <div v-else class="notification-list">
        <el-card 
          v-for="notification in notifications" 
          :key="notification.id" 
          class="notification-item" 
          :class="{ 'unread': !notification.is_read }"
          shadow="hover"
        >
          <div class="notification-content">
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-footer">
              <div class="notification-time">{{ formatDateTime(notification.created_at) }}</div>
              <el-button 
                v-if="!notification.is_read" 
                type="primary" 
                size="small" 
                @click.stop="markAsRead(notification.id)"
              >
                标为已读
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue';
import { ElMessage } from 'element-plus';
import http from '../utils/axios';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

dayjs.extend(utc);
dayjs.extend(timezone);

const notifications = ref([]);
const polling = ref(null);
const hasUnreadNotifications = inject('hasUnreadNotifications', ref(false));

// 计算是否有未读通知
const hasUnread = computed(() => {
  return notifications.value.some(notification => !notification.is_read);
});

// 获取通知列表
const fetchNotifications = async () => {
  try {
    const response = await http.get('/notifications/');
    notifications.value = response.data;
    
    // 更新未读通知标记
    hasUnreadNotifications.value = hasUnread.value;
  } catch (error) {
    console.error('获取通知失败:', error);
  }
};

// 将时间转换为北京时间
const formatDateTime = (dateTime) => {
  return dayjs(dateTime).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss');
};

// 标记单个通知为已读
const markAsRead = async (id) => {
  try {
    await http.patch(`/notifications/${id}/read/`);
    
    // 更新本地通知状态
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.value[index].is_read = true;
    }
    
    // 更新未读通知标记
    hasUnreadNotifications.value = notifications.value.some(n => !n.is_read);
    
    ElMessage.success('已标记为已读');
  } catch (error) {
    console.error('标记为已读失败:', error);
    ElMessage.error('标记为已读失败');
  }
};

// 标记所有通知为已读
const markAllAsRead = async () => {
  try {
    const unreadNotifications = notifications.value.filter(n => !n.is_read);
    
    if (unreadNotifications.length === 0) {
      return;
    }
    
    // 依次将每个未读通知标记为已读
    for (const notification of unreadNotifications) {
      await markAsRead(notification.id);
    }
    
    ElMessage.success('所有通知已标记为已读');
  } catch (error) {
    console.error('标记全部已读失败:', error);
    ElMessage.error('标记全部已读失败');
  }
};

// 启动轮询
const startPolling = () => {
  fetchNotifications(); // 立即获取一次
  
  // 每分钟轮询一次
  polling.value = setInterval(() => {
    fetchNotifications();
  }, 60000); // 60秒 = 1分钟
};

// 停止轮询
const stopPolling = () => {
  if (polling.value) {
    clearInterval(polling.value);
    polling.value = null;
  }
};

// 组件挂载时初始化
onMounted(() => {
  startPolling();
});

// 组件卸载时清理
onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.notifications-container {
  padding: var(--spacing-large);
}

.notifications-header {
  margin-bottom: var(--spacing-large);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications-content {
  min-height: 200px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-base);
}

.notification-item {
  border-radius: var(--border-radius);
  transition: all var(--transition-duration);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.notification-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--box-shadow);
}

.notification-item.unread {
  border-left: 3px solid var(--primary-color);
  background-color: var(--primary-light);
}

.notification-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-base);
}

.notification-message {
  font-size: var(--font-size-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.notification-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-time {
  font-size: var(--font-size-small);
  color: var(--text-secondary);
}
</style> 