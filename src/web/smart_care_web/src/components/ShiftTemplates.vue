<template>
  <div class="shift-templates-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>排班模板管理</h1>
      <div class="page-description">管理排班模板，用于员工排班</div>
    </div>

    <!-- 模板列表和操作区域 -->
    <div class="templates-section">
      <div class="section-header">
        <h2>模板列表</h2>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建模板
        </el-button>
      </div>

      <div class="templates-list">
        <el-table :data="templates" style="width: 100%" v-loading="loading">
          <el-table-column prop="template_id" label="ID" width="80" />
          <el-table-column prop="shift_name" label="班次名称" width="180" />
          <el-table-column label="时间段" min-width="200">
            <template #default="{ row }">
              {{ row.start_time }} - {{ row.end_time }}
            </template>
          </el-table-column>
          <el-table-column label="颜色标识" width="120">
            <template #default="{ row }">
              <div class="color-preview" :style="{ backgroundColor: row.color_code }"></div>
              <span class="color-code">{{ row.color_code }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="confirmDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 新建/编辑模板对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑排班模板' : '新建排班模板'"
      width="500px"
    >
      <el-form :model="templateForm" label-width="100px" :rules="formRules" ref="templateFormRef">
        <el-form-item label="班次名称" prop="shift_name">
          <el-input v-model="templateForm.shift_name" placeholder="请输入班次名称" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker
            v-model="templateForm.start_time"
            format="HH:mm:ss"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker
            v-model="templateForm.end_time"
            format="HH:mm:ss"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="颜色标识" prop="color_code">
          <el-color-picker v-model="templateForm.color_code" show-alpha />
          <span class="color-preview" :style="{ backgroundColor: templateForm.color_code }"></span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEditing ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import http from '../utils/axios';

// 数据状态
const templates = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const isEditing = ref(false);
const submitting = ref(false);
const templateFormRef = ref(null);

// 表单数据
const templateForm = reactive({
  template_id: null,
  shift_name: '',
  start_time: '',
  end_time: '',
  color_code: '#409EFF'
});

// 表单验证规则
const formRules = {
  shift_name: [
    { required: true, message: '请输入班次名称', trigger: 'blur' },
    { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  color_code: [
    { required: true, message: '请选择颜色', trigger: 'change' }
  ]
};

// 获取所有排班模板
const fetchTemplates = async () => {
  loading.value = true;
  try {
    const response = await http.get('/api/templates/get/');
    templates.value = response.data;
  } catch (error) {
    console.error('获取排班模板失败:', error);
    ElMessage.error('获取排班模板失败');
  } finally {
    loading.value = false;
  }
};

// 打开创建模板对话框
const openCreateDialog = () => {
  isEditing.value = false;
  resetForm();
  dialogVisible.value = true;
};

// 打开编辑模板对话框
const openEditDialog = (row) => {
  isEditing.value = true;
  resetForm();
  
  // 复制数据到表单
  templateForm.template_id = row.template_id;
  templateForm.shift_name = row.shift_name;
  templateForm.color_code = row.color_code;
  
  // 处理时间格式
  templateForm.start_time = new Date(`2000-01-01T${row.start_time}`);
  templateForm.end_time = new Date(`2000-01-01T${row.end_time}`);
  
  dialogVisible.value = true;
};

// 重置表单
const resetForm = () => {
  if (templateFormRef.value) {
    templateFormRef.value.resetFields();
  }
  
  templateForm.template_id = null;
  templateForm.shift_name = '';
  templateForm.start_time = '';
  templateForm.end_time = '';
  templateForm.color_code = '#409EFF';
};

// 格式化时间为后端需要的格式
const formatTime = (timeDate) => {
  if (!timeDate) return '';
  
  const hours = timeDate.getHours().toString().padStart(2, '0');
  const minutes = timeDate.getMinutes().toString().padStart(2, '0');
  const seconds = timeDate.getSeconds().toString().padStart(2, '0');
  
  return `${hours}:${minutes}:${seconds}`;
};

// 提交表单
const submitForm = async () => {
  if (!templateFormRef.value) return;
  
  await templateFormRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    
    try {
      const formData = {
        shift_name: templateForm.shift_name,
        start_time: formatTime(templateForm.start_time),
        end_time: formatTime(templateForm.end_time),
        color_code: templateForm.color_code
      };
      
      if (isEditing.value) {
        // 更新模板
        formData.template_id = templateForm.template_id;
        await http.patch('/api/templates/update/', formData);
        ElMessage.success('模板更新成功');
      } else {
        // 创建模板
        await http.post('/api/templates/create/', formData);
        ElMessage.success('模板创建成功');
      }
      
      dialogVisible.value = false;
      fetchTemplates(); // 刷新列表
    } catch (error) {
      console.error('操作失败:', error);
      ElMessage.error(`${isEditing.value ? '更新' : '创建'}模板失败`);
    } finally {
      submitting.value = false;
    }
  });
};

// 确认删除
const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除"${row.shift_name}"模板吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteTemplate(row.template_id);
  }).catch(() => {
    // 用户取消删除
  });
};

// 删除模板
const deleteTemplate = async (templateId) => {
  loading.value = true;
  try {
    await http.delete(`/api/templates/delete/${templateId}/`);
    ElMessage.success('模板删除成功');
    fetchTemplates(); // 刷新列表
  } catch (error) {
    console.error('删除模板失败:', error);
    ElMessage.error('删除模板失败');
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchTemplates();
});
</script>

<style scoped>
.shift-templates-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px;
  color: var(--el-text-color-primary);
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.templates-section {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.templates-section:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 18px;
  font-weight: 600;
}

.templates-list {
  margin-top: 16px;
}

.color-preview {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  margin-right: 8px;
  vertical-align: middle;
  border: 1px solid #dcdfe6;
}

.color-code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  vertical-align: middle;
}

:deep(.el-form-item__content) {
  display: flex;
  align-items: center;
}

:deep(.el-color-picker) {
  margin-right: 10px;
}

:deep(.el-table .cell) {
  display: flex;
  align-items: center;
}

:deep(.el-table .el-button) {
  padding: 6px 12px;
  margin-right: 8px;
}

:deep(.el-table .el-button .el-icon) {
  margin-right: 4px;
}
</style> 