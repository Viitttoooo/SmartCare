<template>
  <div class="staff-schedule">
    <!-- 筛选区域 -->
    <div class="filter-container">
      <div class="filter-section">
        <div class="section-title">排班筛选</div>
        <div class="filter-content">
          <template v-if="isAdmin">
            <el-input
              v-model="staffIdFilter"
              placeholder="员工ID"
              class="staff-filter"
              clearable
            />
            <el-input
              v-model="staffNameFilter"
              placeholder="员工姓名"
              class="staff-filter"
              clearable
            />
          </template>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-range-picker"
          />
        </div>
      </div>
    </div>

    <!-- 操作区域（仅管理员可见） -->
    <div v-if="isAdmin" class="operation-container">
      <el-button type="primary" @click="showAddDialog">
        添加排班
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <!-- 排班表格 -->
    <div class="schedule-table">
      <el-table :data="filteredSchedules" border style="width: 100%">
        <el-table-column prop="staff" label="员工ID" width="100" />
        <el-table-column label="员工姓名" width="120">
          <template #default="scope">
            {{ scope.row.staff_last_name }}{{ scope.row.staff_first_name }}
          </template>
        </el-table-column>
        <el-table-column prop="assigned_date" label="排班日期" width="120" />
        <el-table-column label="班次" width="100">
          <template #default="scope">
            <el-tag
              :color="getTemplateColor(scope.row.template)"
              :style="{ color: getDarkerColor(scope.row.template) }"
            >
              {{ getTemplateName(scope.row.template) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="200">
          <template #default="scope">
            {{ getTemplateTime(scope.row.template) }}
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="150" fixed="right">
          <template #default="scope">
            <div class="button-group">
              <el-button 
                type="primary" 
                size="small"
                @click="editSchedule(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small"
                @click="deleteSchedule(scope.row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑排班对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '编辑排班' : '添加排班'"
      width="30%"
    >
      <el-form :model="scheduleForm" label-width="100px">
        <el-form-item label="员工">
          <el-select 
            v-model="scheduleForm.staff" 
            placeholder="请选择员工"
            filterable
          >
            <el-option
              v-for="staff in staffList"
              :key="staff.staff_id"
              :label="`${staff.last_name}${staff.first_name} (ID: ${staff.staff_id})`"
              :value="staff.staff_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排班日期">
          <el-date-picker
            v-model="scheduleForm.assigned_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="班次">
          <el-select 
            v-model="scheduleForm.template" 
            placeholder="请选择班次"
          >
            <el-option
              v-for="template in templates"
              :key="template.template_id"
              :label="template.shift_name"
              :value="template.template_id"
            >
              <div class="template-option">
                <div 
                  class="color-dot" 
                  :style="{ backgroundColor: template.color_code }"
                ></div>
                <span 
                  class="template-name"
                  :style="{ color: getColorForTemplate(template) }"
                >
                  {{ template.shift_name }}
                </span>
                <span class="template-time">
                  {{ template.start_time }} - {{ template.end_time }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="saveSchedule">
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
      <span>确定要删除这条排班记录吗？</span>
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

// 用户角色判断
const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role_name === '管理员';
});

// 筛选条件
const staffIdFilter = ref('');
const staffNameFilter = ref('');
const dateRange = ref([]);

// 数据列表
const schedules = ref([]);
const staffList = ref([]);
const templates = ref([]);

// 对话框控制
const showDialog = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false);
const currentSchedule = ref(null);

// 表单数据
const scheduleForm = ref({
  staff: '',
  assigned_date: '',
  template: ''
});

// 获取班次名称
const getTemplateName = (templateId) => {
  const template = templates.value.find(t => t.template_id === templateId);
  return template ? template.shift_name : '';
};

// 获取班次时间
const getTemplateTime = (templateId) => {
  const template = templates.value.find(t => t.template_id === templateId);
  return template ? `${template.start_time} - ${template.end_time}` : '';
};

// 获取班次颜色
const getTemplateColor = (templateId) => {
  const template = templates.value.find(t => t.template_id === templateId);
  return template ? template.color_code : '#909399';
};

// 获取背景色的深色版本作为文字颜色
const getDarkerColor = (templateId) => {
  const template = templates.value.find(t => t.template_id === templateId);
  if (!template) return '#333333';
  
  // 将十六进制颜色转换为RGB
  const hex = template.color_code.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  
  // 计算亮度
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  
  // 对于亮色背景使用深色文字，对于深色背景使用白色文字
  return brightness > 160 ? '#333333' : '#FFFFFF';
};

// 获取颜色逻辑
const getColorForTemplate = (template) => {
  // 在下拉菜单中始终返回固定颜色
  return '#333333';
};

// 筛选后的排班列表
const filteredSchedules = computed(() => {
  // 首先按日期降序排序
  const sortedSchedules = [...schedules.value].sort((a, b) => 
    b.assigned_date.localeCompare(a.assigned_date)
  );
  
  return sortedSchedules.filter(schedule => {
    const staffIdMatch = !staffIdFilter.value || 
      String(schedule.staff) === staffIdFilter.value;
    
    const staffNameMatch = !staffNameFilter.value ||
      (schedule.staff_last_name + schedule.staff_first_name)
        .toLowerCase()
        .includes(staffNameFilter.value.toLowerCase());
    
    const dateMatch = !dateRange.value || !dateRange.value.length ||
      (schedule.assigned_date >= dateRange.value[0] && 
       schedule.assigned_date <= dateRange.value[1]);
    
    return staffIdMatch && staffNameMatch && dateMatch;
  });
});

// 获取排班数据
const fetchSchedules = async () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    let response;
    
    if (isAdmin.value) {
      response = await http.get('/schedules/get/');
    } else {
      response = await http.get(`/schedules/get/${user.staff_id}/`);
    }
    
    schedules.value = response.data;
  } catch (error) {
    console.error('获取排班数据失败:', error);
    ElMessage.error('获取排班数据失败');
  }
};

// 获取员工列表
const fetchStaffList = async () => {
  try {
    const response = await http.get('/api/users/staff/');
    staffList.value = response.data;
  } catch (error) {
    console.error('获取员工列表失败:', error);
    ElMessage.error('获取员工列表失败');
  }
};

// 获取班次模板
const fetchTemplates = async () => {
  try {
    const response = await http.get('/api/templates/get/');
    templates.value = response.data;
  } catch (error) {
    console.error('获取班次模板失败:', error);
    ElMessage.error('获取班次模板失败');
  }
};

// 显示添加对话框
const showAddDialog = () => {
  isEditing.value = false;
  scheduleForm.value = {
    staff: '',
    assigned_date: '',
    template: ''
  };
  showDialog.value = true;
};

// 显示编辑对话框
const editSchedule = (schedule) => {
  isEditing.value = true;
  currentSchedule.value = schedule;
  scheduleForm.value = {
    staff: schedule.staff,
    assigned_date: schedule.assigned_date,
    template: schedule.template
  };
  showDialog.value = true;
};

// 保存排班
const saveSchedule = async () => {
  try {
    if (isEditing.value) {
      // 编辑模式
      const response = await http.patch('/schedules/update/', {
        shift_id: currentSchedule.value.shift_id,
        ...scheduleForm.value
      });
      
      if (response.status === 200) {
        ElMessage.success('更新成功');
        await fetchSchedules();
      }
    } else {
      // 添加模式
      const response = await http.post('/schedules/create/', scheduleForm.value);
      
      if (response.status === 200) {
        ElMessage.success('添加成功');
        await fetchSchedules();
      }
    }
    
    showDialog.value = false;
  } catch (error) {
    console.error(isEditing.value ? '更新失败:' : '添加失败:', error);
    ElMessage.error(isEditing.value ? '更新失败' : '添加失败');
  }
};

// 删除排班
const deleteSchedule = (schedule) => {
  currentSchedule.value = schedule;
  showDeleteConfirm.value = true;
};

// 确认删除
const confirmDelete = async () => {
  try {
    const response = await http.delete(`/schedules/delete/${currentSchedule.value.shift_id}/`);
    
    if (response.status === 200) {
      ElMessage.success('删除成功');
      await fetchSchedules();
    }
    
    showDeleteConfirm.value = false;
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  await Promise.all([
    fetchSchedules(),
    fetchStaffList(),
    fetchTemplates()
  ]);
});
</script>

<style scoped>
.staff-schedule {
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

.staff-filter {
  width: 150px;
}

.date-range-picker {
  width: 320px;
}

.operation-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.schedule-table {
  background: white;
  border-radius: 4px;
  padding: 20px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-date-picker) {
  width: 100%;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* 班次标签样式 */
:deep(.el-tag) {
  padding: 4px 8px;
  border: none;
  font-size: 13px;
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.el-tag:hover) {
  opacity: 0.9;
}

/* 班次选择下拉菜单样式 */
.template-option {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 4px 0;
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-right: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.template-name {
  font-weight: 500;
  flex: 1;
  color: #333333 !important; /* 固定黑色字体 */
}

.template-time {
  color: #8492a6;
  font-size: 13px;
  margin-left: 8px;
  flex-shrink: 0;
}

:deep(.el-select-dropdown__item) {
  padding: 8px 12px;
}

:deep(.el-select-dropdown__item.selected) {
  background-color: rgba(64, 158, 255, 0.1);
}
</style> 