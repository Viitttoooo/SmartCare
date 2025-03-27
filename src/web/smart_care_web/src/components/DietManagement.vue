<template>
  <div class="diet-management">
    <!-- 管理员/员工视图：客户列表 -->
    <div v-if="isStaff" class="client-list-view" v-show="!selectedClient">
      <div class="panel">
        <div class="panel-header">
          <h2>客户列表</h2>
          <div class="search-bar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索客户ID或姓名"
              clearable
              prefix-icon="Search"
              style="width: 300px"
            />
          </div>
        </div>
        
        <el-table 
          :data="filteredClients" 
          style="width: 100%" 
          v-loading="loading"
          border
          stripe
          highlight-current-row
          class="custom-table"
        >
          <el-table-column label="客户ID" prop="client_id" width="100" />
          <el-table-column label="姓名">
            <template #default="{ row }">
              {{ row.last_name + row.first_name }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewClientDietPlans(row)">
                查看膳食计划
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 客户视图：直接显示膳食计划 -->
    <div v-if="!isStaff || selectedClient" class="diet-plans-view">
      <!-- 返回按钮（仅管理员/员工可见） -->
      <div v-if="isStaff" class="back-button">
        <el-button @click="backToClientList">
          <el-icon><ArrowLeft /></el-icon>
          返回客户列表
        </el-button>
      </div>

      <!-- 膳食计划列表 -->
      <div class="panel">
        <div class="panel-header">
          <h2>{{ isStaff ? `${selectedClient?.last_name}${selectedClient?.first_name} - ` : ''}}膳食计划列表</h2>
          <div class="filter-section">
            <el-date-picker
              v-model="dateFilter"
              type="date"
              placeholder="按日期筛选"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 180px; margin-right: 16px;"
              clearable
            />
            <el-button v-if="isStaff" type="primary" @click="createDietPlan">
              <el-icon><Plus /></el-icon> 新增膳食计划
            </el-button>
          </div>
        </div>

        <el-table 
          :data="sortedAndFilteredDietPlans" 
          style="width: 100%" 
          v-loading="loading"
          border
          stripe
          highlight-current-row
          class="custom-table"
        >
          <el-table-column label="日期" prop="diet_date" width="180" />
          <el-table-column label="制定人">
            <template #default="{ row }">
              {{ getStaffName(row.staff) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center">
            <template #default="{ row }">
              <div class="button-group">
                <el-button type="primary" size="small" @click="viewDietPlanDetail(row)">
                  详情
                </el-button>
                <el-button v-if="isStaff" type="danger" size="small" @click="deleteDietPlan(row)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 膳食计划详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="isEditing ? '编辑膳食计划' : '膳食计划详情'"
      width="75%"
      class="custom-dialog"
    >
      <div v-if="currentDietPlan" class="diet-plan-detail">
        <!-- 客户饮食偏好 -->
        <div class="detail-section dietary-preference" v-if="selectedClient">
          <h3>客户饮食偏好</h3>
          <div class="preference-list">
            <div class="avoid-foods">
              <span class="label">忌口：</span>
              <div class="tag-group">
                <el-tag 
                  v-for="food in selectedClient.dietary_preference.忌口"
                  :key="food"
                  type="danger"
                  effect="light"
                  style="margin-right: 8px; margin-bottom: 8px"
                >
                  {{ food }}
                </el-tag>
                <span v-if="selectedClient.dietary_preference.忌口.length === 0" class="empty-text">无</span>
              </div>
            </div>
            <div class="favorite-foods">
              <span class="label">爱吃：</span>
              <div class="tag-group">
                <el-tag
                  v-for="food in selectedClient.dietary_preference.爱吃"
                  :key="food"
                  type="success"
                  effect="light"
                  style="margin-right: 8px; margin-bottom: 8px"
                >
                  {{ food }}
                </el-tag>
                <span v-if="selectedClient.dietary_preference.爱吃.length === 0" class="empty-text">无</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section-container">
          <!-- 基本信息 -->
          <div class="detail-section basic-info">
            <h3>基本信息</h3>
            <el-form :model="editForm" label-width="120px" class="diet-form">
              <el-form-item label="日期">
                <el-date-picker
                  v-model="editForm.diet_date"
                  type="date"
                  :disabled="!isEditing"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="制定人">
                <el-select
                  v-model="editForm.staff"
                  placeholder="选择制定人"
                  :disabled="!isEditing"
                  style="width: 100%"
                >
                  <el-option
                    v-for="staff in staffList"
                    :key="staff.staff_id"
                    :label="`${staff.last_name}${staff.first_name}`"
                    :value="staff.staff_id"
                  />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <!-- 营养需求 -->
          <div class="detail-section nutrition-requirements">
            <h3>营养需求</h3>
            <el-form :model="editForm.nutrition_requirements" label-width="120px" class="diet-form">
              <el-form-item 
                v-for="(value, key) in editForm.nutrition_requirements"
                :key="key"
                :label="key"
              >
                <div class="nutrition-input">
                  <el-input-number
                    v-model="editForm.nutrition_requirements[key].数量"
                    :disabled="!isEditing"
                    :min="0"
                    :precision="2"
                    :step="0.1"
                  />
                  <span class="unit">{{ value.单位 }}</span>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 智能推荐区域 -->
        <div class="detail-section smart-recommendation">
          <div class="section-header">
            <h3>智能推荐</h3>
            <el-button 
              v-if="isStaff" 
              type="primary" 
              size="small" 
              @click="generateRecommendation"
              :loading="isGenerating"
              :disabled="isGenerating"
            >
              获取推荐
            </el-button>
          </div>
          <div class="recommendation-content">
            <div v-if="isGenerating" class="generating-state">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <span>正在生成智能推荐，请稍候...</span>
            </div>
            <div v-else-if="!currentDietPlan.smart_recommendation" class="empty-recommendation">
              暂无推荐
            </div>
            <div v-else class="markdown-content">
              <div v-html="renderMarkdown(currentDietPlan.smart_recommendation)"></div>
              <div class="disclaimer">
                <el-icon><InfoFilled /></el-icon>
                <span>内容由AI生成，请自行甄别</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 实际营养摄入 -->
        <div class="detail-section nutrition-taken">
          <h3>实际营养摄入</h3>
          <div class="nutrition-cards">
            <div 
              v-for="(value, key) in currentDietPlan.nutrition_taken"
              :key="key"
              class="nutrition-card"
            >
              <div class="nutrition-name">{{ key }}</div>
              <div class="nutrition-value">{{ value.数量.toFixed(2) }}</div>
              <div class="nutrition-unit">{{ value.单位 }}</div>
            </div>
          </div>
        </div>

        <!-- 三餐安排 -->
        <div class="detail-section meals">
          <h3>三餐安排</h3>
          <div class="meals-container">
            <div v-for="meal in ['breakfast', 'lunch', 'dinner']" :key="meal" class="meal-section">
              <h4>{{ getMealName(meal) }}</h4>
              <div class="meal-content">
                <template v-if="!isEditing">
                  <div class="meal-tags">
                    <el-tag
                      v-for="recipe in currentDietPlan[meal]"
                      :key="recipe"
                      :type="getRecipeTagType(recipe)"
                      effect="light"
                      class="meal-tag"
                    >
                      {{ recipe }}
                    </el-tag>
                    <span v-if="currentDietPlan[meal].length === 0" class="empty-text">未设置</span>
                  </div>
                </template>
                <template v-else>
                  <div class="edit-meal">
                    <el-select
                      v-model="editForm[meal]"
                      multiple
                      filterable
                      placeholder="选择菜品"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="recipe in recipes"
                        :key="recipe.recipe_id"
                        :label="recipe.recipe_name"
                        :value="recipe.recipe_id"
                        :class="getRecipeClass(recipe)"
                      />
                    </el-select>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <div class="button-group-right">
            <el-button @click="detailVisible = false">关闭</el-button>
            <template v-if="isStaff">
              <el-button v-if="!isEditing" type="primary" @click="startEdit">
                编辑
              </el-button>
              <el-button v-else type="primary" @click="saveDietPlan">
                保存
              </el-button>
            </template>
          </div>
        </span>
      </template>
    </el-dialog>

    <!-- 新增膳食计划弹窗 -->
    <el-dialog
      v-model="createVisible"
      title="新增膳食计划"
      width="50%"
      class="custom-dialog"
    >
      <el-form :model="createForm" label-width="120px" class="create-form">
        <el-form-item label="日期" required>
          <el-date-picker
            v-model="createForm.diet_date"
            type="date"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="制定人" required>
          <el-select
            v-model="createForm.staff"
            placeholder="选择制定人"
            style="width: 100%"
          >
            <el-option
              v-for="staff in staffList"
              :key="staff.staff_id"
              :label="`${staff.last_name}${staff.first_name}`"
              :value="staff.staff_id"
            />
          </el-select>
        </el-form-item>
        
        <div class="form-section-title">营养需求</div>
        <el-divider></el-divider>
        
        <el-form-item 
          v-for="(value, key) in createForm.nutrition_requirements"
          :key="key"
          :label="key"
        >
          <div class="nutrition-input">
            <el-input-number
              v-model="createForm.nutrition_requirements[key].数量"
              :min="0"
              :precision="2"
              :step="0.1"
            />
            <span class="unit">{{ value.单位 }}</span>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <div class="button-group-right">
            <el-button @click="createVisible = false">取消</el-button>
            <el-button type="primary" @click="submitCreateDietPlan">
              确定
            </el-button>
          </div>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { ArrowLeft, Plus, Loading, InfoFilled } from '@element-plus/icons-vue';
import http from '../utils/axios';
import { marked } from 'marked';

// 数据
const loading = ref(false);
const clients = ref([]);
const selectedClient = ref(null);
const dietPlans = ref([]);
const staffList = ref([]);
const recipes = ref([]);
const searchQuery = ref('');
const detailVisible = ref(false);
const createVisible = ref(false);
const isEditing = ref(false);
const currentDietPlan = ref(null);
const dateFilter = ref('');
const isGenerating = ref(false);

// 从本地存储获取用户信息
const user = ref(JSON.parse(localStorage.getItem('user')));
const isStaff = computed(() => 
  user.value?.role_name === '管理员' || user.value?.role_name === '员工'
);

// 表单数据
const createForm = ref({
  diet_date: '',
  staff: null,
  nutrition_requirements: {
    热量: { 单位: 'kcal', 数量: 0 },
    脂肪: { 单位: 'g', 数量: 0 },
    蛋白质: { 单位: 'g', 数量: 0 },
    碳水化合物: { 单位: 'g', 数量: 0 }
  }
});

const editForm = ref({
  diet_date: '',
  staff: null,
  nutrition_requirements: {
    热量: { 单位: 'kcal', 数量: 0 },
    脂肪: { 单位: 'g', 数量: 0 },
    蛋白质: { 单位: 'g', 数量: 0 },
    碳水化合物: { 单位: 'g', 数量: 0 }
  },
  breakfast: [],
  lunch: [],
  dinner: []
});

// 日期格式化函数（修复时区问题）
const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  // 月份是从0开始的，所以需要+1，并且保证两位数
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 检查日期是否已存在膳食计划
const checkDateExist = (date, excludePlanId = null) => {
  const formattedDate = formatDate(date);
  return dietPlans.value.some(plan => 
    plan.diet_date === formattedDate && 
    (excludePlanId === null || plan.diet_plan_id !== excludePlanId)
  );
};

// 客户列表过滤
const filteredClients = computed(() => {
  if (!searchQuery.value) return clients.value;
  const query = searchQuery.value.toLowerCase();
  return clients.value.filter(client => 
    client.client_id.toString().includes(query) ||
    (client.last_name + client.first_name).toLowerCase().includes(query)
  );
});

// 排序和过滤后的膳食计划
const sortedAndFilteredDietPlans = computed(() => {
  let filtered = [...dietPlans.value];
  
  // 应用日期筛选
  if (dateFilter.value) {
    filtered = filtered.filter(plan => plan.diet_date === dateFilter.value);
  }
  
  // 按日期降序排序
  return filtered.sort((a, b) => new Date(b.diet_date) - new Date(a.diet_date));
});

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

// 获取菜品列表
const fetchRecipes = async () => {
  try {
    const response = await http.get('/api/recipes/');
    recipes.value = response.data;
  } catch (error) {
    console.error('获取菜品列表失败:', error);
    ElMessage.error('获取菜品列表失败');
  }
};

// 获取膳食计划列表
const fetchDietPlans = async (clientId) => {
  loading.value = true;
  try {
    const response = await http.get(`/api/diet_plans/${clientId}/`);
    dietPlans.value = response.data;
  } catch (error) {
    console.error('获取膳食计划列表失败:', error);
    ElMessage.error('获取膳食计划列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取膳食计划详情
const fetchDietPlanDetail = async (clientId, dietDate) => {
  try {
    // 格式化日期为 YYYY-MM-DD，修复时区问题
    const formattedDate = formatDate(dietDate);
    
    const response = await http.get(`/api/diet_plans/certain_day/?client_id=${clientId}&diet_date=${formattedDate}`);
    currentDietPlan.value = response.data;
    // 初始化编辑表单
    editForm.value = {
      diet_date: response.data.diet_date,
      staff: response.data.staff,
      nutrition_requirements: response.data.nutrition_requirements,
      breakfast: response.data.breakfast.map(name => 
        recipes.value.find(r => r.recipe_name === name)?.recipe_id
      ).filter(Boolean),
      lunch: response.data.lunch.map(name => 
        recipes.value.find(r => r.recipe_name === name)?.recipe_id
      ).filter(Boolean),
      dinner: response.data.dinner.map(name => 
        recipes.value.find(r => r.recipe_name === name)?.recipe_id
      ).filter(Boolean)
    };
  } catch (error) {
    console.error('获取膳食计划详情失败:', error);
    ElMessage.error('获取膳食计划详情失败');
  }
};

// 查看客户膳食计划
const viewClientDietPlans = (client) => {
  selectedClient.value = client;
  fetchDietPlans(client.client_id);
};

// 返回客户列表
const backToClientList = () => {
  selectedClient.value = null;
  dietPlans.value = [];
};

// 获取员工姓名
const getStaffName = (staffId) => {
  if (!staffId) return '未指定';
  const staff = staffList.value.find(s => s.staff_id === staffId);
  return staff ? `${staff.last_name}${staff.first_name}` : '未知';
};

// 获取餐次名称
const getMealName = (meal) => {
  const mealNames = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐'
  };
  return mealNames[meal];
};

// 判断菜品标签类型
const getRecipeTagType = (recipeName) => {
  if (!selectedClient.value) return '';
  
  const recipe = recipes.value.find(r => r.recipe_name === recipeName);
  if (!recipe) return '';

  const hasAvoidIngredient = recipe.ingredients.some(item =>
    selectedClient.value.dietary_preference.忌口.includes(item.ingredient.ingredient_name)
  );
  if (hasAvoidIngredient) return 'danger';

  const hasFavoriteIngredient = recipe.ingredients.some(item =>
    selectedClient.value.dietary_preference.爱吃.includes(item.ingredient.ingredient_name)
  );
  if (hasFavoriteIngredient) return 'success';

  return '';
};

// 获取菜品类名
const getRecipeClass = (recipe) => {
  if (!selectedClient.value) return '';

  const hasAvoidIngredient = recipe.ingredients.some(item =>
    selectedClient.value.dietary_preference.忌口.includes(item.ingredient.ingredient_name)
  );
  if (hasAvoidIngredient) return 'avoid-recipe';

  const hasFavoriteIngredient = recipe.ingredients.some(item =>
    selectedClient.value.dietary_preference.爱吃.includes(item.ingredient.ingredient_name)
  );
  if (hasFavoriteIngredient) return 'favorite-recipe';

  return '';
};

// 查看膳食计划详情
const viewDietPlanDetail = async (plan) => {
  await fetchDietPlanDetail(plan.client, plan.diet_date);
  detailVisible.value = true;
  isEditing.value = false;
};

// 开始编辑
const startEdit = () => {
  isEditing.value = true;
};

// 保存膳食计划基本信息
const saveDietPlan = async () => {
  try {
    // 格式化日期为 YYYY-MM-DD，修复时区问题
    const formattedDate = formatDate(editForm.value.diet_date);
    
    // 检查除当前计划外是否有同日期的计划
    if (checkDateExist(editForm.value.diet_date, currentDietPlan.value.diet_plan_id)) {
      ElMessage.error('该客户在所选日期已有膳食计划，请选择其他日期');
      return;
    }

    // 更新基本信息
    await http.patch(`/api/diet_plans/update_fields/${currentDietPlan.value.diet_plan_id}/`, {
      diet_date: formattedDate,
      staff: editForm.value.staff,
      nutrition_requirements: editForm.value.nutrition_requirements
    });

    // 更新三餐
    const meals = ['breakfast', 'lunch', 'dinner'];
    const mealTypes = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' };

    for (const meal of meals) {
      await http.patch('/api/diet_plans/update/', {
        diet_plan_id: currentDietPlan.value.diet_plan_id,
        type: mealTypes[meal],
        recipe_ids: editForm.value[meal]
      });
    }

    ElMessage.success('更新成功');
    isEditing.value = false;
    await fetchDietPlanDetail(currentDietPlan.value.client, formattedDate);
    await fetchDietPlans(selectedClient.value.client_id);
  } catch (error) {
    console.error('更新失败:', error);
    ElMessage.error('更新失败');
  }
};

// 删除膳食计划
const deleteDietPlan = async (plan) => {
  try {
    await http.delete(`/api/diet_plans/delete_entire/${plan.diet_plan_id}/`);
    ElMessage.success('删除成功');
    await fetchDietPlans(selectedClient.value.client_id);
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 创建膳食计划
const createDietPlan = () => {
  createForm.value = {
    diet_date: '',
    staff: null,
    nutrition_requirements: {
      热量: { 单位: 'kcal', 数量: 0 },
      脂肪: { 单位: 'g', 数量: 0 },
      蛋白质: { 单位: 'g', 数量: 0 },
      碳水化合物: { 单位: 'g', 数量: 0 }
    }
  };
  createVisible.value = true;
};

// 提交创建膳食计划
const submitCreateDietPlan = async () => {
  try {
    // 格式化日期为 YYYY-MM-DD，修复时区问题
    const formattedDate = formatDate(createForm.value.diet_date);
    
    // 检查是否有同日期的计划
    if (checkDateExist(createForm.value.diet_date)) {
      ElMessage.error('该客户在所选日期已有膳食计划，请选择其他日期');
      return;
    }
    
    await http.post('/api/diet_plans/create_record/', {
      client: selectedClient.value.client_id,
      diet_date: formattedDate,
      staff: createForm.value.staff,
      nutrition_requirements: createForm.value.nutrition_requirements
    });
    
    ElMessage.success('创建成功');
    createVisible.value = false;
    await fetchDietPlans(selectedClient.value.client_id);
  } catch (error) {
    console.error('创建失败:', error);
    ElMessage.error('创建失败');
  }
};

// Markdown渲染函数
const renderMarkdown = (text) => {
  if (!text) return '';
  return marked(text);
};

// 生成智能推荐
const generateRecommendation = async () => {
  if (!currentDietPlan.value || !currentDietPlan.value.diet_plan_id) return;
  
  isGenerating.value = true;
  try {
    // 设置较长的超时时间，因为大模型生成可能需要较长时间
    const response = await http.patch(
      `/api/diet_plans/generate_diet_recommendation/${currentDietPlan.value.diet_plan_id}/`,
      {}, // 空对象作为请求体
      { 
        timeout: 120000, // 设置2分钟超时
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    // 只要收到200状态码，就认为成功接收到数据
    if (response.status === 200) {
      // 更新当前膳食计划的智能推荐
      currentDietPlan.value.smart_recommendation = response.data.smart_recommendation;
      ElMessage.success('智能推荐生成成功');
      
      // 刷新膳食计划列表，确保数据同步
      if (selectedClient.value) {
        await fetchDietPlans(selectedClient.value.client_id);
      }
    }
  } catch (error) {
    console.error('生成智能推荐失败:', error);
    
    // 细化错误处理
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('生成智能推荐超时，请稍后再试');
    } else if (error.response) {
      ElMessage.error(`生成失败: ${error.response.data?.message || '服务器错误'}`);
    } else {
      ElMessage.error('生成智能推荐失败，请稍后再试');
    }
    
    // 尝试重新获取当前膳食计划数据
    try {
      if (currentDietPlan.value && selectedClient.value) {
        await fetchDietPlanDetail(selectedClient.value.client_id, currentDietPlan.value.diet_date);
      }
    } catch (refreshError) {
      console.error('刷新膳食计划详情失败:', refreshError);
    }
  } finally {
    isGenerating.value = false;
  }
};

// 初始化
onMounted(async () => {
  if (isStaff.value) {
    await fetchClients();
  } else {
    // 客户视图：直接获取自己的膳食计划
    await fetchDietPlans(user.value.client_id);
  }
  await fetchStaffList();
  await fetchRecipes();
});
</script>

<style scoped>
.diet-management {
  padding: 20px;
  color: #333;
}

.panel {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.search-bar {
  margin-bottom: 0;
}

.back-button {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  align-items: center;
}

/* 表格样式 */
.custom-table {
  border-radius: 6px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #fafafa;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: #f0f9ff;
}

/* 详情弹窗样式 */
.custom-dialog :deep(.el-dialog__body) {
  padding: 20px 30px;
}

.diet-plan-detail {
  overflow-y: auto;
  max-height: 70vh;
}

.detail-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.detail-section-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 1.2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.preference-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.avoid-foods,
.favorite-foods {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.label {
  font-weight: bold;
  color: #606266;
  margin-bottom: 5px;
}

.empty-text {
  color: #909399;
  font-style: italic;
}

.diet-form {
  margin-top: 15px;
}

.nutrition-input {
  display: flex;
  align-items: center;
}

.unit {
  margin-left: 8px;
  color: #606266;
}

/* 营养摄入卡片 */
.nutrition-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.nutrition-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.nutrition-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.nutrition-name {
  font-weight: bold;
  color: #606266;
  margin-bottom: 8px;
}

.nutrition-value {
  font-size: 1.5rem;
  color: #409EFF;
  margin-bottom: 5px;
}

.nutrition-unit {
  color: #909399;
  font-size: 0.9rem;
}

/* 三餐样式 */
.meals-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.meal-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
}

.meal-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #2c3e50;
  font-size: 1.1rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.meal-content {
  margin-top: 10px;
}

.meal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meal-tag {
  margin-bottom: 8px;
}

.avoid-recipe {
  color: #f56c6c;
}

.favorite-recipe {
  color: #67c23a;
}

.edit-meal {
  margin-bottom: 10px;
}

/* 创建表单样式 */
.create-form {
  padding: 10px;
}

.form-section-title {
  font-weight: bold;
  color: #2c3e50;
  margin: 20px 0 5px 0;
  font-size: 1.1rem;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .detail-section-container {
    grid-template-columns: 1fr;
  }
  
  .meals-container {
    grid-template-columns: 1fr;
  }
  
  .nutrition-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-section {
    width: 100%;
    justify-content: space-between;
  }
}

/* 按钮组样式 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.button-group-right {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 弹窗底部按钮样式 */
.dialog-footer {
  width: 100%;
  display: block;
}

/* 智能推荐区域样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 1.2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.section-header h3 {
  margin: 0;
}

.recommendation-content {
  min-height: 150px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #909399;
}

.loading-icon {
  font-size: 24px;
  margin-bottom: 10px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.empty-recommendation {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #909399;
  font-style: italic;
}

.markdown-content {
  padding: 10px;
  line-height: 1.6;
}

.disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #e0e0e0;
  color: #909399;
  font-size: 0.9rem;
}

.disclaimer .el-icon {
  margin-right: 5px;
  color: #E6A23C;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.markdown-content :deep(p) {
  margin-bottom: 12px;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}

.markdown-content :deep(li) {
  margin-bottom: 4px;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #409EFF;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  padding-left: 16px;
  margin-left: 0;
  color: #6a737d;
}

.markdown-content :deep(code) {
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}
</style> 