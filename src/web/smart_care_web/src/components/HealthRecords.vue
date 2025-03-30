<template>
  <div class="health-records">
    <!-- 管理员和员工视图：显示客户列表 -->
    <template v-if="isStaff">
      <!-- 客户筛选区域 -->
      <div class="filter-container">
        <div class="filter-section client-filter-section">
          <div class="section-title">客户筛选</div>
          <div class="filter-content">
            <el-input
              v-model="searchQuery"
              placeholder="搜索客户姓名"
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-input
              v-model="clientIdFilter"
              placeholder="客户ID"
              class="client-id-input"
              clearable
            />
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

        <!-- 健康记录筛选区域 -->
        <div class="filter-section record-filter-section">
          <div class="section-title">记录筛选</div>
          <div class="filter-content">
            <el-date-picker
              v-model="dateFilter"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="date-picker"
            />
            <el-input
              v-model="staffNameFilter"
              placeholder="员工姓名"
              clearable
              class="staff-filter"
            />
            <el-input
              v-model="staffIdFilter"
              placeholder="员工ID"
              clearable
              class="staff-filter"
            />
          </div>
        </div>
      </div>

      <!-- 客户列表 -->
      <div class="clients-list">
        <el-collapse v-model="activeNames">
          <el-collapse-item 
            v-for="client in filteredClients" 
            :key="client.client_id"
            :name="client.client_id"
          >
            <template #title>
              <div class="client-item">
                <span class="client-id">ID: {{ client.client_id }}</span>
                <span class="client-name">
                  {{ client.last_name }}{{ client.first_name }}
                </span>
                <span class="gender-tag" v-if="client.gender">
                  <el-tag 
                    :type="client.gender === '男' ? 'info' : 'danger'" 
                    size="small"
                    effect="plain"
                  >
                    {{ client.gender }}
                  </el-tag>
                </span>
                <span class="care-level" v-if="client.care_level">
                  护理等级: {{ client.care_level }}级
                </span>
              </div>
            </template>
            
            <!-- 健康记录列表 -->
            <div class="health-metrics-list">
              <!-- 添加新记录按钮移到最前面 -->
              <div class="add-record-container">
                <el-button
                  type="primary"
                  circle
                  @click="createNewRecord(client.client_id)"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>

              <el-timeline>
                <el-timeline-item
                  v-for="metric in sortedFilteredMetrics(clientMetrics[client.client_id] || [])"
                  :key="metric.metric_id"
                  :timestamp="formatDate(metric.record_date)"
                  placement="top"
                >
                  <el-card>
                    <div class="metric-item">
                      <div class="metric-header">
                        <span>记录ID: {{ metric.metric_id }}</span>
                        <span class="staff-info" @click="selectStaff(metric)">
                          记录员工: {{ metric.staff_last_name }}{{ metric.staff_first_name }}
                          <el-icon><Edit /></el-icon>
                        </span>
                      </div>
                      <div class="metric-assessment">
                        评估结果: {{ metric.assessment }}
                      </div>
                      <div v-if="metric.mets_probability !== undefined" class="metric-mets-risk">
                        代谢综合征风险: 
                        <el-tag 
                          :type="getMetsProbabilityTagType(metric.mets_probability)"
                          size="small"
                        >
                          {{ (metric.mets_probability * 100).toFixed(2) }}%
                        </el-tag>
                      </div>
                      <div class="metric-actions">
                        <el-button 
                          type="primary" 
                          link 
                          @click="viewMetricDetail(metric)"
                        >
                          查看详情
                        </el-button>
                        <el-button 
                          type="warning" 
                          link 
                          @click="editMetric(metric)"
                        >
                          编辑
                        </el-button>
                        <el-button 
                          type="danger" 
                          link 
                          @click="deleteMetric(metric.metric_id)"
                        >
                          删除
                        </el-button>
                      </div>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </template>

    <!-- 客户视图：直接显示健康记录 -->
    <template v-else>
      <!-- 健康记录筛选区域 -->
      <div class="filter-container">
        <div class="filter-section record-filter-section">
          <div class="section-title">记录筛选</div>
          <div class="filter-content">
            <el-date-picker
              v-model="dateFilter"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="date-picker"
            />
            <el-input
              v-model="staffNameFilter"
              placeholder="员工姓名"
              clearable
              class="staff-filter"
            />
          </div>
        </div>
      </div>

      <div class="health-metrics-list">
        <el-timeline>
          <el-timeline-item
            v-for="metric in filteredMetrics"
            :key="metric.metric_id"
            :timestamp="formatDate(metric.record_date)"
            placement="top"
          >
            <el-card>
              <div class="metric-item">
                <div class="metric-header">
                  <span>记录ID: {{ metric.metric_id }}</span>
                  <span>记录员工: {{ metric.staff_last_name }}{{ metric.staff_first_name }}</span>
                </div>
                <div class="metric-assessment">
                  评估结果: {{ metric.assessment }}
                </div>
                <div v-if="metric.mets_probability !== undefined" class="metric-mets-risk">
                  代谢综合征风险: 
                  <el-tag 
                    :type="getMetsProbabilityTagType(metric.mets_probability)"
                    size="small"
                  >
                    {{ (metric.mets_probability * 100).toFixed(2) }}%
                  </el-tag>
                </div>
                <el-button 
                  type="primary" 
                  link 
                  @click="viewMetricDetail(metric)"
                >
                  查看详情
                </el-button>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </template>

    <!-- 健康指标详情对话框 -->
    <el-dialog
      v-model="showMetricDetail"
      title="健康指标详情"
      width="60%"
      :before-close="handleCloseDetail"
    >
      <div v-if="currentMetric" class="metric-detail">
        <div class="detail-header">
          <div>记录时间：{{ formatDate(currentMetric.record_date) }}</div>
          <div>记录员工：{{ currentMetric.staff_last_name }}{{ currentMetric.staff_first_name }}</div>
          <div>评估结果：{{ currentMetric.assessment }}</div>
          <div v-if="currentMetric.mets_probability !== undefined">
            <span>代谢综合征风险：</span>
            <el-tag 
              :type="getMetsProbabilityTagType(currentMetric.mets_probability)"
              size="small"
            >
              {{ (currentMetric.mets_probability * 100).toFixed(2) }}%
            </el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <!-- 智能评估结果 -->
        <div class="smart-assessment">
          <div class="smart-assessment-header">
            <h3>智能评估结果</h3>
            <el-button 
              v-if="isStaff" 
              type="primary" 
              size="small" 
              :loading="generatingAssessment"
              @click="generateSmartAssessment(currentMetric.metric_id)"
            >
              {{ currentMetric.smart_assessment ? '重新生成' : '生成智能评估' }}
            </el-button>
          </div>
          
          <div v-if="currentMetric.smart_assessment" class="markdown-content">
            <div v-html="renderMarkdown(currentMetric.smart_assessment)"></div>
            <div class="disclaimer">
              <el-icon><InfoFilled /></el-icon>
              <span>内容由AI生成，请自行甄别</span>
            </div>
          </div>
          <div v-else class="no-assessment">
            暂无智能评估结果
          </div>
        </div>
        
        <el-divider />
        
        <div class="vital-signs">
          <h3>生命体征</h3>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="身高">
              {{ currentMetric.vital_signs.height.value }} {{ currentMetric.vital_signs.height.unit }}
            </el-descriptions-item>
            <el-descriptions-item label="体重">
              {{ currentMetric.vital_signs.weight.value }} {{ currentMetric.vital_signs.weight.unit }}
            </el-descriptions-item>
            <el-descriptions-item label="BMI">
              {{ currentMetric.vital_signs.bmi.value }} {{ currentMetric.vital_signs.bmi.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.bmi.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="腰围">
              {{ currentMetric.vital_signs.waist_circumference.value }} {{ currentMetric.vital_signs.waist_circumference.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.waist_circumference.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="心率">
              {{ currentMetric.vital_signs.heart_rate.value }} {{ currentMetric.vital_signs.heart_rate.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.heart_rate.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="血压">
              收缩压: {{ currentMetric.vital_signs.blood_pressure.systolic.value }} {{ currentMetric.vital_signs.blood_pressure.systolic.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.blood_pressure.systolic.normal_range }}
              </el-tag>
              <br>
              舒张压: {{ currentMetric.vital_signs.blood_pressure.diastolic.value }} {{ currentMetric.vital_signs.blood_pressure.diastolic.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.blood_pressure.diastolic.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="体温">
              {{ currentMetric.vital_signs.body_temperature.value }} {{ currentMetric.vital_signs.body_temperature.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.body_temperature.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="呼吸频率">
              {{ currentMetric.vital_signs.respiratory_rate.value }} {{ currentMetric.vital_signs.respiratory_rate.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.respiratory_rate.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="血氧饱和度">
              {{ currentMetric.vital_signs.oxygen_saturation.value }} {{ currentMetric.vital_signs.oxygen_saturation.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.oxygen_saturation.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="尿酸">
              {{ currentMetric.vital_signs.uric_acid.value }} {{ currentMetric.vital_signs.uric_acid.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.uric_acid.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="尿蛋白">
              {{ currentMetric.vital_signs.albuminuria.value }} {{ currentMetric.vital_signs.albuminuria.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.albuminuria.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="血糖">
              {{ currentMetric.vital_signs.blood_glucose.value }} {{ currentMetric.vital_signs.blood_glucose.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.blood_glucose.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="甘油三酯">
              {{ currentMetric.vital_signs.triglycerides.value }} {{ currentMetric.vital_signs.triglycerides.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.triglycerides.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="HDL胆固醇">
              {{ currentMetric.vital_signs.hdl_cholesterol.value }} {{ currentMetric.vital_signs.hdl_cholesterol.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.hdl_cholesterol.normal_range }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="尿白蛋白肌酐比">
              {{ currentMetric.vital_signs.urine_albumin_creatinine_ratio.value }} {{ currentMetric.vital_signs.urine_albumin_creatinine_ratio.unit }}
              <el-tag 
                size="small" 
                type="success"
              >
                参考范围: {{ currentMetric.vital_signs.urine_albumin_creatinine_ratio.normal_range }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showMetricDetail = false">返回</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 员工选择对话框 -->
    <el-dialog
      v-model="showStaffSelector"
      title="选择记录员工"
      width="30%"
    >
      <div class="staff-list">
        <el-scrollbar height="300px">
          <el-radio-group v-model="selectedStaffId">
            <el-radio
              v-for="staff in staffList"
              :key="staff.staff_id"
              :label="staff.staff_id"
              class="staff-radio"
            >
              {{ staff.last_name }}{{ staff.first_name }} (ID: {{ staff.staff_id }})
            </el-radio>
          </el-radio-group>
        </el-scrollbar>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showStaffSelector = false">取消</el-button>
          <el-button type="primary" @click="confirmStaffSelection">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑记录对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="isCreating ? '新增健康记录' : '编辑健康记录'"
      width="60%"
    >
      <div class="edit-form" v-if="editingMetric">
        <el-form :model="editingMetric" label-width="120px">
          <el-form-item label="记录时间">
            <el-date-picker
              v-model="editingMetric.record_date"
              type="datetime"
              placeholder="选择日期时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              :default-time="new Date(2000, 0, 1, 0, 0, 0)"
            />
          </el-form-item>
          <el-form-item label="评估结果">
            <el-input
              v-model="editingMetric.assessment"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          <el-form-item label="记录员工">
            <div class="staff-selector" @click="selectStaffForEdit">
              <span v-if="editingMetric.staff_last_name">
                {{ editingMetric.staff_last_name }}{{ editingMetric.staff_first_name }}
              </span>
              <span v-else>点击选择员工</span>
              <el-icon><Edit /></el-icon>
            </div>
          </el-form-item>
          
          <!-- 生命体征表单 -->
          <el-divider>生命体征</el-divider>
          <div class="vital-signs-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="身高">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.height.value"
                      :min="0"
                      :max="300"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.height.unit }}</span>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="体重">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.weight.value"
                      :min="0"
                      :max="500"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.weight.unit }}</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="BMI">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.bmi.value"
                      :min="0"
                      :max="100"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.bmi.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.bmi.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="腰围">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.waist_circumference.value"
                      :min="0"
                      :max="200"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.waist_circumference.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.waist_circumference.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="心率">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.heart_rate.value"
                      :min="0"
                      :max="300"
                      :precision="0"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.heart_rate.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.heart_rate.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="尿酸">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.uric_acid.value"
                      :min="0"
                      :max="20"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.uric_acid.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.uric_acid.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="收缩压">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.blood_pressure.systolic.value"
                      :min="0"
                      :max="300"
                      :precision="0"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.blood_pressure.systolic.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.blood_pressure.systolic.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="舒张压">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.blood_pressure.diastolic.value"
                      :min="0"
                      :max="300"
                      :precision="0"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.blood_pressure.diastolic.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.blood_pressure.diastolic.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="体温">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.body_temperature.value"
                      :min="30"
                      :max="45"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.body_temperature.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.body_temperature.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="呼吸频率">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.respiratory_rate.value"
                      :min="0"
                      :max="100"
                      :precision="0"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.respiratory_rate.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.respiratory_rate.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="血氧饱和度">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.oxygen_saturation.value"
                      :min="0"
                      :max="100"
                      :precision="0"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.oxygen_saturation.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.oxygen_saturation.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="尿蛋白">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.albuminuria.value"
                      :min="0"
                      :max="1000"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.albuminuria.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.albuminuria.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="血糖">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.blood_glucose.value"
                      :min="0"
                      :max="30"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.blood_glucose.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.blood_glucose.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="甘油三酯">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.triglycerides.value"
                      :min="0"
                      :max="10"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.triglycerides.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.triglycerides.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="HDL胆固醇">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.hdl_cholesterol.value"
                      :min="0"
                      :max="5"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.hdl_cholesterol.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.hdl_cholesterol.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="尿白蛋白肌酐比">
                  <div>
                    <el-input-number
                      v-model="editingMetric.vital_signs.urine_albumin_creatinine_ratio.value"
                      :min="0"
                      :max="1000"
                      :precision="1"
                    />
                    <span class="unit">{{ editingMetric.vital_signs.urine_albumin_creatinine_ratio.unit }}</span>
                  </div>
                  <div class="reference-range">
                    参考范围: {{ editingMetric.vital_signs.urine_albumin_creatinine_ratio.normal_range }}
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveMetric">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Edit, Plus, InfoFilled } from '@element-plus/icons-vue';
import http from '../utils/axios';
import { marked } from 'marked';

const isStaff = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role_name === '员工' || user.role_name === '管理员';
});

// 筛选条件
const dateFilter = ref('');
const staffNameFilter = ref('');
const staffIdFilter = ref('');
const clientIdFilter = ref('');

// 客户列表相关
const clients = ref([]);
const searchQuery = ref('');
const selectedLevel = ref('');
const activeNames = ref([]);
const clientMetrics = ref({});
const showClientsList = ref(true);

// 健康指标相关
const metrics = ref([]);
const currentMetric = ref(null);
const showMetricDetail = ref(false);
const generatingAssessment = ref(false);

// 员工相关
const staffList = ref([]);
const selectedStaffId = ref(null);
const showStaffSelector = ref(false);
const currentEditingMetricId = ref(null);
const isCreating = ref(false);
const editingMetric = ref(null);
const showEditDialog = ref(false);

// 筛选后的客户列表
const filteredClients = computed(() => {
  return clients.value.filter(client => {
    const nameMatch = (client.last_name + client.first_name)
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase());
    
    const levelMatch = !selectedLevel.value || client.care_level === selectedLevel.value;
    
    const clientIdMatch = !clientIdFilter.value || 
      String(client.client_id).includes(clientIdFilter.value);
    
    return nameMatch && levelMatch && clientIdMatch;
  });
});

// 客户视图的筛选后的记录
const filteredMetrics = computed(() => {
  return metrics.value
    .filter(metric => {
      const dateMatch = !dateFilter.value || 
        formatDate(metric.record_date).split(' ')[0] === dateFilter.value;
      
      const staffNameMatch = !staffNameFilter.value || 
        (metric.staff_last_name + metric.staff_first_name)
          .toLowerCase()
          .includes(staffNameFilter.value.toLowerCase());
      
      return dateMatch && staffNameMatch;
    })
    .sort((a, b) => new Date(b.record_date) - new Date(a.record_date)); // 按时间降序排序
});

// 格式化日期（用于显示）
const formatDate = (dateString) => {
  const date = new Date(dateString);
  // 转换为北京时间
  const beijingDate = new Date(date.getTime() + (8 * 60 * 60 * 1000));
  return `${beijingDate.getUTCFullYear()}-${String(beijingDate.getUTCMonth() + 1).padStart(2, '0')}-${String(beijingDate.getUTCDate()).padStart(2, '0')} ${String(beijingDate.getUTCHours()).padStart(2, '0')}:${String(beijingDate.getUTCMinutes()).padStart(2, '0')}`;
};

// 转换为UTC时间
const toUTCDate = (dateString) => {
  const date = new Date(dateString);
  // 转换为UTC时间（减去8小时）
  const utcDate = new Date(date.getTime() - (8 * 60 * 60 * 1000));
  return utcDate.toISOString();
};

// 检查数值是否在正常范围内
const isInRange = (value, range) => {
  if (!range) return true;
  const [min, max] = range.split('-').map(Number);
  return value >= min && value <= max;
};

// 获取代谢综合征概率标签类型
const getMetsProbabilityTagType = (probability) => {
  if (probability < 0.1) return 'success';
  if (probability < 0.3) return 'warning';
  return 'danger';
};

// 排序和筛选后的记录
const sortedFilteredMetrics = (metricsList) => {
  return metricsList
    .filter(metric => {
      const dateMatch = !dateFilter.value || 
        formatDate(metric.record_date).split(' ')[0] === dateFilter.value;
      
      const staffNameMatch = !staffNameFilter.value || 
        (metric.staff_last_name + metric.staff_first_name)
          .toLowerCase()
          .includes(staffNameFilter.value.toLowerCase());
      
      const staffIdMatch = !staffIdFilter.value || 
        String(metric.staff) === String(staffIdFilter.value);
      
      return dateMatch && staffNameMatch && staffIdMatch;
    })
    .sort((a, b) => new Date(b.record_date) - new Date(a.record_date));
};

// 获取所有客户信息（仅员工/管理员）
const fetchClients = async () => {
  try {
    const response = await http.get('/api/clients/');
    clients.value = response.data;
  } catch (error) {
    console.error('获取客户列表失败:', error);
    ElMessage.error('获取客户列表失败');
  }
};

// 获取指定客户的健康指标
const fetchClientMetrics = async (clientId) => {
  try {
    const response = await http.get(`/api/metrics/get/${clientId}/`);
    clientMetrics.value[clientId] = response.data;
  } catch (error) {
    console.error(`获取客户${clientId}的健康指标失败:`, error);
    ElMessage.error('获取健康指标失败');
  }
};

// 获取当前客户的健康指标（仅客户）
const fetchSelfMetrics = async () => {
  try {
    // 从本地存储获取用户信息
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const clientId = user.client_id;
    
    if (!clientId) {
      ElMessage.error('未找到客户ID信息');
      return;
    }
    
    const response = await http.get(`/api/metrics/get/${clientId}/`);
    metrics.value = response.data;
  } catch (error) {
    console.error('获取健康指标失败:', error);
    ElMessage.error('获取健康指标失败');
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

// 查看健康指标详情
const viewMetricDetail = (metric) => {
  currentMetric.value = metric;
  showMetricDetail.value = true;
};

// 关闭详情对话框
const handleCloseDetail = () => {
  showMetricDetail.value = false;
  currentMetric.value = null;
};

// 选择员工（用于更新记录员工）
const selectStaff = (metric) => {
  currentEditingMetricId.value = metric.metric_id;
  selectedStaffId.value = metric.staff_id;
  showStaffSelector.value = true;
};

// 为编辑表单选择员工
const selectStaffForEdit = () => {
  showStaffSelector.value = true;
};

// 确认员工选择
const confirmStaffSelection = async () => {
  if (!selectedStaffId.value) {
    ElMessage.warning('请选择员工');
    return;
  }

  const selectedStaff = staffList.value.find(staff => staff.staff_id === selectedStaffId.value);
  if (!selectedStaff) {
    ElMessage.error('未找到选中的员工');
    return;
  }

  if (editingMetric.value) {
    // 更新编辑表单中的员工信息
    editingMetric.value.staff = selectedStaff.staff_id;
    editingMetric.value.staff_first_name = selectedStaff.first_name;
    editingMetric.value.staff_last_name = selectedStaff.last_name;
  } else if (currentEditingMetricId.value) {
    // 直接更新记录的员工
    try {
      const response = await http.patch('/api/metrics/update/staff/', {
        metric_id: currentEditingMetricId.value,
        staff: selectedStaff.staff_id
      });
      
      if (response.status === 200) {
        ElMessage.success('更新成功');
        // 更新本地数据
        const updatedMetric = response.data;
        Object.keys(clientMetrics.value).forEach(clientId => {
          const index = clientMetrics.value[clientId].findIndex(m => m.metric_id === updatedMetric.metric_id);
          if (index !== -1) {
            clientMetrics.value[clientId][index] = updatedMetric;
          }
        });
      }
    } catch (error) {
      console.error('更新员工失败:', error);
      ElMessage.error('更新员工失败');
    }
  }

  showStaffSelector.value = false;
  currentEditingMetricId.value = null;
  selectedStaffId.value = null;
};

// 编辑记录
const editMetric = (metric) => {
  const metricCopy = JSON.parse(JSON.stringify(metric)); // 深拷贝
  // 将 UTC 时间转换为北京时间字符串
  const utcDate = new Date(metricCopy.record_date);
  const beijingDate = new Date(utcDate.getTime() + (8 * 60 * 60 * 1000));
  const formattedDate = `${beijingDate.getUTCFullYear()}-${String(beijingDate.getUTCMonth() + 1).padStart(2, '0')}-${String(beijingDate.getUTCDate()).padStart(2, '0')} ${String(beijingDate.getUTCHours()).padStart(2, '0')}:${String(beijingDate.getUTCMinutes()).padStart(2, '0')}:${String(beijingDate.getUTCSeconds()).padStart(2, '0')}`;
  metricCopy.record_date = formattedDate;
  editingMetric.value = metricCopy;
  isCreating.value = false;
  showEditDialog.value = true;
};

// 创建新记录
const createNewRecord = (clientId) => {
  const currentDate = new Date();
  // 直接使用本地时间的字符串格式
  const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')} ${String(currentDate.getHours()).padStart(2, '0')}:${String(currentDate.getMinutes()).padStart(2, '0')}:${String(currentDate.getSeconds()).padStart(2, '0')}`;
  
  editingMetric.value = {
    client: clientId,
    record_date: formattedDate,
    assessment: '',
    vital_signs: {
      height: { value: null, unit: 'cm' },
      weight: { value: null, unit: 'kg' },
      bmi: { value: null, unit: 'kg/m²', normal_range: '18.5-24.9' },
      heart_rate: { value: null, unit: 'bpm', normal_range: '60-100' },
      blood_pressure: {
        systolic: { value: null, unit: 'mmHg', normal_range: '90-140' },
        diastolic: { value: null, unit: 'mmHg', normal_range: '60-90' }
      },
      body_temperature: { value: null, unit: '°C', normal_range: '36.3-37.2' },
      respiratory_rate: { value: null, unit: 'bpm', normal_range: '12-20' },
      oxygen_saturation: { value: null, unit: '%', normal_range: '95-100' },
      waist_circumference: { value: null, unit: 'cm', normal_range: '<90 (男性), <80 (女性)' },
      uric_acid: { value: null, unit: 'mg/dL', normal_range: '3.4-7.0 (男性), 2.4-6.0 (女性)' },
      albuminuria: { value: null, unit: 'mg/L', normal_range: '<30' },
      blood_glucose: { value: null, unit: 'mmol/L', normal_range: '<5.6 (空腹)' },
      triglycerides: { value: null, unit: 'mmol/L', normal_range: '<1.7' },
      hdl_cholesterol: { value: null, unit: 'mmol/L', normal_range: '>1.0' },
      urine_albumin_creatinine_ratio: { value: null, unit: 'mg/g', normal_range: '<30' }
    }
  };
  isCreating.value = true;
  showEditDialog.value = true;
};

// 保存记录
const saveMetric = async () => {
  try {
    // 将本地时间转换为 UTC 时间（减去8小时）
    const localDate = new Date(editingMetric.value.record_date);
    const utcDate = new Date(localDate.getTime() - (8 * 60 * 60 * 1000));
    const utcString = `${utcDate.getFullYear()}-${String(utcDate.getMonth() + 1).padStart(2, '0')}-${String(utcDate.getDate()).padStart(2, '0')} ${String(utcDate.getHours()).padStart(2, '0')}:${String(utcDate.getMinutes()).padStart(2, '0')}:${String(utcDate.getSeconds()).padStart(2, '0')}`;
    
    const payload = {
      vital_signs: editingMetric.value.vital_signs,
      record_date: utcString,  // 使用 UTC 时间
      assessment: editingMetric.value.assessment,
      staff: editingMetric.value.staff,
      client: editingMetric.value.client
    };

    let response;
    if (isCreating.value) {
      response = await http.post('/api/metrics/create/staff/', payload);
    } else {
      payload.metric_id = editingMetric.value.metric_id;
      response = await http.patch('/api/metrics/update/staff/', payload);
    }

    if (response.status === 200) {
      ElMessage.success(isCreating.value ? '创建成功' : '更新成功');
      
      // 更新本地数据
      const updatedMetric = response.data;
      if (isCreating.value) {
        if (!clientMetrics.value[updatedMetric.client]) {
          clientMetrics.value[updatedMetric.client] = [];
        }
        clientMetrics.value[updatedMetric.client].unshift(updatedMetric);
      } else {
        Object.keys(clientMetrics.value).forEach(clientId => {
          const index = clientMetrics.value[clientId].findIndex(m => m.metric_id === updatedMetric.metric_id);
          if (index !== -1) {
            clientMetrics.value[clientId][index] = updatedMetric;
          }
        });
      }
      
      showEditDialog.value = false;
      editingMetric.value = null;
    }
  } catch (error) {
    console.error(isCreating.value ? '创建失败:' : '更新失败:', error);
    ElMessage.error(isCreating.value ? '创建失败' : '更新失败');
  }
};

// 删除记录
const deleteMetric = async (metricId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条健康记录吗？删除后将无法恢复',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    const response = await http.delete(`/api/metrics/delete/${metricId}/`);
    if (response.status === 200) {
      ElMessage.success('删除成功');
      // 更新本地数据
      Object.keys(clientMetrics.value).forEach(clientId => {
        clientMetrics.value[clientId] = clientMetrics.value[clientId].filter(
          m => m.metric_id !== metricId
        );
      });
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 监听展开的客户变化
watch(activeNames, async (newNames) => {
  if (isStaff.value) {
    for (const clientId of newNames) {
      if (!clientMetrics.value[clientId]) {
        await fetchClientMetrics(clientId);
      }
    }
  }
});

// 将Markdown渲染为HTML
const renderMarkdown = (markdown) => {
  if (!markdown) return '';
  return marked(markdown);
};

// 生成智能评估结果
const generateSmartAssessment = async (metricId) => {
  try {
    generatingAssessment.value = true;
    
    const response = await http.patch(
      `/api/metrics/generate_metrics_assessment/${metricId}/`,
      {}, // 空对象作为请求体
      { 
        timeout: 120000, // 设置2分钟超时
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    if (response.status === 200) {
      // 更新当前指标的智能评估结果
      if (currentMetric.value && currentMetric.value.metric_id === metricId) {
        currentMetric.value.smart_assessment = response.data.smart_assessment;
      }
      
      // 更新本地数据中的智能评估结果
      Object.keys(clientMetrics.value).forEach(clientId => {
        const metricIndex = clientMetrics.value[clientId].findIndex(
          m => m.metric_id === metricId
        );
        if (metricIndex !== -1) {
          clientMetrics.value[clientId][metricIndex].smart_assessment = response.data.smart_assessment;
        }
      });
      
      ElMessage.success('智能评估结果生成成功');
    }
  } catch (error) {
    console.error('生成智能评估结果失败:', error);
    ElMessage.error('生成智能评估结果失败');
  } finally {
    generatingAssessment.value = false;
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  if (isStaff.value) {
    await fetchClients();
    await fetchStaffList();
  } else {
    await fetchSelfMetrics();
  }
});
</script>

<style scoped>
.health-records {
  padding: 24px;
  background-color: #f9fafc;
  min-height: calc(100vh - 48px);
  border-radius: 12px;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.filter-section {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.filter-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.section-title {
  font-size: 16px;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
  font-weight: 500;
  position: relative;
  padding-left: 12px;
  letter-spacing: 0.5px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background-color: var(--el-color-primary);
  border-radius: 6px;
  opacity: 0.8;
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input,
.client-id-input,
.level-filter,
.date-picker,
.staff-filter {
  transition: all 0.3s ease;
}

.search-input:hover,
.client-id-input:hover,
.level-filter:hover,
.date-picker:hover,
.staff-filter:hover {
  transform: translateY(-1px);
}

.search-input {
  width: 220px;
}

.client-id-input {
  width: 140px;
}

.level-filter {
  width: 140px;
}

.date-picker {
  width: 240px;
}

.staff-filter {
  width: 160px;
}

.clients-list {
  margin-top: 24px;
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

.client-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
  width: 100%;
}

.client-id {
  color: var(--el-text-color-secondary);
  width: 80px;
  flex-shrink: 0;
  font-family: var(--el-font-family);
  font-size: 14px;
}

.client-name {
  font-weight: 500;
  width: 120px;
  flex-shrink: 0;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gender-tag {
  margin-right: 12px;
  display: inline-flex;
  align-items: center;
}

.care-level {
  color: var(--el-color-primary);
  font-weight: 500;
  font-size: 12px;
  background-color: rgba(64, 158, 255, 0.08);
  padding: 2px 8px;
  border-radius: 12px;
  white-space: nowrap;
  display: inline-block;
  line-height: 1.4;
}

/* 添加占位空间 */
.client-item::after {
  content: '';
  flex: 1;
}

.health-metrics-list {
  padding: 20px;
  background: var(--el-bg-color);
  border-radius: 12px;
}

.add-record-container {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  padding: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.metric-item {
  padding: 16px;
  transition: all 0.3s ease;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.metric-assessment {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.metric-mets-risk {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.detail-header {
  margin-bottom: 24px;
  line-height: 2;
  color: var(--el-text-color-regular);
}

.vital-signs {
  margin-top: 24px;
}

.vital-signs h3 {
  margin-bottom: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.staff-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-color-primary);
  transition: all 0.3s ease;
  font-size: 14px;
}

.staff-info:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.metric-actions {
  margin-top: 12px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.staff-selector {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.staff-selector:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background-color: rgba(64, 158, 255, 0.05);
}

.edit-form {
  padding: 20px;
}

.vital-signs-form {
  margin-top: 20px;
  background-color: rgba(64, 158, 255, 0.05);
  padding: 20px;
  border-radius: 12px;
}

.reference-range {
  color: var(--el-color-success);
  font-size: 12px;
  margin-top: 4px;
  padding-left: 4px;
  display: block;
  position: relative;
  clear: both;
  width: 100%;
  float: none !important;
  text-align: left !important;
}

.unit {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.staff-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.staff-radio {
  display: block;
  margin-bottom: 8px;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.staff-radio:hover {
  background-color: rgba(64, 158, 255, 0.05);
}

.dialog-footer {
  text-align: right;
  padding-top: 16px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-collapse-item__header) {
  font-size: 15px;
  padding: 12px 16px;
  background-color: rgba(64, 158, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

:deep(.el-collapse-item__header:hover) {
  background-color: rgba(64, 158, 255, 0.1);
}

:deep(.el-collapse-item__content) {
  padding: 20px 10px;
}

:deep(.el-timeline-item__node) {
  background-color: var(--el-color-primary-light-5);
  border-color: var(--el-color-primary-light-3);
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-card) {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

:deep(.el-card:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

:deep(.el-descriptions) {
  padding: 16px;
  background-color: rgba(64, 158, 255, 0.05);
  border-radius: 12px;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}

:deep(.el-tag) {
  border-radius: 12px;
  padding: 0 10px;
  font-weight: normal;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, var(--el-color-primary), #79bbff);
  border: none;
}

:deep(.el-button--primary.is-link) {
  background: none;
}

:deep(.el-button--warning.is-link:hover),
:deep(.el-button--danger.is-link:hover),
:deep(.el-button--primary.is-link:hover) {
  background-color: rgba(64, 158, 255, 0.05);
  border-radius: 4px;
}

:deep(.el-input__inner),
:deep(.el-select__wrapper),
:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-collapse-item__arrow) {
  margin: 0 0 0 auto;
  position: relative;
  right: 0;
}

@media (max-width: 768px) {
  .health-records {
    padding: 16px;
  }

  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .client-id-input,
  .level-filter,
  .date-picker,
  .staff-filter {
    width: 100%;
  }

  .client-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

.smart-assessment {
  margin-top: 24px;
  margin-bottom: 24px;
}

.smart-assessment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.smart-assessment-header h3 {
  margin: 0;
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.markdown-content {
  background-color: #f7f9fc;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid var(--el-color-primary);
  line-height: 1.7;
  color: var(--el-text-color-primary);
  overflow-wrap: break-word;
  position: relative;
}

.disclaimer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #e0e0e0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.disclaimer .el-icon {
  color: var(--el-color-warning);
  font-size: 14px;
}

.markdown-content :deep(h3) {
  color: var(--el-color-primary);
  font-size: 16px;
  margin-top: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 6px;
}

.markdown-content :deep(ul) {
  padding-left: 18px;
}

.markdown-content :deep(li) {
  margin-bottom: 6px;
}

.markdown-content :deep(p) {
  margin-bottom: 12px;
  line-height: 1.6;
}

.markdown-content :deep(strong) {
  color: var(--el-color-danger);
  font-weight: 600;
}

.no-assessment {
  padding: 24px 16px;
  background-color: #f7f9fc;
  border-radius: 8px;
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  border: 1px dashed #e0e0e0;
}
</style> 