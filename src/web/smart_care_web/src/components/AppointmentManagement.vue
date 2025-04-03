<template>
  <div class="appointment-management">
    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-input
        v-model="clientNameFilter"
        placeholder="客户姓名"
        clearable
        class="filter-item"
        v-if="isStaff"
      />
      <el-input
        v-model="staffNameFilter"
        placeholder="员工姓名"
        clearable
        class="filter-item"
      />
      <el-date-picker
        v-model="dateRangeFilter"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
        class="filter-item date-range-filter"
      />
      <el-select
        v-model="stateFilter"
        placeholder="预约状态"
        clearable
        class="filter-item"
      >
        <el-option
          v-for="state in ['待确认', '已预约', '已结束', '已取消']"
          :key="state"
          :label="state"
          :value="state"
        />
      </el-select>
      <el-select
        v-model="staffAssignedFilter"
        placeholder="员工分配状态"
        clearable
        class="filter-item"
      >
        <el-option key="已分配" label="已分配员工" value="已分配" />
        <el-option key="未分配" label="未分配员工" value="未分配" />
      </el-select>
      <el-button type="primary" @click="createAppointment">
        新增预约
      </el-button>
    </div>

    <!-- 预约列表 -->
    <el-table :data="filteredAppointments" style="width: 100%" v-loading="loading">
      <el-table-column label="客户姓名" min-width="120">
        <template #default="{ row }">
          {{ row.client_last_name }}{{ row.client_first_name }}
        </template>
      </el-table-column>
      <el-table-column label="服务项目" prop="service_name" min-width="120" />
      <el-table-column label="预约日期" min-width="120">
        <template #default="{ row }">
          {{ row.schedule_date }}
        </template>
      </el-table-column>
      <el-table-column label="时间" min-width="180">
        <template #default="{ row }">
          {{ row.schedule_time }} - {{ row.end_time }}
        </template>
      </el-table-column>
      <el-table-column label="员工" min-width="120">
        <template #default="{ row }">
          <span v-if="row.staff_first_name">
            {{ row.staff_last_name }}{{ row.staff_first_name }}
          </span>
          <span v-else class="unassigned">未分配</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" min-width="100">
        <template #default="{ row }">
          <el-tag :type="getStateType(row.state)">{{ row.state }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="满意度" min-width="100">
        <template #default="{ row }">
          <span v-if="row.satisfaction !== null">{{ row.satisfaction }} 分</span>
          <span v-else>未评分</span>
        </template>
      </el-table-column>
      <el-table-column label="计划" min-width="150">
        <template #default="{ row }">
          <span v-if="row.plan !== null">属于康复计划{{ row.plan }}</span>
          <span v-else>独立预约</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" min-width="200">
        <template #default="{ row }">
          <div class="button-group">
            <!-- 员工可以编辑未结束和未取消的预约 -->
            <el-button 
              v-if="isStaff"
              type="primary" 
              size="small" 
              @click="editAppointment(row)"
            >
              编辑
            </el-button>
            
            <!-- 客户只能为已结束的预约评分 -->
            <el-button 
              v-if="!isStaff && row.state === '已结束'"
              type="primary" 
              size="small" 
              @click="editAppointment(row)"
            >
              评分
            </el-button>
            
            <!-- 客户可以取消未结束和未取消的预约 -->
            <el-button 
              v-if="!isStaff && row.state !== '已取消' && row.state !== '已结束'"
              type="danger" 
              size="small" 
              @click="cancelAppointment(row)"
            >
              取消预约
            </el-button>
            
            <!-- 员工可以删除预约 -->
            <el-button
              v-if="isStaff"
              type="danger"
              size="small"
              @click="deleteAppointment(row)"
            >
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑预约对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? ((!isStaff && currentAppointment?.state === '已结束') ? '预约评分' : '编辑预约') : '新增预约'"
      width="50%"
    >
      <el-form :model="appointmentForm" label-width="120px">
        <el-form-item label="客户" v-if="isStaff">
          <el-select
            v-model="appointmentForm.client"
            placeholder="选择客户"
            filterable
            :disabled="isEdit"
          >
            <el-option
              v-for="client in clients"
              :key="client.client_id"
              :label="`${client.client_id} - ${client.last_name}${client.first_name}`"
              :value="client.client_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="服务">
          <el-select
            v-model="appointmentForm.service"
            placeholder="选择服务"
            @change="handleServiceChange"
            :disabled="(!isStaff && isEdit) || (isEdit && (appointmentForm.state === '已结束' || appointmentForm.state === '已取消'))"
          >
            <el-option
              v-for="service in services"
              :key="service.service_id"
              :label="service.service_name"
              :value="service.service_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="预约日期">
          <el-date-picker
            v-model="appointmentForm.schedule_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            @change="handleDateTimeChange"
            :disabled="(!isStaff && isEdit) || (isEdit && (appointmentForm.state === '已结束' || appointmentForm.state === '已取消'))"
          />
        </el-form-item>

        <el-form-item label="开始时间">
          <el-time-select
            v-model="appointmentForm.schedule_time"
            start="09:00"
            step="00:10"
            end="21:50"
            format="HH:mm"
            placeholder="选择时间"
            @change="handleDateTimeChange"
            :disabled="(!isStaff && isEdit) || (isEdit && (appointmentForm.state === '已结束' || appointmentForm.state === '已取消'))"
          />
        </el-form-item>

        <el-form-item label="结束时间">
          <span>{{ appointmentForm.end_time || '-' }}</span>
        </el-form-item>

        <el-form-item label="员工" v-if="isStaff">
          <el-select
            v-model="appointmentForm.staff"
            placeholder="选择员工"
            :disabled="!canSelectStaff || (isEdit && (appointmentForm.state === '已结束' || appointmentForm.state === '已取消'))"
          >
            <el-option
              v-for="staff in availableStaff"
              :key="staff.staff_id"
              :label="`${staff.last_name}${staff.first_name}`"
              :value="staff.staff_id"
            />
            <el-option
              v-if="availableStaff.length === 0 && canSelectStaff"
              disabled
              label="无其他可用员工"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="康复计划" v-if="isStaff">
          <el-select
            v-model="appointmentForm.plan"
            placeholder="选择康复计划"
            clearable
            :disabled="!appointmentForm.client || (isEdit && (appointmentForm.state === '已结束' || appointmentForm.state === '已取消'))"
          >
            <el-option
              v-for="plan in plans"
              :key="plan.plan_id"
              :label="`${plan.plan_id} - ${plan.plan_type}`"
              :value="plan.plan_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" v-if="isEdit && isStaff">
          <el-select 
            v-model="appointmentForm.state"
          >
            <el-option
              v-for="state in ['待确认', '已预约', '已结束', '已取消']"
              :key="state"
              :label="state"
              :value="state"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="满意度" v-if="!isStaff && isEdit && currentAppointment?.state === '已结束'">
          <el-rate
            v-model="appointmentForm.satisfaction"
            :max="10"
            show-score
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAppointment">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 取消预约确认框 -->
    <el-dialog
      v-model="cancelDialogVisible"
      title="取消预约"
      width="30%"
    >
      <span>确定要取消这个预约吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCancel">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除预约确认框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除预约"
      width="30%"
    >
      <span>确定要删除这个预约吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDelete">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import http from '../utils/axios';

// 用户角色判断
const isStaff = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role_name === '员工' || user.role_name === '管理员';
});

// 数据相关
const loading = ref(false);
const appointments = ref([]);
const clients = ref([]);
const services = ref([]);
const availableStaff = ref([]);
const plans = ref([]);

// 筛选相关
const clientNameFilter = ref('');
const staffNameFilter = ref('');
const stateFilter = ref('');
const staffAssignedFilter = ref('');
const dateRangeFilter = ref([]);

// 对话框相关
const dialogVisible = ref(false);
const cancelDialogVisible = ref(false);
const isEdit = ref(false);
const currentAppointment = ref(null);
const deleteDialogVisible = ref(false);
const currentAppointmentToDelete = ref(null);

// 表单相关
const appointmentForm = ref({
  client: null,
  service: null,
  schedule_date: '',
  schedule_time: '',
  end_time: '',
  staff: null,
  plan: null,
  state: '待确认',
  satisfaction: null
});

// 计算筛选后的预约列表
const filteredAppointments = computed(() => {
  const filtered = appointments.value.filter(appointment => {
    const clientName = `${appointment.client_last_name}${appointment.client_first_name}`;
    const staffName = appointment.staff_first_name ? 
      `${appointment.staff_last_name}${appointment.staff_first_name}` : '';
    
    const clientMatch = !clientNameFilter.value || 
      clientName.toLowerCase().includes(clientNameFilter.value.toLowerCase());
    const staffMatch = !staffNameFilter.value || 
      staffName.toLowerCase().includes(staffNameFilter.value.toLowerCase());
    const stateMatch = !stateFilter.value || 
      appointment.state === stateFilter.value;
    
    // 员工分配状态筛选
    let staffAssignedMatch = true;
    if (staffAssignedFilter.value === '已分配') {
      staffAssignedMatch = appointment.staff !== null && appointment.staff_first_name !== null;
    } else if (staffAssignedFilter.value === '未分配') {
      staffAssignedMatch = appointment.staff === null || appointment.staff_first_name === null;
    }
    
    // 日期范围筛选
    let dateRangeMatch = true;
    if (dateRangeFilter.value && dateRangeFilter.value.length === 2) {
      const appointmentDate = new Date(appointment.schedule_date);
      const startDate = new Date(dateRangeFilter.value[0]);
      const endDate = new Date(dateRangeFilter.value[1]);
      
      // 设置时间为00:00:00，确保日期比较准确
      appointmentDate.setHours(0, 0, 0, 0);
      startDate.setHours(0, 0, 0, 0);
      endDate.setHours(0, 0, 0, 0);
      
      // 包含端点的日期范围比较
      dateRangeMatch = appointmentDate >= startDate && appointmentDate <= endDate;
    }
    
    return clientMatch && staffMatch && stateMatch && staffAssignedMatch && dateRangeMatch;
  });

  // 按预约时间从新到旧排序
  return filtered.sort((a, b) => {
    const dateA = new Date(`${a.schedule_date} ${a.schedule_time}`);
    const dateB = new Date(`${b.schedule_date} ${b.schedule_time}`);
    return dateB - dateA;
  });
});

// 判断是否可以选择员工
const canSelectStaff = computed(() => {
  return appointmentForm.value.schedule_date && 
         appointmentForm.value.schedule_time && 
         appointmentForm.value.end_time;
});

// 获取状态对应的类型
const getStateType = (state) => {
  const types = {
    '待确认': 'warning',
    '已预约': 'primary',
    '已结束': 'success',
    '已取消': 'danger'
  };
  return types[state] || 'info';
};

// 禁用今天之前的日期
const disabledDate = (date) => {
  return date < new Date();
};

// 处理服务变更
const handleServiceChange = async () => {
  const service = services.value.find(s => s.service_id === appointmentForm.value.service);
  if (service && appointmentForm.value.schedule_time) {
    calculateEndTime(service.duration);
  }
  if (canSelectStaff.value) {
    await fetchAvailableStaff();
  }
};

// 处理日期时间变更
const handleDateTimeChange = async () => {
  if (appointmentForm.value.service && appointmentForm.value.schedule_time) {
    const service = services.value.find(s => s.service_id === appointmentForm.value.service);
    if (service) {
      calculateEndTime(service.duration);
    }
  }
  if (canSelectStaff.value) {
    await fetchAvailableStaff();
  }
};

// 计算结束时间
const calculateEndTime = (duration) => {
  if (!appointmentForm.value.schedule_time) return;
  
  const [hours, minutes] = appointmentForm.value.schedule_time.split(':').map(Number);
  const endDate = new Date(2000, 0, 1, hours, minutes);
  endDate.setMinutes(endDate.getMinutes() + duration);
  
  if (endDate.getHours() >= 22) {
    ElMessage.warning('预约时间不能超过晚上22:00');
    appointmentForm.value.schedule_time = '';
    appointmentForm.value.end_time = '';
    return;
  }
  
  appointmentForm.value.schedule_time = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:00`;
  appointmentForm.value.end_time = `${String(endDate.getHours()).padStart(2, '0')}:${String(endDate.getMinutes()).padStart(2, '0')}:00`;
};

// 获取可用员工
const fetchAvailableStaff = async () => {
  try {
    // 确保时间格式为 HH:mm:ss
    const formatTime = (time) => {
      if (!time) return '';
      return time.length === 5 ? `${time}:00` : time;
    };

    const response = await http.get('/api/staff/available/', {
      params: {
        date: appointmentForm.value.schedule_date,
        start_time: formatTime(appointmentForm.value.schedule_time),
        end_time: formatTime(appointmentForm.value.end_time)
      }
    });
    availableStaff.value = response.data;
  } catch (error) {
    console.error('获取可用员工失败:', error);
    ElMessage.error('获取可用员工失败');
  }
};

// 获取康复计划
const fetchPlans = async (clientId) => {
  try {
    const response = await http.get(`/api/plans/get/${clientId}/`);
    plans.value = response.data;
  } catch (error) {
    console.error('获取康复计划失败:', error);
    ElMessage.error('获取康复计划失败');
  }
};

// 获取所有预约
const fetchAppointments = async () => {
  loading.value = true;
  try {
    let url;
    
    if (isStaff.value) {
      // 员工/管理员获取所有预约
      url = '/api/appointments/';
    } else {
      // 客户获取自己的预约，从本地存储获取 client_id
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const clientId = user.client_id;
      
      if (!clientId) {
        ElMessage.error('未找到客户ID信息');
        return;
      }
      
      url = `/api/appointments/${clientId}/`;
    }
    
    const response = await http.get(url);
    appointments.value = response.data;
  } catch (error) {
    console.error('获取预约列表失败:', error);
    ElMessage.error('获取预约列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取客户列表
const fetchClients = async () => {
  try {
    const response = await http.get('/api/clients/');
    clients.value = response.data;
  } catch (error) {
    console.error('获取客户列表失败:', error);
    ElMessage.error('获取客户列表失败');
  }
};

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

// 新增预约
const createAppointment = () => {
  isEdit.value = false;
  // 重置当前预约对象，避免之前的评分状态影响新建预约
  currentAppointment.value = null;
  appointmentForm.value = {
    client: null,
    service: null,
    schedule_date: '',
    schedule_time: '',
    end_time: '',
    staff: null,
    plan: null,
    state: '待确认',
    satisfaction: null
  };
  dialogVisible.value = true;
};

// 编辑预约
const editAppointment = (row) => {
  isEdit.value = true;
  currentAppointment.value = row;
  
  // 客户只能编辑已结束预约的评分
  if (!isStaff.value && row.state === '已结束') {
    appointmentForm.value = {
      client: row.client,
      service: row.service,
      schedule_date: row.schedule_date,
      schedule_time: row.schedule_time.substring(0, 5),
      end_time: row.end_time,
      staff: row.staff,
      plan: row.plan,
      state: row.state,
      satisfaction: row.satisfaction || null
    };
  } else {
    appointmentForm.value = {
      client: row.client,
      service: row.service,
      schedule_date: row.schedule_date,
      schedule_time: row.schedule_time.substring(0, 5),
      end_time: row.end_time,
      staff: row.staff,
      plan: row.plan,
      state: row.state,
      satisfaction: row.satisfaction
    };
  }
  
  if (isStaff.value && row.client) {
    fetchPlans(row.client);
  }
  if (canSelectStaff.value) {
    fetchAvailableStaff();
  }
  dialogVisible.value = true;
};

// 保存预约
const saveAppointment = async () => {
  try {
    // 确保时间格式为 HH:mm:ss
    const formatTime = (time) => {
      if (!time) return '';
      return time.length === 5 ? `${time}:00` : time;
    };

    let payload = {};
    
    // 客户只能更新已结束预约的评分
    if (!isStaff.value && isEdit.value && currentAppointment.value?.state === '已结束') {
      payload = {
        appointment_id: currentAppointment.value.appointment_id,
        satisfaction: appointmentForm.value.satisfaction
      };
    } else {
      // 构建基本的预约数据
      payload = {
        schedule_date: appointmentForm.value.schedule_date,
        schedule_time: formatTime(appointmentForm.value.schedule_time),
        end_time: formatTime(appointmentForm.value.end_time),
        service: appointmentForm.value.service,
        state: appointmentForm.value.state
      };
      
      if (isStaff.value) {
        payload.staff = appointmentForm.value.staff;
        if (appointmentForm.value.plan) {
          payload.plan = appointmentForm.value.plan;
        }
      }
      
      if (isEdit.value) {
        payload.appointment_id = currentAppointment.value.appointment_id;
      }
    }

    // 获取客户ID
    let clientId;
    if (isStaff.value) {
      clientId = appointmentForm.value.client;
    } else {
      // 客户角色，从本地存储获取 client_id
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      clientId = user.client_id;
      
      if (!clientId) {
        ElMessage.error('未找到客户ID信息');
        return;
      }
    }

    let response;
    if (isEdit.value) {
      response = await http.patch(`/api/appointments/update/${clientId}/`, payload);
    } else {
      response = await http.post(`/api/appointments/create/${clientId}/`, payload);
    }

    if (response.status === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      dialogVisible.value = false;
      fetchAppointments();
    }
  } catch (error) {
    console.error(isEdit.value ? '更新失败:' : '创建失败:', error);
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败');
  }
};

// 取消预约
const cancelAppointment = (row) => {
  currentAppointment.value = row;
  cancelDialogVisible.value = true;
};

// 确认取消预约
const confirmCancel = async () => {
  try {
    // 从本地存储获取客户ID
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const clientId = user.client_id;
    
    if (!clientId) {
      ElMessage.error('未找到客户ID信息');
      return;
    }
    
    const response = await http.patch(`/api/appointments/update/${clientId}/`, {
      appointment_id: currentAppointment.value.appointment_id,
      state: '已取消'
    });

    if (response.status === 200) {
      ElMessage.success('预约已取消');
      cancelDialogVisible.value = false;
      fetchAppointments();
    }
  } catch (error) {
    console.error('取消预约失败:', error);
    ElMessage.error('取消预约失败');
  }
};

// 删除预约
const deleteAppointment = (row) => {
  currentAppointmentToDelete.value = row;
  deleteDialogVisible.value = true;
};

// 确认删除预约
const confirmDelete = async () => {
  try {
    const response = await http.delete(
      `/api/appointments/delete/${currentAppointmentToDelete.value.appointment_id}/`
    );
    if (response.status === 200) {
      ElMessage.success('删除成功');
      deleteDialogVisible.value = false;
      fetchAppointments();
    }
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 监听客户变化
watch(() => appointmentForm.value.client, async (newValue) => {
  if (newValue && isStaff.value) {
    await fetchPlans(newValue);
  }
});

// 监听状态变化，当状态改变时更新可编辑状态并可能需要重新获取可用员工
watch(() => appointmentForm.value.state, async (newState) => {
  if (isEdit.value && isStaff.value && canSelectStaff.value) {
    // 如果状态从"已结束"或"已取消"变为其他状态，需要重新获取可用员工
    if (newState !== '已结束' && newState !== '已取消' && 
        (currentAppointment.value?.state === '已结束' || currentAppointment.value?.state === '已取消')) {
      await fetchAvailableStaff();
    }
  }
});

// 组件挂载时获取数据
onMounted(async () => {
  await fetchAppointments();
  await fetchServices();
  if (isStaff.value) {
    await fetchClients();
  }
});
</script>

<style scoped>
.appointment-management {
  padding: var(--spacing-large);
}

.filter-section {
  background: var(--white);
  border-radius: var(--border-radius);
  padding: var(--spacing-large);
  margin-bottom: var(--spacing-large);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-medium);
  align-items: center;
  box-shadow: var(--box-shadow-light);
}

.filter-item {
  min-width: 180px;
  max-width: 220px;
}

.date-range-filter {
  min-width: 300px;
}

.unassigned {
  color: var(--danger-color);
  font-style: italic;
}

@media (max-width: 768px) {
  .filter-item {
    width: 100%;
    max-width: none;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
}

:deep(.el-rate) {
  margin-top: 8px;
}

.dialog-footer {
  text-align: right;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style> 