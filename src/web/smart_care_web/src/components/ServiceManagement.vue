<template>
  <div class="service-management">
    <!-- 筛选区域 -->
    <div class="filter-container">
      <div class="filter-section">
        <div class="section-title">服务筛选</div>
        <div class="filter-content">
          <el-input
            v-model="searchQuery"
            placeholder="搜索服务名称"
            class="search-input"
            clearable
          />
        </div>
      </div>
    </div>

    <!-- 操作区域 -->
    <div class="operation-container">
      <el-button type="primary" @click="showAddDialog">
        添加服务
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <!-- 服务列表 -->
    <div class="service-table">
      <el-table :data="filteredServices" border style="width: 100%">
        <el-table-column prop="service_name" label="服务名称" />
        <el-table-column label="时长">
          <template #default="scope">
            {{ scope.row.duration }} 分钟
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <div class="button-group">
              <el-button 
                type="primary" 
                size="small"
                @click="editService(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small"
                @click="deleteService(scope.row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑服务对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '编辑服务' : '添加服务'"
      width="30%"
    >
      <el-form :model="serviceForm" label-width="100px">
        <el-form-item label="服务名称">
          <el-input v-model="serviceForm.service_name" />
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input-number 
            v-model="serviceForm.duration" 
            :min="1"
            :max="480"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="saveService">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteConfirm"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除这项服务吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteConfirm = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import http from '../utils/axios';

// 数据列表
const services = ref([]);
const searchQuery = ref('');

// 对话框控制
const showDialog = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false);
const currentService = ref(null);

// 表单数据
const serviceForm = ref({
  service_name: '',
  duration: 60
});

// 筛选后的服务列表
const filteredServices = computed(() => {
  if (!searchQuery.value) return services.value;
  
  return services.value.filter(service => 
    service.service_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// 获取服务列表
const fetchServices = async () => {
  try {
    const response = await http.get('/api/services/');
    services.value = response.data;
  } catch (error) {
    console.error('获取服务列表失败:', error);
    ElMessage.error('获取服务列表失败');
  }
};

// 显示添加对话框
const showAddDialog = () => {
  isEditing.value = false;
  serviceForm.value = {
    service_name: '',
    duration: 60
  };
  showDialog.value = true;
};

// 显示编辑对话框
const editService = (service) => {
  isEditing.value = true;
  currentService.value = service;
  serviceForm.value = {
    service_name: service.service_name,
    duration: service.duration
  };
  showDialog.value = true;
};

// 保存服务
const saveService = async () => {
  try {
    if (isEditing.value) {
      // 编辑模式
      await http.patch('/api/services/update/', {
        service_id: currentService.value.service_id,
        ...serviceForm.value
      });
      ElMessage.success('更新成功');
    } else {
      // 添加模式
      await http.post('/api/services/create/', serviceForm.value);
      ElMessage.success('添加成功');
    }
    
    showDialog.value = false;
    await fetchServices();
  } catch (error) {
    console.error(isEditing.value ? '更新失败:' : '添加失败:', error);
    ElMessage.error(isEditing.value ? '更新失败' : '添加失败');
  }
};

// 删除服务
const deleteService = (service) => {
  currentService.value = service;
  showDeleteConfirm.value = true;
};

// 确认删除
const confirmDelete = async () => {
  try {
    await http.delete(`/api/services/delete/${currentService.value.service_id}/`);
    ElMessage.success('删除成功');
    showDeleteConfirm.value = false;
    await fetchServices();
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  await fetchServices();
});
</script>

<style scoped>
.service-management {
  padding: 20px;
}

.filter-container {
  margin-bottom: 20px;
}

.filter-section {
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
}

.section-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 16px;
  font-weight: 500;
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 200px;
}

.operation-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.service-table {
  background: white;
  border-radius: 4px;
  padding: 20px;
}

:deep(.el-input-number) {
  width: 180px;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style> 