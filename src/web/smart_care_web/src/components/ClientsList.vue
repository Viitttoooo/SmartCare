<template>
  <div class="clients-list">
    <el-scrollbar>
      <!-- 搜索和筛选区域 -->
      <div class="filter-container">
        <div class="filter-section client-filter-section">
          <div class="section-title">客户筛选</div>
          <div class="filter-content">
            <el-input
              v-model="searchQuery"
              placeholder="搜索客户姓名或ID"
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="selectedLevel"
              placeholder="护理等级"
              clearable
              class="level-filter"
            >
              <el-option
                v-for="level in [1, 2, 3, 4, 5]"
                :key="level"
                :label="`${level}级`"
                :value="level"
              />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 客户列表区域 -->
      <div class="clients-content-wrapper">
        <div class="clients-content">
          <div 
            v-for="client in filteredClients" 
            :key="client.client_id"
            class="client-card"
          >
            <el-collapse v-model="activeNames">
              <el-collapse-item 
                :name="client.client_id"
              >
                <template #title>
                  <div class="client-item">
                    <div class="client-basic-info">
                      <div class="name-id-row">
                        <span class="client-name">
                          {{ client.last_name }}{{ client.first_name }}
                        </span>
                        <el-tag 
                          size="small" 
                          effect="plain" 
                          :type="client.gender === '男' ? 'info' : 'danger'"
                          class="gender-tag"
                        >
                          {{ client.gender }}
                        </el-tag>
                        <span class="client-id">ID: {{ client.client_id }}</span>
                      </div>
                    </div>
                    <div class="care-level" v-if="client.care_level">
                      <span class="care-label">护理等级:</span>
                      <el-tag 
                        :type="getCareTagType(client.care_level)" 
                        size="small" 
                        effect="light"
                        class="care-tag"
                      >
                        {{ client.care_level }}级
                      </el-tag>
                    </div>
                  </div>
                </template>
                
                <!-- 客户详细信息 -->
                <div class="client-details">
                  <div class="profile-header">
                    <h3>客户详细信息</h3>
                    <el-button 
                      type="primary" 
                      @click.stop="toggleEdit(client)"
                      class="edit-button"
                    >
                      <el-icon v-if="isEditing && editingClientId === client.client_id"><Check /></el-icon>
                      <el-icon v-else><Edit /></el-icon>
                      <span>{{ isEditing && editingClientId === client.client_id ? '保存' : '修改信息' }}</span>
                    </el-button>
                  </div>

                  <div class="details-container">
                    <div class="details-section">
                      <div class="section-title">基本信息</div>
                      <el-descriptions :column="2" border>
                        <el-descriptions-item label="姓">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-input v-model="editedInfo.last_name" />
                          </template>
                          <template v-else>{{ client.last_name }}</template>
                        </el-descriptions-item>
                        <el-descriptions-item label="名">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-input v-model="editedInfo.first_name" />
                          </template>
                          <template v-else>{{ client.first_name }}</template>
                        </el-descriptions-item>
                        <el-descriptions-item label="性别">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-select v-model="editedInfo.gender">
                              <el-option label="男" value="男" />
                              <el-option label="女" value="女" />
                            </el-select>
                          </template>
                          <template v-else>
                            <el-tag 
                              :type="client.gender === '男' ? 'info' : 'danger'" 
                              effect="plain" 
                              size="small"
                            >
                              {{ client.gender }}
                            </el-tag>
                          </template>
                        </el-descriptions-item>
                        <el-descriptions-item label="出生日期">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-date-picker 
                              v-model="editedInfo.birth_date" 
                              type="date" 
                              format="YYYY-MM-DD"
                              value-format="YYYY-MM-DD"
                            />
                          </template>
                          <template v-else>{{ client.birth_date }}</template>
                        </el-descriptions-item>
                        <el-descriptions-item label="护理等级">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-input-number v-model="editedInfo.care_level" :min="1" :max="5" />
                          </template>
                          <template v-else>
                            <el-tag :type="getCareTagType(client.care_level)" effect="light">{{ client.care_level }} 级</el-tag>
                          </template>
                        </el-descriptions-item>
                        <el-descriptions-item label="婚姻状况">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-select v-model="editedInfo.marital">
                              <el-option label="已婚" value="已婚" />
                              <el-option label="未婚" value="未婚" />
                              <el-option label="离婚" value="离婚" />
                              <el-option label="丧偶" value="丧偶" />
                              <el-option label="分居" value="分居" />
                            </el-select>
                          </template>
                          <template v-else>
                            {{ client.marital || '未填写' }}
                          </template>
                        </el-descriptions-item>
                        <el-descriptions-item label="收入范围">
                          <template v-if="isEditing && editingClientId === client.client_id">
                            <el-select v-model="editedInfo.income_range">
                              <el-option label="小于3000元/月" value="小于3000元/月" />
                              <el-option label="3000-6000元/月" value="3000-6000元/月" />
                              <el-option label="大于6000元/月" value="大于6000元/月" />
                            </el-select>
                          </template>
                          <template v-else>
                            {{ client.income_range || '未填写' }}
                          </template>
                        </el-descriptions-item>
                      </el-descriptions>
                    </div>

                    <div class="details-section">
                      <div class="section-title">护理需求</div>
                      <div class="care-info-box">
                        <template v-if="isEditing && editingClientId === client.client_id">
                          <el-input v-model="editedInfo.care_demand" type="textarea" :rows="4" />
                        </template>
                        <template v-else>
                          <div class="care-text">{{ client.care_demand || '暂无护理需求' }}</div>
                        </template>
                      </div>
                    </div>

                    <div class="details-section">
                      <div class="section-title">病史</div>
                      <div class="care-info-box">
                        <template v-if="isEditing && editingClientId === client.client_id">
                          <el-input v-model="editedInfo.medical_history" type="textarea" :rows="4" />
                        </template>
                        <template v-else>
                          <div class="care-text">{{ client.medical_history || '暂无病史记录' }}</div>
                        </template>
                      </div>
                    </div>

                    <div class="details-section">
                      <div class="section-title">饮食偏好</div>
                      <el-descriptions :column="2" border>
                        <el-descriptions-item label="忌口">
                          <div class="dietary-preferences">
                            <el-tag 
                              v-for="item in getDietaryPreference(client, editedInfo, '忌口')" 
                              :key="item"
                              class="dietary-tag"
                              type="danger"
                              effect="light"
                              :closable="isEditing && editingClientId === client.client_id"
                              @close="removePreference('忌口', item)"
                            >
                              {{ item }}
                            </el-tag>
                            <span v-if="getDietaryPreference(client, editedInfo, '忌口').length === 0" class="empty-text">
                              无忌口食材
                            </span>
                            <el-dropdown 
                              v-if="isEditing && editingClientId === client.client_id" 
                              trigger="click" 
                              @command="item => addPreference('忌口', item)"
                            >
                              <el-button class="add-button" circle size="small">
                                <el-icon><Plus /></el-icon>
                              </el-button>
                              <template #dropdown>
                                <el-dropdown-menu class="ingredient-dropdown">
                                  <el-input
                                    v-model="ingredientSearch"
                                    placeholder="搜索食材"
                                    clearable
                                    class="ingredient-search"
                                  />
                                  <el-scrollbar max-height="200px">
                                    <el-dropdown-item 
                                      v-for="ingredient in filteredIngredients"
                                      :key="ingredient.ingredient_id"
                                      :command="ingredient.ingredient_name"
                                      :disabled="isIngredientInLoves(ingredient.ingredient_name) || isIngredientInAvoids(ingredient.ingredient_name)"
                                    >
                                      {{ ingredient.ingredient_name }}
                                    </el-dropdown-item>
                                  </el-scrollbar>
                                </el-dropdown-menu>
                              </template>
                            </el-dropdown>
                          </div>
                        </el-descriptions-item>
                        <el-descriptions-item label="爱吃">
                          <div class="dietary-preferences">
                            <el-tag 
                              v-for="item in getDietaryPreference(client, editedInfo, '爱吃')" 
                              :key="item"
                              type="success"
                              effect="light"
                              class="dietary-tag"
                              :closable="isEditing && editingClientId === client.client_id"
                              @close="removePreference('爱吃', item)"
                            >
                              {{ item }}
                            </el-tag>
                            <span v-if="getDietaryPreference(client, editedInfo, '爱吃').length === 0" class="empty-text">
                              无特别喜好
                            </span>
                            <el-dropdown 
                              v-if="isEditing && editingClientId === client.client_id" 
                              trigger="click" 
                              @command="item => addPreference('爱吃', item)"
                            >
                              <el-button class="add-button" circle size="small">
                                <el-icon><Plus /></el-icon>
                              </el-button>
                              <template #dropdown>
                                <el-dropdown-menu class="ingredient-dropdown">
                                  <el-input
                                    v-model="ingredientSearch"
                                    placeholder="搜索食材"
                                    clearable
                                    class="ingredient-search"
                                  />
                                  <el-scrollbar max-height="200px">
                                    <el-dropdown-item 
                                      v-for="ingredient in filteredIngredients"
                                      :key="ingredient.ingredient_id"
                                      :command="ingredient.ingredient_name"
                                      :disabled="isIngredientInAvoids(ingredient.ingredient_name) || isIngredientInLoves(ingredient.ingredient_name)"
                                    >
                                      {{ ingredient.ingredient_name }}
                                    </el-dropdown-item>
                                  </el-scrollbar>
                                </el-dropdown-menu>
                              </template>
                            </el-dropdown>
                          </div>
                        </el-descriptions-item>
                      </el-descriptions>
                    </div>

                    <div class="details-section">
                      <div class="section-title">紧急联系人</div>
                      <el-table 
                        :data="getEmergencyContacts(client, editedInfo)" 
                        border 
                        style="width: 100%; min-height: 100px"
                        :show-header="getEmergencyContacts(client, editedInfo) && getEmergencyContacts(client, editedInfo).length > 0"
                        class="custom-table"
                      >
                        <el-table-column prop="relative" label="关系">
                          <template #default="scope">
                            <template v-if="isEditing && editingClientId === client.client_id">
                              <el-input v-model="scope.row.relative" />
                            </template>
                            <template v-else>{{ scope.row.relative }}</template>
                          </template>
                        </el-table-column>
                        <el-table-column prop="phone" label="联系电话">
                          <template #default="scope">
                            <template v-if="isEditing && editingClientId === client.client_id">
                              <el-input 
                                v-model="scope.row.phone"
                                :class="{ 'is-error': !isValidPhone(scope.row.phone) }"
                                @blur="validatePhone(scope.row)"
                              />
                            </template>
                            <template v-else>{{ scope.row.phone }}</template>
                          </template>
                        </el-table-column>
                        <el-table-column v-if="isEditing && editingClientId === client.client_id" width="80">
                          <template #default="scope">
                            <el-button 
                              type="danger" 
                              circle 
                              size="small"
                              @click="removeContact(scope.$index)"
                            >
                              <el-icon><Delete /></el-icon>
                            </el-button>
                          </template>
                        </el-table-column>
                        <template #empty>
                          <div class="no-data-text">暂无紧急联系人</div>
                        </template>
                      </el-table>
                      <div v-if="isEditing && editingClientId === client.client_id" class="add-contact">
                        <el-button type="primary" circle @click="addNewContact">
                          <el-icon><Plus /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus, Delete, Search, Edit, Check } from '@element-plus/icons-vue';
import http from '../utils/axios';

const clients = ref([]);
const activeNames = ref([]);
const isEditing = ref(false);
const editingClientId = ref(null);
const editedInfo = ref({});
const availableIngredients = ref([]);
const searchQuery = ref('');
const selectedLevel = ref('');
const clientIdFilter = ref('');
const ingredientSearch = ref('');

// 获取客户头像背景色
const getAvatarColor = (clientId) => {
  const colors = [
    { bg: 'linear-gradient(135deg, #4b93e0, #7eb9ff)', text: 'white' }, // 蓝色
    { bg: 'linear-gradient(135deg, #67c23a, #95d475)', text: 'white' }, // 绿色
    { bg: 'linear-gradient(135deg, #e6a23c, #f3d19e)', text: '#5c4500' }, // 黄色
    { bg: 'linear-gradient(135deg, #f56c6c, #fab6b6)', text: 'white' }, // 红色
    { bg: 'linear-gradient(135deg, #909399, #c8c9cc)', text: 'white' }, // 灰色
    { bg: 'linear-gradient(135deg, #9c27b0, #ce93d8)', text: 'white' }, // 紫色
  ];
  
  // 使用客户ID作为种子来选择颜色
  const index = clientId % colors.length;
  return colors[index];
};

// 获取所有客户信息
const fetchClients = async () => {
  try {
    const response = await http.get('/api/clients/');
    clients.value = response.data;
  } catch (error) {
    console.error('获取客户列表失败:', error);
    ElMessage.error('获取客户列表失败');
  }
};

// 获取所有食材信息
const fetchIngredients = async () => {
  try {
    const response = await http.get('/ingredients/');
    availableIngredients.value = response.data;
  } catch (error) {
    console.error('获取食材信息失败:', error);
    ElMessage.error('获取食材信息失败');
  }
};

// 电话号码验证
const phoneRegex = /^1[3-9]\d{9}$/;
const isValidPhone = (phone) => {
  return phoneRegex.test(phone);
};

// 验证电话号码并提示
const validatePhone = (contact) => {
  if (contact.phone && !isValidPhone(contact.phone)) {
    ElMessage.warning('请输入正确的手机号码格式');
  }
};

// 过滤后的客户列表
const filteredClients = computed(() => {
  return clients.value.filter(client => {
    const searchText = searchQuery.value.toLowerCase();
    const nameMatch = (client.last_name + client.first_name)
      .toLowerCase()
      .includes(searchText);
    
    const idMatch = String(client.client_id).includes(searchText);
    
    const levelMatch = !selectedLevel.value || client.care_level === selectedLevel.value;
    
    return (nameMatch || idMatch) && levelMatch;
  });
});

// 过滤后的食材列表
const filteredIngredients = computed(() => {
  if (!ingredientSearch.value) {
    return availableIngredients.value;
  }
  return availableIngredients.value.filter(ingredient => 
    ingredient.ingredient_name.toLowerCase().includes(ingredientSearch.value.toLowerCase())
  );
});

// 检查食材是否在忌口列表中
const isIngredientInAvoids = (ingredientName) => {
  if (!editedInfo.value.dietary_preference?.忌口) return false;
  return editedInfo.value.dietary_preference.忌口.includes(ingredientName);
};

// 检查食材是否在爱吃列表中
const isIngredientInLoves = (ingredientName) => {
  if (!editedInfo.value.dietary_preference?.爱吃) return false;
  return editedInfo.value.dietary_preference.爱吃.includes(ingredientName);
};

// 切换编辑模式
const toggleEdit = async (client) => {
  if (isEditing.value && editingClientId.value === client.client_id) {
    // 验证所有联系人电话
    const hasInvalidPhone = editedInfo.value.emergency_contact?.some(
      contact => contact.phone && !isValidPhone(contact.phone)
    );
    
    if (hasInvalidPhone) {
      ElMessage.error('请确保所有紧急联系人的电话号码格式正确');
      return;
    }
    
    // 保存更改
    try {
      await http.patch(`/clients/update/${client.client_id}/`, editedInfo.value);
      
      // 更新本地数据
      const index = clients.value.findIndex(c => c.client_id === client.client_id);
      if (index !== -1) {
        clients.value[index] = { ...editedInfo.value, client_id: client.client_id };
      }
      
      ElMessage.success('保存成功');
      isEditing.value = false;
      editingClientId.value = null;
    } catch (error) {
      console.error('保存失败:', error);
      ElMessage.error('保存失败');
    }
  } else {
    // 进入编辑模式
    editedInfo.value = JSON.parse(JSON.stringify(client));
    // 确保饮食偏好对象存在且有正确的结构
    if (!editedInfo.value.dietary_preference) {
      editedInfo.value.dietary_preference = { 忌口: [], 爱吃: [] };
    } else {
      // 确保每个类型都是数组
      if (!Array.isArray(editedInfo.value.dietary_preference.忌口)) {
        editedInfo.value.dietary_preference.忌口 = editedInfo.value.dietary_preference.忌口 
          ? [editedInfo.value.dietary_preference.忌口] 
          : [];
      }
      if (!Array.isArray(editedInfo.value.dietary_preference.爱吃)) {
        editedInfo.value.dietary_preference.爱吃 = editedInfo.value.dietary_preference.爱吃
          ? [editedInfo.value.dietary_preference.爱吃]
          : [];
      }
    }
    
    // 确保婚姻状况和收入范围字段存在
    if (!editedInfo.value.marital) {
      editedInfo.value.marital = '未婚';
    }
    if (!editedInfo.value.income_range) {
      editedInfo.value.income_range = '3000-6000元/月';
    }
    
    // 确保紧急联系人为数组
    if (editedInfo.value.emergency_contact === null || editedInfo.value.emergency_contact === undefined) {
      editedInfo.value.emergency_contact = [];
    }
    
    if (availableIngredients.value.length === 0) {
      await fetchIngredients();
    }
    isEditing.value = true;
    editingClientId.value = client.client_id;
    // 重置食材搜索框
    ingredientSearch.value = '';
  }
};

// 获取饮食偏好
const getDietaryPreference = (client, editedInfo, type) => {
  if (isEditing.value && editingClientId.value === client.client_id) {
    return editedInfo.dietary_preference?.[type] || [];
  }
  return Array.isArray(client.dietary_preference?.[type]) 
    ? client.dietary_preference[type] 
    : (client.dietary_preference?.[type] ? [client.dietary_preference[type]] : []);
};

// 获取紧急联系人
const getEmergencyContacts = (client, editedInfo) => {
  if (isEditing.value && editingClientId.value === client.client_id) {
    return editedInfo.emergency_contact || [];
  }
  return client.emergency_contact || [];
};

// 添加饮食偏好
const addPreference = (type, ingredient) => {
  if (!editedInfo.value.dietary_preference) {
    editedInfo.value.dietary_preference = { 忌口: [], 爱吃: [] };
  }
  if (!editedInfo.value.dietary_preference[type]) {
    editedInfo.value.dietary_preference[type] = [];
  }

  // 检查冲突
  if (type === '忌口' && isIngredientInLoves(ingredient)) {
    ElMessage.error(`食材"${ingredient}"已在爱吃列表中，不能同时添加到忌口`);
    return;
  } else if (type === '爱吃' && isIngredientInAvoids(ingredient)) {
    ElMessage.error(`食材"${ingredient}"已在忌口列表中，不能同时添加到爱吃`);
    return;
  }

  if (!editedInfo.value.dietary_preference[type].includes(ingredient)) {
    editedInfo.value.dietary_preference[type].push(ingredient);
  }
};

// 移除饮食偏好
const removePreference = (type, item) => {
  if (editedInfo.value.dietary_preference?.[type]) {
    const index = editedInfo.value.dietary_preference[type].indexOf(item);
    if (index > -1) {
      editedInfo.value.dietary_preference[type].splice(index, 1);
    }
  }
};

// 添加新的紧急联系人
const addNewContact = () => {
  // 确保紧急联系人数组存在
  if (!editedInfo.value.emergency_contact) {
    editedInfo.value.emergency_contact = [];
  }
  editedInfo.value.emergency_contact.push({
    relative: '',
    phone: ''
  });
};

// 移除紧急联系人
const removeContact = (index) => {
  editedInfo.value.emergency_contact.splice(index, 1);
};

// 获取护理等级标签类型
const getCareTagType = (level) => {
  switch(level) {
    case 1: return 'info';
    case 2: return 'success';
    case 3: return 'warning';
    case 4: return 'danger';
    case 5: return 'danger';
    default: return 'info';
  }
};

onMounted(() => {
  fetchClients();
});
</script>

<style scoped>
.clients-list {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-container {
  padding: var(--spacing-large);
  padding-bottom: 0;
  flex-shrink: 0;
}

.filter-section {
  background: var(--white);
  border-radius: var(--border-radius);
  padding: var(--spacing-large);
  box-shadow: var(--box-shadow-light);
  margin-bottom: var(--spacing-medium);
  transition: all 0.3s ease;
}

.filter-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
}

.level-filter {
  width: 150px;
}

@media (max-width: 768px) {
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input,
  .level-filter {
    width: 100%;
  }
}

.clients-content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--spacing-large);
  padding-bottom: var(--spacing-large);
}

.clients-content {
  padding-bottom: 50px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .clients-content {
    grid-template-columns: 1fr;
  }
}

.client-card {
  margin-bottom: 0;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  background-color: #fff;
  height: fit-content;
}

.client-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.client-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 0;
}

.client-basic-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  flex: 1;
  margin-right: 16px;
}

.name-id-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.client-name {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

.gender-tag {
  font-size: 11px;
  padding: 0 6px;
  height: 20px;
  line-height: 18px;
  margin: 0 4px;
  font-weight: normal;
  flex-shrink: 0;
}

.client-id {
  color: #909399;
  font-size: 13px;
  flex-shrink: 0;
  white-space: nowrap;
}

.care-level {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  white-space: nowrap;
}

.care-label {
  color: #606266;
  font-size: 14px;
}

.care-tag {
  font-weight: 500;
}

.client-details {
  padding: 24px;
  background-color: #fff;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05) inset;
  overflow: visible !important;
  animation: fadeIn 0.3s ease-out;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 16px;
}

.profile-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.details-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow: visible !important;
}

.details-section {
  background-color: #fff;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  transition: all 0.3s ease;
}

.details-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 15px;
  color: #303133;
  font-weight: 600;
  background-color: #f5f7fa;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.care-info-box {
  padding: 16px;
  min-height: 60px;
  background-color: #fafafa;
  border-radius: 0 0 12px 12px;
}

.care-text {
  color: #606266;
  line-height: 1.8;
  white-space: pre-line;
  font-size: 15px;
  padding: 8px;
}

.empty-text {
  color: #909399;
  font-style: italic;
  font-size: 14px;
}

.dietary-preferences {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 12px;
}

.dietary-tag {
  margin-bottom: 5px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 16px;
  padding: 0 12px;
}

.add-button {
  margin-left: 8px;
  transition: all 0.3s ease;
}

.add-button:hover {
  transform: rotate(90deg);
}

.add-contact {
  margin-top: 16px;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
}

.custom-table {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table--border) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #606266;
  padding: 12px 0;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  background-color: #f5f7fa;
  padding: 12px 16px;
}

:deep(.el-descriptions__content) {
  padding: 12px 16px;
  color: #303133;
  line-height: 1.6;
}

:deep(.el-descriptions) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-input) {
  width: 100%;
}

:deep(.el-date-picker) {
  width: 100%;
}

.is-error input {
  border-color: #f56c6c;
}

/* 食材搜索框样式 */
.ingredient-search {
  margin: 8px;
  width: calc(100% - 16px);
}

:deep(.ingredient-dropdown) {
  min-width: 200px;
}

:deep(.el-dropdown-menu__item.is-disabled) {
  color: #c0c4cc;
  cursor: not-allowed;
  background-color: #f5f7fa;
}

:deep(.el-scrollbar__wrap) {
  max-height: inherit;
}

:deep(.el-dropdown-menu__item) {
  padding: 8px 20px;
  line-height: 1.5;
}

/* 强制禁用所有内部滚动 */
:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__wrap),
:deep(.el-collapse-item__content) {
  overflow: visible !important;
}

/* 确保紧急联系人为空时显示提示 */
.no-data-text {
  color: #909399;
  font-style: italic;
  padding: 20px 0;
  text-align: center;
  font-size: 14px;
  width: 100%;
  display: block;
}

:deep(.el-table__empty-text) {
  display: block !important;
}

:deep(.el-table__empty-block) {
  min-height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  padding: 12px 20px;
  transition: all 0.3s;
  border-radius: 12px 12px 0 0;
  height: auto;
  line-height: 1.5;
  display: flex;
  align-items: center;
}

:deep(.el-collapse-item__header:hover) {
  background-color: #ecf5ff;
}

:deep(.el-collapse-item.is-active .el-collapse-item__header) {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

:deep(.el-collapse-item__arrow) {
  margin: 0 0 0 8px;
  font-size: 16px;
  color: #606266;
}

:deep(.el-collapse-item__header) .client-item {
  flex: 1;
  padding: 4px 0;
}

/* 确保下拉菜单正确定位 */
:deep(.el-dropdown-menu) {
  max-height: 300px;
  overflow-y: auto;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__wrapper) {
  max-width: 100%;
}

/* 添加动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.el-collapse-item__content) {
  padding: 0;
}

/* 修改按钮文字居中 */
:deep(.el-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

:deep(.el-button .el-icon) {
  margin: 0;
}

:deep(.profile-header .el-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 8px 16px;
  line-height: 1;
}

:deep(.profile-header .el-button .el-icon) {
  margin: 0;
  vertical-align: middle;
}

:deep(.profile-header .el-button .el-icon + span) {
  margin-left: 4px;
  vertical-align: middle;
}

.edit-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.edit-button .el-icon {
  margin: 0;
  font-size: 16px;
}

.edit-button span {
  line-height: 1;
}
</style> 