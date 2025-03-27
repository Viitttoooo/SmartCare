<template>
  <div class="recipe-management">
    <!-- 搜索和筛选区域 -->
    <div class="filter-section">
      <div class="filters-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索菜品名称"
          clearable
          class="filter-item"
        />
        <el-select
          v-model="includeIngredients"
          multiple
          collapse-tags
          placeholder="包含食材"
          clearable
          class="filter-item"
        >
          <el-option
            v-for="item in ingredients"
            :key="item.ingredient_id"
            :label="item.ingredient_name"
            :value="item.ingredient_name"
          />
        </el-select>
        <el-select
          v-model="excludeIngredients"
          multiple
          collapse-tags
          placeholder="不包含食材"
          clearable
          class="filter-item"
        >
          <el-option
            v-for="item in ingredients"
            :key="item.ingredient_id"
            :label="item.ingredient_name"
            :value="item.ingredient_name"
          />
        </el-select>
      </div>
      <el-button type="primary" class="add-button" @click="createRecipe">
        新增菜品
      </el-button>
    </div>

    <!-- 食谱列表 -->
    <div class="recipe-list">
      <el-table :data="filteredRecipes" style="width: 100%" v-loading="loading">
        <el-table-column label="菜品名称" prop="recipe_name" />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <div class="button-group">
              <el-button type="primary" size="small" @click="viewDetail(row)">
                详情
              </el-button>
              <el-button type="danger" size="small" @click="deleteRecipe(row)">
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
      :title="currentRecipe?.recipe_name"
      width="50%"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="菜品ID">
          {{ currentRecipe?.recipe_id }}
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

      <div class="ingredients-info">
        <h3>食材清单</h3>
        <el-table :data="ingredientsList" border>
          <el-table-column label="食材名称" prop="name" />
          <el-table-column label="用量" prop="quantity" />
        </el-table>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="startEdit">
            编辑
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑菜品' : '新增菜品'"
      width="50%"
    >
      <el-form 
        :model="recipeForm" 
        :rules="rules"
        ref="formRef"
        label-width="120px"
      >
        <el-form-item label="菜品名称" prop="recipe_name">
          <el-input v-model="recipeForm.recipe_name" />
        </el-form-item>
        <el-form-item label="食材">
          <div v-for="(item, index) in recipeForm.ingredients" :key="index" class="ingredient-item">
            <el-select 
              v-model="item.ingredient_name" 
              placeholder="选择食材"
              style="width: 200px"
              @change="handleIngredientChange(index)"
              filterable
            >
              <el-option
                v-for="ingredient in ingredients"
                :key="ingredient.ingredient_id"
                :label="ingredient.ingredient_name"
                :value="ingredient.ingredient_name"
              />
            </el-select>
            <el-input 
              v-model="item.quantity" 
              style="width: 120px"
              placeholder="用量"
              type="number"
              min="0"
            />
            <span style="margin-left: 4px">克</span>
            <el-button type="danger" circle @click="removeIngredient(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" @click="addIngredient">
            添加食材
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRecipe">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除菜品"
      width="30%"
    >
      <span>确定要删除这个菜品吗？</span>
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
import { Delete } from '@element-plus/icons-vue';
import http from '../utils/axios';

// 数据相关
const loading = ref(false);
const recipes = ref([]);
const ingredients = ref([]);
const searchQuery = ref('');
const includeIngredients = ref([]);
const excludeIngredients = ref([]);
const detailVisible = ref(false);
const formVisible = ref(false);
const deleteDialogVisible = ref(false);
const currentRecipe = ref(null);
const isEdit = ref(false);

// 表单数据
const recipeForm = ref({
  recipe_name: '',
  ingredients: []
});

// 表单引用
const formRef = ref(null);

// 表单验证规则
const rules = {
  recipe_name: [
    { required: true, message: '请输入菜品名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
};

// 计算营养成分列表
const nutritionList = computed(() => {
  if (!currentRecipe.value?.nutrition_info) return [];
  return Object.entries(currentRecipe.value.nutrition_info).map(([name, info]) => ({
    name,
    amount: info.数量.toFixed(2),
    unit: info.单位
  }));
});

// 计算食材列表
const ingredientsList = computed(() => {
  if (!currentRecipe.value?.ingredients) return [];
  return currentRecipe.value.ingredients.map(item => ({
    name: item.ingredient.ingredient_name,
    quantity: `${Math.floor(item.quantity * item.ingredient.ingredient_amount)}克`
  }));
});

// 过滤食谱列表
const filteredRecipes = computed(() => {
  let result = recipes.value;
  
  // 按名称搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(item => 
      item.recipe_name.toLowerCase().includes(query)
    );
  }

  // 包含食材筛选
  if (includeIngredients.value.length > 0) {
    result = result.filter(recipe => 
      includeIngredients.value.every(ingredient =>
        recipe.ingredients.some(item => 
          item.ingredient.ingredient_name === ingredient
        )
      )
    );
  }

  // 不包含食材筛选
  if (excludeIngredients.value.length > 0) {
    result = result.filter(recipe => 
      excludeIngredients.value.every(ingredient =>
        !recipe.ingredients.some(item => 
          item.ingredient.ingredient_name === ingredient
        )
      )
    );
  }

  return result.sort((a, b) => 
    a.recipe_name.localeCompare(b.recipe_name, 'zh-CN')
  );
});

// 获取食谱列表
const fetchRecipes = async () => {
  loading.value = true;
  try {
    const response = await http.get('/api/recipes/');
    recipes.value = response.data;
  } catch (error) {
    console.error('获取食谱列表失败:', error);
    ElMessage.error('获取食谱列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取食材列表
const fetchIngredients = async () => {
  try {
    const response = await http.get('/api/ingredients/');
    ingredients.value = response.data;
  } catch (error) {
    console.error('获取食材列表失败:', error);
    ElMessage.error('获取食材列表失败');
  }
};

// 查看详情
const viewDetail = (recipe) => {
  currentRecipe.value = recipe;
  detailVisible.value = true;
};

// 开始编辑
const startEdit = () => {
  isEdit.value = true;
  recipeForm.value = {
    recipe_id: currentRecipe.value.recipe_id,
    recipe_name: currentRecipe.value.recipe_name,
    ingredients: currentRecipe.value.ingredients.map(item => ({
      ingredient_name: item.ingredient.ingredient_name,
      quantity: Math.floor(item.quantity * item.ingredient.ingredient_amount),
      unit: '克'
    }))
  };
  detailVisible.value = false;
  formVisible.value = true;
};

// 创建食谱
const createRecipe = () => {
  isEdit.value = false;
  recipeForm.value = {
    recipe_name: '',
    ingredients: []
  };
  formVisible.value = true;
};

// 添加食材
const addIngredient = () => {
  recipeForm.value.ingredients.push({
    ingredient_name: '',
    quantity: 0,
    unit: '克'
  });
};

// 移除食材
const removeIngredient = (index) => {
  recipeForm.value.ingredients.splice(index, 1);
};

// 处理食材选择变化
const handleIngredientChange = (index) => {
  const selectedIngredient = ingredients.value.find(
    item => item.ingredient_name === recipeForm.value.ingredients[index].ingredient_name
  );
  if (selectedIngredient) {
    recipeForm.value.ingredients[index].unit = '克';
  }
};

// 保存食谱
const saveRecipe = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    // 创建一个新的对象用于发送请求
    const requestData = {
      ...recipeForm.value,
      ingredients: recipeForm.value.ingredients.map(item => ({
        ...item,
        quantity: parseInt(item.quantity)
      }))
    };

    const response = await http[isEdit.value ? 'patch' : 'post'](
      `/api/recipes/${isEdit.value ? 'update' : 'create'}/`,
      requestData
    );

    if (response.status === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      formVisible.value = false;
      fetchRecipes();
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

// 删除食谱
const deleteRecipe = (recipe) => {
  currentRecipe.value = recipe;
  deleteDialogVisible.value = true;
};

// 确认删除
const confirmDelete = async () => {
  try {
    const response = await http.delete(
      `/api/recipes/delete/${currentRecipe.value.recipe_id}/`
    );
    if (response.status === 200) {
      ElMessage.success('删除成功');
      deleteDialogVisible.value = false;
      fetchRecipes();
    }
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchRecipes();
  fetchIngredients();
});
</script>

<style scoped>
.recipe-management {
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

.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-medium);
  flex: 1;
}

.filter-item {
  min-width: 180px;
  max-width: 220px;
}

.add-button {
  margin-left: var(--spacing-medium);
  white-space: nowrap;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters-container {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-item {
    width: 100%;
    max-width: none;
  }
  
  .add-button {
    margin-left: 0;
    margin-top: var(--spacing-medium);
    width: 100%;
  }
}

.ingredient-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.nutrition-info,
.ingredients-info {
  margin-top: 20px;
}

.nutrition-info h3,
.ingredients-info h3 {
  margin-bottom: 16px;
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