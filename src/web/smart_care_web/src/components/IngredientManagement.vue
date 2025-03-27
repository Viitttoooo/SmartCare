<template>
  <div class="ingredient-management">
    <!-- 搜索栏 -->
    <div class="filter-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索食材名称"
        clearable
        class="filter-item"
      />
      <el-button type="primary" class="add-button" @click="createIngredient">
        新增食材
      </el-button>
    </div>

    <!-- 食材列表 -->
    <div class="ingredient-list">
      <el-table :data="filteredIngredients" style="width: 100%" v-loading="loading">
        <el-table-column label="食材名称" prop="ingredient_name" />
        <el-table-column label="操作" width="250" align="center">
          <template #default="{ row }">
            <div class="button-group">
              <el-button type="primary" size="small" @click="viewDetail(row)">
                详情
              </el-button>
              <el-button type="primary" size="small" @click="editIngredient(row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteIngredient(row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentIngredient?.ingredient_name"
      width="50%"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="食材ID">
          {{ currentIngredient?.ingredient_id }}
        </el-descriptions-item>
        <el-descriptions-item label="数量">
          {{ currentIngredient?.ingredient_amount }}{{ currentIngredient?.unit }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ currentIngredient?.ingredient_description }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="nutrition-info">
        <h3>营养成分</h3>
        <el-table :data="nutritionList" border>
          <el-table-column label="营养素" prop="name" />
          <el-table-column label="数量" prop="amount" />
          <el-table-column label="单位" prop="unit" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑食材' : '新增食材'"
      width="50%"
    >
      <el-form 
        :model="ingredientForm" 
        :rules="rules"
        ref="formRef"
        label-width="120px"
      >
        <div class="form-section basic-info">
          <h3 class="section-title">基本信息</h3>
          <el-form-item label="食材名称" prop="ingredient_name">
            <el-input v-model="ingredientForm.ingredient_name" />
          </el-form-item>
          <el-form-item label="描述" prop="ingredient_description">
            <el-input
              v-model="ingredientForm.ingredient_description"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          <el-form-item label="数量" prop="ingredient_amount">
            <div class="amount-input-group">
              <el-input-number v-model="ingredientForm.ingredient_amount" :min="0" />
              <span class="unit-text">{{ ingredientForm.unit }}</span>
            </div>
          </el-form-item>
        </div>
        
        <div class="form-section nutrition-section">
          <h3 class="section-title">营养成分</h3>
          <div class="nutrition-grid">
            <div v-for="(item, key) in ingredientForm.nutrition" :key="key" class="nutrition-item">
              <span class="nutrition-label">{{ key }}</span>
              <div class="nutrition-value">
                <el-input-number 
                  v-model="item.数量" 
                  :min="0" 
                  :precision="1"
                  controls-position="right"
                />
                <span class="unit-text">{{ key === '热量' ? 'kcal' : 'g' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="saveIngredient">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除食材"
      width="30%"
    >
      <span>确定要删除这个食材吗？</span>
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
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import http from '../utils/axios';

// 数据相关
const loading = ref(false);
const ingredients = ref([]);
const searchQuery = ref('');
const detailVisible = ref(false);
const formVisible = ref(false);
const deleteDialogVisible = ref(false);
const currentIngredient = ref(null);
const isEdit = ref(false);

// 表单数据
const ingredientForm = ref({
  ingredient_name: '',
  ingredient_description: '',
  ingredient_amount: 1,
  unit: '克',
  nutrition: {
    '热量': { 单位: 'kcal', 数量: 0 },
    '脂肪': { 单位: 'g', 数量: 0 },
    '蛋白质': { 单位: 'g', 数量: 0 },
    '碳水化合物': { 单位: 'g', 数量: 0 }
  }
});

// 表单引用
const formRef = ref(null);

// 表单验证规则
const rules = {
  ingredient_name: [
    { required: true, message: '请输入食材名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  ingredient_description: [
    { required: true, message: '请输入食材描述', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  ingredient_amount: [
    { required: true, message: '请输入食材数量', trigger: 'blur' }
  ]
};

// 计算营养成分列表
const nutritionList = computed(() => {
  if (!currentIngredient.value) return [];
  return Object.entries(currentIngredient.value.nutrition).map(([name, info]) => ({
    name,
    amount: info.数量,
    unit: info.单位
  }));
});

// 过滤和排序食材列表
const filteredIngredients = computed(() => {
  let result = ingredients.value;
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(item => 
      item.ingredient_name.toLowerCase().includes(query)
    );
  }
  return result.sort((a, b) => 
    a.ingredient_name.localeCompare(b.ingredient_name, 'zh-CN')
  );
});

// 获取食材列表
const fetchIngredients = async () => {
  loading.value = true;
  try {
    const response = await http.get('/api/ingredients/');
    ingredients.value = response.data;
  } catch (error) {
    console.error('获取食材列表失败:', error);
    ElMessage.error('获取食材列表失败');
  } finally {
    loading.value = false;
  }
};

// 查看详情
const viewDetail = (ingredient) => {
  currentIngredient.value = ingredient;
  detailVisible.value = true;
};

// 创建食材
const createIngredient = () => {
  isEdit.value = false;
  ingredientForm.value = {
    ingredient_name: '',
    ingredient_description: '',
    ingredient_amount: 1,
    unit: '克',
    nutrition: {
      '热量': { 单位: 'kcal', 数量: 0 },
      '脂肪': { 单位: 'g', 数量: 0 },
      '蛋白质': { 单位: 'g', 数量: 0 },
      '碳水化合物': { 单位: 'g', 数量: 0 }
    }
  };
  formVisible.value = true;
};

// 编辑食材
const editIngredient = (ingredient) => {
  isEdit.value = true;
  const ingredientCopy = JSON.parse(JSON.stringify(ingredient));
  ingredientCopy.unit = '克'; // 强制设置为克
  
  // 确保营养成分单位固定
  if (ingredientCopy.nutrition) {
    Object.keys(ingredientCopy.nutrition).forEach(key => {
      ingredientCopy.nutrition[key].单位 = key === '热量' ? 'kcal' : 'g';
    });
  }
  
  ingredientForm.value = ingredientCopy;
  formVisible.value = true;
};

// 保存食材
const saveIngredient = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    // 确保营养成分单位固定
    Object.keys(ingredientForm.value.nutrition).forEach(key => {
      ingredientForm.value.nutrition[key].单位 = key === '热量' ? 'kcal' : 'g';
    });
    
    const response = await http[isEdit.value ? 'patch' : 'post'](
      `/api/ingredients/${isEdit.value ? 'update' : 'create'}/`,
      ingredientForm.value
    );

    if (response.status === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      formVisible.value = false;
      fetchIngredients();
    }
  } catch (error) {
    if (error.name === 'ValidationError') {
      ElMessage.error('请填写所有必填项');
    } else {
      console.error(isEdit.value ? '更新失败:' : '创建失败:', error);
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败');
    }
  }
};

// 删除食材
const deleteIngredient = (ingredient) => {
  currentIngredient.value = ingredient;
  deleteDialogVisible.value = true;
};

// 确认删除
const confirmDelete = async () => {
  try {
    const response = await http.delete(
      `/api/ingredients/delete/${currentIngredient.value.ingredient_id}/`
    );
    if (response.status === 200) {
      ElMessage.success('删除成功');
      deleteDialogVisible.value = false;
      fetchIngredients();
    }
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchIngredients();
});
</script>

<style scoped>
.ingredient-management {
  padding: 20px;
}

.filter-section {
  background: var(--white);
  border-radius: var(--border-radius);
  padding: var(--spacing-large);
  margin-bottom: var(--spacing-large);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--box-shadow-light);
}

.filter-item {
  flex: 1;
  max-width: 300px;
  margin-right: var(--spacing-medium);
}

.add-button {
  white-space: nowrap;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    max-width: none;
    margin-right: 0;
    margin-bottom: var(--spacing-medium);
  }
}

.nutrition-info {
  margin-top: 20px;
}

.nutrition-info h3 {
  margin-bottom: 16px;
}

/* 表单部分样式 */
.form-section {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 8px;
  background-color: #f7f8fa;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  color: var(--text-primary, #303133);
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.nutrition-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nutrition-label {
  min-width: 80px;
  font-weight: 500;
}

.nutrition-value {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.nutrition-value .el-input-number {
  width: 100%;
}

.amount-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit-text {
  color: var(--text-regular);
  font-size: 14px;
  padding-left: 4px;
}

/* 确保对话框内表单有足够的空间 */
:deep(.el-dialog__body) {
  padding: 20px 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
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