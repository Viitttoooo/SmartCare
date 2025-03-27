<template>
  <div class="care-plan">
    <!-- 客户列表视图（仅管理员和员工可见） -->
    <div v-if="isStaff && !selectedClient" class="client-list-view">
      <div class="filter-section">
        <el-input
          v-model="clientFilter"
          placeholder="搜索客户ID/姓名"
          clearable
          class="filter-item"
        />
      </div>

      <el-table :data="filteredClients" style="width: 100%" v-loading="loading">
        <el-table-column label="客户ID" prop="client_id" width="100" />
        <el-table-column label="姓名">
          <template #default="{ row }">
            {{ row.last_name }}{{ row.first_name }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <div class="button-group">
              <el-button type="primary" size="small" @click="viewClientPlans(row)">
                查看计划
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 计划列表视图 -->
    <div v-else class="plan-list-view">
      <div class="header-section">
        <div class="back-button" v-if="isStaff">
          <el-button @click="backToClientList">
            返回客户列表
          </el-button>
        </div>
        <el-button type="primary" v-if="isStaff" @click="createPlan">
          新建计划
        </el-button>
      </div>

      <el-table 
        :data="sortedCarePlans" 
        style="width: 100%" 
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column label="计划类型" prop="plan_type" min-width="120" />
        <el-table-column 
          label="开始日期" 
          prop="start_date" 
          min-width="120"
          sortable="custom"
        />
        <el-table-column 
          label="结束日期" 
          prop="end_date" 
          min-width="120"
          sortable="custom"
        />
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getPlanStateType(row.plan_state)">
              {{ row.plan_state }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="责任人" min-width="120">
          <template #default="{ row }">
            <span v-if="row.staff_first_name">
              {{ row.staff_last_name }}{{ row.staff_first_name }}
            </span>
            <span v-else class="unassigned">未分配</span>
          </template>
        </el-table-column>
        <el-table-column label="满意度" min-width="120">
          <template #default="{ row }">
            <template v-if="!isStaff && row.plan_state === '已完成'">
              <el-select
                v-model="row.plan_satisfaction"
                placeholder="请评分"
                @change="updatePlanScore(row)"
              >
                <el-option
                  v-for="score in 10"
                  :key="score"
                  :label="`${score}分`"
                  :value="score"
                />
              </el-select>
            </template>
            <template v-else>
              <span v-if="row.plan_satisfaction !== null">{{ row.plan_satisfaction }}分</span>
              <span v-else>未评分</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column 
          label="操作" 
          min-width="400" 
          align="right"
          header-align="right"
        >
          <template #default="{ row }">
            <div class="button-group">
              <el-button type="primary" size="small" @click="viewPlanDetail(row)">
                详情
              </el-button>
              <el-button type="primary" size="small" @click="getReport(row)">
                进度报告
              </el-button>
              <template v-if="isStaff">
                <el-button type="primary" size="small" @click="editPlan(row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deletePlan(row)">
                  删除
                </el-button>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 计划详情对话框 -->
    <el-dialog
      v-model="planDetailVisible"
      :title="currentPlan ? `${currentPlan.plan_type} - 详细信息` : '计划详情'"
      width="70%"
    >
      <div v-if="currentPlan" class="plan-detail">
        <div class="basic-info">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="计划类型">{{ currentPlan.plan_type }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getPlanStateType(currentPlan.plan_state)">
                {{ currentPlan.plan_state }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开始日期">{{ currentPlan.start_date }}</el-descriptions-item>
            <el-descriptions-item label="结束日期">{{ currentPlan.end_date }}</el-descriptions-item>
            <el-descriptions-item label="责任人">
              <span v-if="currentPlan.staff_first_name">
                {{ currentPlan.staff_last_name }}{{ currentPlan.staff_first_name }}
              </span>
              <span v-else class="unassigned">未分配</span>
            </el-descriptions-item>
            <el-descriptions-item label="满意度">
              <span v-if="currentPlan.plan_satisfaction !== null">{{ currentPlan.plan_satisfaction }}分</span>
              <span v-else>未评分</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="goals-section">
          <div class="section-header">
            <h3>计划目标</h3>
            <el-button v-if="isStaff" type="primary" size="small" @click="createGoal">
              新增目标
            </el-button>
          </div>
          <div v-if="planGoals.length === 0" class="empty-text">未制定目标</div>
          <el-table v-else :data="planGoals">
            <el-table-column label="目标描述" prop="description" />
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.goal_state === '已达成' ? 'success' : 'warning'">
                  {{ row.goal_state }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column v-if="isStaff" label="操作" width="250" align="right">
              <template #default="{ row }">
                <div class="button-group">
                  <el-button type="primary" size="small" @click="editGoal(row)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteGoal(row)">
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="appointments-section">
          <div class="section-header">
            <h3>相关预约</h3>
            <el-button v-if="isStaff" type="primary" size="small" @click="createAppointment">
              新增预约
            </el-button>
          </div>
          <div v-if="planAppointments.length === 0" class="empty-text">未预约服务</div>
          <el-table v-else :data="planAppointments">
            <el-table-column label="服务项目" prop="service_name" />
            <el-table-column label="预约日期" prop="schedule_date" />
            <el-table-column label="时间">
              <template #default="{ row }">
                {{ row.schedule_time }} - {{ row.end_time }}
              </template>
            </el-table-column>
            <el-table-column label="状态">
              <template #default="{ row }">
                <el-tag :type="getAppointmentStateType(row.state)">
                  {{ row.state }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="满意度" width="150">
              <template #default="{ row }">
                <template v-if="!isStaff && row.state === '已结束'">
                  <el-select
                    v-model="row.satisfaction"
                    placeholder="请评分"
                    @change="updateAppointmentScore(row)"
                  >
                    <el-option
                      v-for="score in 10"
                      :key="score"
                      :label="`${score}分`"
                      :value="score"
                    />
                  </el-select>
                </template>
                <template v-else>
                  <span v-if="row.satisfaction !== null">{{ row.satisfaction }}分</span>
                  <span v-else>未评分</span>
                </template>
              </template>
            </el-table-column>
            <el-table-column v-if="isStaff" label="操作" width="250" align="right">
              <template #default="{ row }">
                <div class="button-group">
                  <el-button type="primary" size="small" @click="editAppointment(row)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteAppointment(row)">
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 计划编辑对话框 -->
    <el-dialog
      v-model="planFormVisible"
      :title="isEditingPlan ? '编辑计划' : '新建计划'"
      width="50%"
    >
      <el-form :model="planForm" label-width="120px">
        <el-form-item label="计划类型">
          <el-select v-model="planForm.plan_type">
            <el-option label="康复护理" value="康复护理" />
            <el-option label="日常护理" value="日常护理" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划状态">
          <el-select v-model="planForm.plan_state">
            <el-option label="待开始" value="待开始" />
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="planForm.start_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="planForm.end_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="责任人">
          <el-select v-model="planForm.staff" clearable placeholder="选择责任人">
            <el-option
              v-for="staff in staffList"
              :key="staff.staff_id"
              :label="`${staff.last_name}${staff.first_name}`"
              :value="staff.staff_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="planFormVisible = false">取消</el-button>
          <el-button type="primary" @click="savePlan">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 目标编辑对话框 -->
    <el-dialog
      v-model="goalFormVisible"
      :title="isEditingGoal ? '编辑目标' : '新增目标'"
      width="50%"
    >
      <el-form :model="goalForm" label-width="120px">
        <el-form-item label="目标描述">
          <el-input
            v-model="goalForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入目标描述"
          />
        </el-form-item>
        <el-form-item label="目标状态">
          <el-select v-model="goalForm.goal_state">
            <el-option label="未达成" value="未达成" />
            <el-option label="已达成" value="已达成" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="goalFormVisible = false">取消</el-button>
          <el-button type="primary" @click="saveGoal">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预约编辑对话框 -->
    <el-dialog
      v-model="appointmentFormVisible"
      :title="isEditingAppointment ? '编辑预约' : '新增预约'"
      width="50%"
    >
      <el-form :model="appointmentForm" label-width="120px">
        <el-form-item label="服务">
          <el-select
            v-model="appointmentForm.service"
            placeholder="选择服务"
            @change="handleServiceChange"
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
          />
        </el-form-item>

        <el-form-item label="结束时间">
          <span>{{ appointmentForm.end_time || '-' }}</span>
        </el-form-item>

        <el-form-item label="员工" v-if="isStaff">
          <el-select
            v-model="appointmentForm.staff"
            placeholder="选择员工"
            :disabled="!canSelectStaff"
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

        <el-form-item label="状态" v-if="isEditingAppointment && isStaff">
          <el-select v-model="appointmentForm.state">
            <el-option
              v-for="state in ['待确认', '已预约', '已结束', '已取消']"
              :key="state"
              :label="state"
              :value="state"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="appointmentFormVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAppointment">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除预约确认框 -->
    <el-dialog
      v-model="deleteAppointmentDialogVisible"
      title="删除预约"
      width="30%"
    >
      <span>确定要删除这个预约吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteAppointmentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDeleteAppointment">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 进度报告对话框 -->
    <el-dialog
      v-model="reportDialogVisible"
      title="康复计划进度报告"
      width="60%"
    >
      <div v-if="currentReport" class="report-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户姓名">
            {{ currentReport.care_plan.client_last_name }}{{ currentReport.care_plan.client_first_name }}
          </el-descriptions-item>
          <el-descriptions-item label="责任人">
            <span v-if="currentReport.care_plan.staff_first_name">
              {{ currentReport.care_plan.staff_last_name }}{{ currentReport.care_plan.staff_first_name }}
            </span>
            <span v-else class="unassigned">未分配</span>
          </el-descriptions-item>
          <el-descriptions-item label="计划类型">
            {{ currentReport.care_plan.plan_type }}
          </el-descriptions-item>
          <el-descriptions-item label="计划状态">
            <el-tag :type="getPlanStateType(currentReport.care_plan.plan_state)">
              {{ currentReport.care_plan.plan_state }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ currentReport.care_plan.start_date }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ currentReport.care_plan.end_date }}
          </el-descriptions-item>
          <el-descriptions-item label="满意度">
            <span v-if="currentReport.care_plan.plan_satisfaction !== null">
              {{ currentReport.care_plan.plan_satisfaction }}分
            </span>
            <span v-else>未评分</span>
          </el-descriptions-item>
          <el-descriptions-item label="报告生成时间">
            {{ currentReport.today }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="report-section">
          <h3>目标完成情况</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="总目标数" :value="currentReport.goal_done + currentReport.goal_undone" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="已完成目标" :value="currentReport.goal_done" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="未完成目标" :value="currentReport.goal_undone" />
            </el-col>
          </el-row>
        </div>

        <div class="report-section">
          <h3>预约情况</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic 
                title="总预约数" 
                :value="currentReport.appointment_pending + currentReport.appointment_booked + 
                       currentReport.appointment_ended + currentReport.appointment_cancelled" 
              />
            </el-col>
            <el-col :span="8">
              <el-statistic title="待确认预约" :value="currentReport.appointment_pending" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="已预约" :value="currentReport.appointment_booked" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="已完成预约" :value="currentReport.appointment_ended" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="已取消预约" :value="currentReport.appointment_cancelled" />
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import http from '../utils/axios';

// 用户角色判断
const isStaff = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role_name === '员工' || user.role_name === '管理员';
});

// 数据相关
const loading = ref(false);
const clients = ref([]);
const carePlans = ref([]);
const planGoals = ref([]);
const planAppointments = ref([]);
const staffList = ref([]);
const selectedClient = ref(null);
const services = ref([]);
const availableStaff = ref([]);
const appointmentFormVisible = ref(false);
const deleteAppointmentDialogVisible = ref(false);
const isEditingAppointment = ref(false);
const currentAppointmentToDelete = ref(null);
const sortBy = ref('');
const sortOrder = ref(null);

// 筛选相关
const clientFilter = ref('');
const filteredClients = computed(() => {
  if (!clientFilter.value) return clients.value;
  const searchText = clientFilter.value.toLowerCase();
  return clients.value.filter(client => {
    const fullName = `${client.last_name}${client.first_name}`;
    return client.client_id.toString().includes(searchText) ||
           fullName.toLowerCase().includes(searchText);
  });
});

// 对话框控制
const planDetailVisible = ref(false);
const planFormVisible = ref(false);
const goalFormVisible = ref(false);
const currentPlan = ref(null);
const isEditingPlan = ref(false);
const isEditingGoal = ref(false);
const reportDialogVisible = ref(false);
const currentReport = ref(null);

// 表单数据
const planForm = ref({
  plan_type: '',
  plan_state: '',
  start_date: '',
  end_date: '',
  staff: null
});

const goalForm = ref({
  description: '',
  goal_state: '未达成'
});

const appointmentForm = ref({
  service: null,
  schedule_date: '',
  schedule_time: '',
  end_time: '',
  staff: null,
  state: '待确认'
});

// 获取状态对应的类型
const getPlanStateType = (state) => {
  const types = {
    '待开始': 'info',
    '进行中': 'warning',
    '已完成': 'success'
  };
  return types[state] || 'info';
};

const getAppointmentStateType = (state) => {
  const types = {
    '待确认': 'warning',
    '已预约': 'primary',
    '已结束': 'success',
    '已取消': 'danger'
  };
  return types[state] || 'info';
};

// 判断是否可以选择员工
const canSelectStaff = computed(() => {
  return appointmentForm.value.schedule_date && 
         appointmentForm.value.schedule_time && 
         appointmentForm.value.end_time;
});

// 禁用今天之前的日期
const disabledDate = (date) => {
  return date < new Date();
};

// 获取客户列表
const fetchClients = async () => {
  loading.value = true;
  try {
    const response = await http.get('/api/clients/');
    clients.value = response.data;
  } catch (error) {
    console.error('获取客户列表失败:', error);
    ElMessage.error('获取客户列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取计划列表
const fetchCarePlans = async () => {
  loading.value = true;
  try {
    let clientId;
    
    if (isStaff.value && selectedClient.value) {
      // 员工/管理员查看特定客户的计划
      clientId = selectedClient.value.client_id;
    } else if (!isStaff.value) {
      // 客户查看自己的计划，从本地存储获取 client_id
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      clientId = user.client_id;
      
      if (!clientId) {
        ElMessage.error('未找到客户ID信息');
        return;
      }
    } else {
      // 其他情况，如员工未选择客户时
      return;
    }
    
    const response = await http.get(`/api/plans/get/${clientId}/`);
    carePlans.value = response.data;
  } catch (error) {
    console.error('获取护理计划失败:', error);
    ElMessage.error('获取护理计划失败');
  } finally {
    loading.value = false;
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

// 获取计划目标
const fetchPlanGoals = async (planId) => {
  try {
    const response = await http.get(`/api/plans/get_goals/${planId}/`);
    planGoals.value = response.data;
  } catch (error) {
    console.error('获取计划目标失败:', error);
    ElMessage.error('获取计划目标失败');
  }
};

// 获取计划预约
const fetchPlanAppointments = async (planId) => {
  try {
    const response = await http.get(`/api/plans/get_appointments/${planId}/`);
    planAppointments.value = response.data;
  } catch (error) {
    console.error('获取计划预约失败:', error);
    ElMessage.error('获取计划预约失败');
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

// 查看客户计划
const viewClientPlans = (client) => {
  selectedClient.value = client;
  fetchCarePlans();
};

// 返回客户列表
const backToClientList = () => {
  selectedClient.value = null;
  carePlans.value = [];
};

// 查看计划详情
const viewPlanDetail = async (plan) => {
  currentPlan.value = plan;
  await Promise.all([
    fetchPlanGoals(plan.plan_id),
    fetchPlanAppointments(plan.plan_id)
  ]);
  planDetailVisible.value = true;
};

// 创建计划
const createPlan = async () => {
  if (isStaff.value && !selectedClient.value) {
    ElMessage.warning('请先选择客户');
    return;
  }
  isEditingPlan.value = false;
  planForm.value = {
    plan_type: '康复护理',
    plan_state: '待开始',
    start_date: '',
    end_date: '',
    staff: null
  };
  await fetchStaffList();
  planFormVisible.value = true;
};

// 编辑计划
const editPlan = async (plan) => {
  isEditingPlan.value = true;
  planForm.value = {
    plan_id: plan.plan_id,
    plan_type: plan.plan_type,
    plan_state: plan.plan_state,
    start_date: plan.start_date,
    end_date: plan.end_date,
    staff: plan.staff
  };
  await fetchStaffList();
  planFormVisible.value = true;
};

// 保存计划
const savePlan = async () => {
  try {
    // 检查开始日期和结束日期是否填写
    if (!planForm.value.start_date || !planForm.value.end_date) {
      ElMessage.error('开始日期和结束日期为必填项');
      return;
    }
    
    const payload = { ...planForm.value };
    if (isStaff.value && selectedClient.value && !isEditingPlan.value) {
      payload.client = selectedClient.value.client_id;
    }

    const response = await http[isEditingPlan.value ? 'patch' : 'post'](
      `/api/plans/${isEditingPlan.value ? 'update' : 'create'}/`,
      payload
    );

    if (response.status === 200) {
      ElMessage.success(isEditingPlan.value ? '更新成功' : '创建成功');
      planFormVisible.value = false;
      fetchCarePlans();
    }
  } catch (error) {
    console.error(isEditingPlan.value ? '更新失败:' : '创建失败:', error);
    ElMessage.error(isEditingPlan.value ? '更新失败' : '创建失败');
  }
};

// 删除计划
const deletePlan = async (plan) => {
  try {
    await ElMessageBox.confirm('确定要删除这个计划吗？', '提示', {
      type: 'warning'
    });
    
    const response = await http.delete(`/api/plans/delete/${plan.plan_id}/`);
    if (response.status === 200) {
      ElMessage.success('删除成功');
      fetchCarePlans();
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 更新计划评分
const updatePlanScore = async (plan) => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const clientId = user.client_id;
    if (!clientId) {
      ElMessage.error('未找到客户ID信息');
      return;
    }
    const response = await http.patch(`/api/plans/score/${clientId}/`, {
      plan_id: plan.plan_id,
      plan_satisfaction: plan.plan_satisfaction
    });

    if (response.status === 200) {
      ElMessage.success('评分更新成功');
      fetchCarePlans();
    }
  } catch (error) {
    console.error('评分更新失败:', error);
    ElMessage.error('评分更新失败');
  }
};

// 创建目标
const createGoal = () => {
  isEditingGoal.value = false;
  goalForm.value = {
    description: '',
    goal_state: '未达成'
  };
  goalFormVisible.value = true;
};

// 编辑目标
const editGoal = (goal) => {
  isEditingGoal.value = true;
  goalForm.value = {
    goal_id: goal.goal_id,
    description: goal.description,
    goal_state: goal.goal_state
  };
  goalFormVisible.value = true;
};

// 保存目标
const saveGoal = async () => {
  try {
    const payload = { ...goalForm.value };
    if (!isEditingGoal.value) {
      payload.plan = currentPlan.value.plan_id;
    }

    const response = await http[isEditingGoal.value ? 'patch' : 'post'](
      `/api/goals/${isEditingGoal.value ? 'update' : 'create'}/`,
      payload
    );

    if (response.status === 200) {
      ElMessage.success(isEditingGoal.value ? '更新成功' : '创建成功');
      goalFormVisible.value = false;
      fetchPlanGoals(currentPlan.value.plan_id);
    }
  } catch (error) {
    console.error(isEditingGoal.value ? '更新失败:' : '创建失败:', error);
    ElMessage.error(isEditingGoal.value ? '更新失败' : '创建失败');
  }
};

// 删除目标
const deleteGoal = async (goal) => {
  try {
    await ElMessageBox.confirm('确定要删除这个目标吗？', '提示', {
      type: 'warning'
    });
    
    const response = await http.delete(`/api/goals/delete/${goal.goal_id}/`);
    if (response.status === 200) {
      ElMessage.success('删除成功');
      fetchPlanGoals(currentPlan.value.plan_id);
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 更新预约评分
const updateAppointmentScore = async (appointment) => {
  try {
    // 从本地存储获取客户ID
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const clientId = user.client_id;
    
    if (!clientId) {
      ElMessage.error('未找到客户ID信息');
      return;
    }
    
    const response = await http.patch(`/api/appointments/update/${clientId}/`, {
      appointment_id: appointment.appointment_id,
      satisfaction: appointment.satisfaction
    });

    if (response.status === 200) {
      ElMessage.success('评分更新成功');
      fetchPlanAppointments(currentPlan.value.plan_id);
    }
  } catch (error) {
    console.error('评分更新失败:', error);
    ElMessage.error('评分更新失败');
  }
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

// 创建预约
const createAppointment = async () => {
  isEditingAppointment.value = false;
  appointmentForm.value = {
    service: null,
    schedule_date: '',
    schedule_time: '',
    end_time: '',
    staff: null,
    state: '待确认'
  };
  await fetchServices();
  appointmentFormVisible.value = true;
};

// 编辑预约
const editAppointment = async (appointment) => {
  isEditingAppointment.value = true;
  appointmentForm.value = {
    appointment_id: appointment.appointment_id,
    service: appointment.service,
    schedule_date: appointment.schedule_date,
    schedule_time: appointment.schedule_time.substring(0, 5),
    end_time: appointment.end_time,
    staff: appointment.staff,
    state: appointment.state
  };
  await fetchServices();
  if (canSelectStaff.value) {
    await fetchAvailableStaff();
  }
  appointmentFormVisible.value = true;
};

// 保存预约
const saveAppointment = async () => {
  try {
    const formatTime = (time) => {
      if (!time) return '';
      return time.length === 5 ? `${time}:00` : time;
    };

    const payload = {
      schedule_date: appointmentForm.value.schedule_date,
      schedule_time: formatTime(appointmentForm.value.schedule_time),
      end_time: formatTime(appointmentForm.value.end_time),
      service: appointmentForm.value.service,
      state: appointmentForm.value.state,
      plan: currentPlan.value.plan_id
    };

    if (isStaff.value) {
      payload.staff = appointmentForm.value.staff;
    }

    if (isEditingAppointment.value) {
      payload.appointment_id = appointmentForm.value.appointment_id;
    }

    // 获取客户ID
    const clientId = selectedClient.value ? selectedClient.value.client_id : currentPlan.value.client;
    
    const response = await http[isEditingAppointment.value ? 'patch' : 'post'](
      `/api/appointments/${isEditingAppointment.value ? 'update' : 'create'}/${clientId}/`,
      payload
    );

    if (response.status === 200) {
      ElMessage.success(isEditingAppointment.value ? '更新成功' : '创建成功');
      appointmentFormVisible.value = false;
      fetchPlanAppointments(currentPlan.value.plan_id);
    }
  } catch (error) {
    console.error(isEditingAppointment.value ? '更新失败:' : '创建失败:', error);
    ElMessage.error(isEditingAppointment.value ? '更新失败' : '创建失败');
  }
};

// 删除预约
const deleteAppointment = (appointment) => {
  currentAppointmentToDelete.value = appointment;
  deleteAppointmentDialogVisible.value = true;
};

// 确认删除预约
const confirmDeleteAppointment = async () => {
  try {
    const response = await http.delete(
      `/api/appointments/delete/${currentAppointmentToDelete.value.appointment_id}/`
    );
    if (response.status === 200) {
      ElMessage.success('删除成功');
      deleteAppointmentDialogVisible.value = false;
      fetchPlanAppointments(currentPlan.value.plan_id);
    }
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 获取进度报告
const getReport = async (plan) => {
  try {
    const response = await http.get(`/api/plans/get_report/${plan.plan_id}/`);
    currentReport.value = response.data;
    reportDialogVisible.value = true;
  } catch (error) {
    console.error('获取进度报告失败:', error);
    ElMessage.error('获取进度报告失败');
  }
};

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  sortBy.value = prop;
  sortOrder.value = order;
};

// 计算排序后的计划列表
const sortedCarePlans = computed(() => {
  if (!sortBy.value || !sortOrder.value) {
    return carePlans.value;
  }

  return [...carePlans.value].sort((a, b) => {
    const fieldA = a[sortBy.value];
    const fieldB = b[sortBy.value];
    
    if (sortOrder.value === 'ascending') {
      return fieldA.localeCompare(fieldB);
    } else if (sortOrder.value === 'descending') {
      return fieldB.localeCompare(fieldA);
    }
    return 0;
  });
});

// 组件挂载时获取数据
onMounted(async () => {
  if (isStaff.value) {
    await fetchClients();
  } else {
    await fetchCarePlans();
  }
});
</script>

<style scoped>
.care-plan {
  padding: 20px;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-item {
  width: 300px;
}

.header-section {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.empty-text {
  color: #909399;
  text-align: center;
  padding: 20px;
}

.unassigned {
  color: #909399;
}

:deep(.el-rate) {
  margin-top: 4px;
}

.dialog-footer {
  text-align: right;
}

.report-section {
  margin-top: 24px;
}

.report-section h3 {
  margin-bottom: 16px;
  font-weight: 500;
}

:deep(.el-statistic) {
  margin-bottom: 20px;
}

:deep(.el-statistic__title) {
  font-size: 14px;
  color: #606266;
}

:deep(.el-statistic__content) {
  font-size: 24px;
  color: #303133;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 5px;
  min-width: 0;
}

/* 客户列表中的按钮组居中对齐 */
.client-list-view .button-group {
  justify-content: center;
}

/* 调整按钮大小和间距，使其能更好地适应紧凑布局 */
.button-group .el-button--small {
  padding: 5px 10px;
  margin: 0;
  font-size: 12px;
}

.plan-list-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-table) {
  flex: 1;
  width: 100% !important;
}

:deep(.el-table__body) {
  width: 100% !important;
}

:deep(.el-table__header) {
  width: 100% !important;
}
</style> 