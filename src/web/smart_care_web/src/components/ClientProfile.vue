<template>
  <div class="client-profile">
    <div class="profile-header">
      <h2>客户档案</h2>
      <el-button type="primary" @click="toggleEdit">{{ isEditing ? '保存' : '修改信息' }}</el-button>
    </div>
    <div class="profile-content">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓">
          <template v-if="isEditing">
            <el-input v-model="editedInfo.last_name" />
          </template>
          <template v-else>{{ clientInfo.last_name }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="名">
          <template v-if="isEditing">
            <el-input v-model="editedInfo.first_name" />
          </template>
          <template v-else>{{ clientInfo.first_name }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          <template v-if="isEditing">
            <el-select v-model="editedInfo.gender">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </template>
          <template v-else>{{ clientInfo.gender }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="出生日期">
          <template v-if="isEditing">
            <el-date-picker 
              v-model="editedInfo.birth_date" 
              type="date" 
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </template>
          <template v-else>{{ clientInfo.birth_date }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="护理等级">
          <template v-if="isEditing">
            {{ editedInfo.care_level }} 级
          </template>
          <template v-else>{{ clientInfo.care_level }} 级</template>
        </el-descriptions-item>
        <el-descriptions-item label="婚姻状况">
          <template v-if="isEditing">
            <el-select v-model="editedInfo.marital">
              <el-option label="已婚" value="已婚" />
              <el-option label="未婚" value="未婚" />
              <el-option label="离婚" value="离婚" />
              <el-option label="丧偶" value="丧偶" />
              <el-option label="分居" value="分居" />
            </el-select>
          </template>
          <template v-else>{{ clientInfo.marital || '未填写' }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="收入范围">
          <template v-if="isEditing">
            <el-select v-model="editedInfo.income_range">
              <el-option label="小于3000元/月" value="小于3000元/月" />
              <el-option label="3000-6000元/月" value="3000-6000元/月" />
              <el-option label="大于6000元/月" value="大于6000元/月" />
            </el-select>
          </template>
          <template v-else>{{ clientInfo.income_range || '未填写' }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="护理需求">
          <template v-if="isEditing">
            <el-input v-model="editedInfo.care_demand" type="textarea" />
          </template>
          <template v-else>{{ clientInfo.care_demand }}</template>
        </el-descriptions-item>
        <el-descriptions-item label="病史" :span="2">
          <template v-if="isEditing">
            <el-input v-model="editedInfo.medical_history" type="textarea" />
          </template>
          <template v-else>{{ clientInfo.medical_history }}</template>
        </el-descriptions-item>
      </el-descriptions>

      <h3 class="section-title">饮食偏好</h3>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="忌口">
          <div class="dietary-preferences">
            <el-tag 
              v-for="item in editedInfo.dietary_preference?.忌口 || []" 
              :key="item"
              class="dietary-tag"
              :closable="isEditing"
              @close="removePreference('忌口', item)"
            >
              {{ item }}
            </el-tag>
            <el-dropdown 
              v-if="isEditing" 
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
              v-for="item in editedInfo.dietary_preference?.爱吃 || []" 
              :key="item"
              type="success"
              class="dietary-tag"
              :closable="isEditing"
              @close="removePreference('爱吃', item)"
            >
              {{ item }}
            </el-tag>
            <el-dropdown 
              v-if="isEditing" 
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

      <h3 class="section-title">紧急联系人</h3>
      <el-table 
        :data="editedInfo.emergency_contact" 
        border 
        style="width: 100%; min-height: 100px"
        :show-header="editedInfo.emergency_contact && editedInfo.emergency_contact.length > 0"
        class="custom-table"
      >
        <el-table-column prop="relative" label="关系">
          <template #default="scope">
            <template v-if="isEditing">
              <el-input v-model="scope.row.relative" />
            </template>
            <template v-else>{{ scope.row.relative }}</template>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话">
          <template #default="scope">
            <template v-if="isEditing">
              <el-input 
                v-model="scope.row.phone"
                :class="{ 'is-error': !isValidPhone(scope.row.phone) }"
                @blur="validatePhone(scope.row)"
              />
            </template>
            <template v-else>{{ scope.row.phone }}</template>
          </template>
        </el-table-column>
        <el-table-column v-if="isEditing" width="80">
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
      <div v-if="isEditing" class="add-contact">
        <el-button type="primary" circle @click="addNewContact">
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus, Delete } from '@element-plus/icons-vue';
import http from '../utils/axios';

const clientInfo = ref({
  first_name: '',
  last_name: '',
  care_level: 0,
  care_demand: '',
  medical_history: '',
  dietary_preference: {
    忌口: [],
    爱吃: []
  },
  gender: '',
  birth_date: '',
  emergency_contact: [],
  marital: '',
  income_range: ''
});

const isEditing = ref(false);
const editedInfo = ref({...clientInfo.value});
const availableIngredients = ref([]);
const ingredientSearch = ref('');

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

// 获取客户信息
const fetchClientInfo = async () => {
  try {
    // 从本地存储获取用户信息
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const clientId = user.client_id;
    
    if (!clientId) {
      ElMessage.error('未找到客户ID信息');
      return;
    }
    
    const response = await http.get(`/api/clients/${clientId}/`);
    clientInfo.value = response.data;
    editedInfo.value = JSON.parse(JSON.stringify(response.data));
  } catch (error) {
    console.error('获取客户信息失败:', error);
    ElMessage.error('获取客户信息失败');
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

// 切换编辑模式
const toggleEdit = async () => {
  if (isEditing.value) {
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
      // 从本地存储获取用户信息
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const clientId = user.client_id;
      
      if (!clientId) {
        ElMessage.error('未找到客户ID信息');
        return;
      }
      
      await http.patch(`/clients/update/${clientId}/`, editedInfo.value);
      clientInfo.value = JSON.parse(JSON.stringify(editedInfo.value));
      ElMessage.success('保存成功');
      isEditing.value = false;
    } catch (error) {
      console.error('保存失败:', error);
      ElMessage.error('保存失败');
    }
  } else {
    // 进入编辑模式
    editedInfo.value = JSON.parse(JSON.stringify(clientInfo.value));
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
    
    // 重置食材搜索框
    ingredientSearch.value = '';
    isEditing.value = true;
  }
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
  const index = editedInfo.value.dietary_preference[type].indexOf(item);
  if (index > -1) {
    editedInfo.value.dietary_preference[type].splice(index, 1);
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

onMounted(() => {
  fetchClientInfo();
});
</script>

<style scoped>
.client-profile {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 20px;
}

.profile-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.profile-content {
  margin-top: 20px;
}

.section-title {
  margin: 30px 0 15px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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
  height: 18px;
  background-color: #409EFF;
  border-radius: 2px;
}

:deep(.el-descriptions) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-descriptions__header) {
  margin-bottom: 0;
}

:deep(.el-descriptions__title) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  padding: 16px 12px;
  background-color: #f5f7fa;
}

:deep(.el-descriptions__content) {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  padding: 16px 12px;
}

:deep(.el-descriptions__body .el-descriptions__table) {
  border-radius: 8px;
}

:deep(.el-descriptions .el-descriptions__body .el-descriptions__table .el-descriptions__cell) {
  border-color: #ebeef5;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__row:first-child td:first-child, 
       .el-descriptions__body .el-descriptions__table .el-descriptions__row:first-child th:first-child) {
  border-top-left-radius: 8px;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__row:first-child td:last-child, 
       .el-descriptions__body .el-descriptions__table .el-descriptions__row:first-child th:last-child) {
  border-top-right-radius: 8px;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__row:last-child td:first-child, 
       .el-descriptions__body .el-descriptions__table .el-descriptions__row:last-child th:first-child) {
  border-bottom-left-radius: 8px;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__row:last-child td:last-child, 
       .el-descriptions__body .el-descriptions__table .el-descriptions__row:last-child th:last-child) {
  border-bottom-right-radius: 8px;
}

.dietary-preferences {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 5px 0;
}

.dietary-tag {
  margin-bottom: 5px;
  font-size: 13px;
  font-weight: 500;
}

.add-button {
  margin-left: 8px;
}

.add-contact {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.custom-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #606266;
  padding: 15px 0;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table--border) {
  border-radius: 8px;
}

:deep(.el-table--border th:first-child),
:deep(.el-table--border td:first-child) {
  border-left: none;
}

:deep(.el-table--border th:last-child),
:deep(.el-table--border td:last-child) {
  border-right: none;
}

.no-data-text {
  color: #909399;
  font-style: italic;
  padding: 20px 0;
  text-align: center;
  font-size: 14px;
  width: 100%;
  display: block;
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

:deep(.el-input) {
  width: 100%;
}

:deep(.el-date-picker) {
  width: 100%;
}
</style> 