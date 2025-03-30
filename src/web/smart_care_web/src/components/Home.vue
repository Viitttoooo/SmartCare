<template>
  <div class="home">
    <!-- 管理员和员工视图 -->
    <template v-if="isStaff">
      <div v-if="!selectedClient">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1>数据概览</h1>
          <div class="page-description">欢迎使用康养管理系统，以下是系统数据概览</div>
        </div>
        
        <!-- 预约数据展示区域 -->
        <div class="section-container">
          <div class="section-header">
            <h2>预约数据展示</h2>
            <div class="section-actions">
              <el-button size="small" type="primary" plain @click="refreshAppointmentData">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </div>
          <div class="charts-row">
            <div class="chart-container">
              <h3>预约满意度</h3>
              <div v-if="hasAppointmentData" ref="appointmentSatisfactionChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
            <div class="chart-container">
              <h3>预约状态</h3>
              <div v-if="hasAppointmentData" ref="appointmentStateChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
            <div class="chart-container">
              <h3>服务类型</h3>
              <div v-if="hasAppointmentData" ref="serviceTypeChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
        </div>

        <!-- 护理计划数据展示区域 -->
        <div class="section-container">
          <div class="section-header">
            <h2>护理计划数据展示</h2>
            <div class="section-actions">
              <el-button size="small" type="primary" plain @click="refreshPlanData">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </div>
          <div class="charts-row">
            <div class="chart-container">
              <h3>计划满意度</h3>
              <div v-if="hasPlanData" ref="planSatisfactionChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
            <div class="chart-container">
              <h3>计划状态</h3>
              <div v-if="hasPlanData" ref="planStateChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
            <div class="chart-container">
              <h3>计划目标状态</h3>
              <div v-if="hasPlanData" ref="goalStateChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
        </div>

        <!-- 新图表展示区域 -->
        <div class="section-container">
          <div class="section-header">
            <h2>满意度分析</h2>
            <div class="section-actions">
              <el-button size="small" type="primary" plain @click="refreshAllData">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </div>
          
          <!-- 预约满意度时间趋势图 -->
          <div class="chart-row">
            <div class="chart-container trend-chart">
              <div class="chart-header">
                <h3>预约满意度时间趋势</h3>
                <div class="view-selector">
                  <el-radio-group v-model="appointmentTimeView" size="small" @change="updateNewCharts">
                    <el-radio-button label="daily">日视图</el-radio-button>
                    <el-radio-button label="monthly">月视图</el-radio-button>
                    <el-radio-button label="yearly">年视图</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
              <div v-if="hasAppointmentAggregationData" ref="appointmentTimeChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
          
          <!-- 服务满意度和护理计划满意度图 -->
          <div class="chart-row">
            <div class="chart-container trend-chart">
              <div class="chart-header">
                <h3>服务满意度分布</h3>
              </div>
              <div v-if="hasServiceSatisfactionData" ref="serviceSatisfactionChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
            
            <div class="chart-container trend-chart">
              <div class="chart-header">
                <h3>护理计划满意度时间趋势</h3>
                <div class="view-selector">
                  <el-radio-group v-model="planTimeView" size="small" @change="updateNewCharts">
                    <el-radio-button label="daily">日视图</el-radio-button>
                    <el-radio-button label="monthly">月视图</el-radio-button>
                    <el-radio-button label="yearly">年视图</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
              <div v-if="hasPlanAggregationData" ref="planTimeChart" class="chart"></div>
              <el-empty v-else description="暂无数据" />
            </div>
          </div>
        </div>

        <!-- 客户列表区域 -->
        <div class="section-container">
          <div class="section-header">
            <h2>客户列表</h2>
            <div class="section-actions">
              <el-input
                v-model="clientFilter"
                placeholder="搜索客户ID/姓名"
                clearable
                class="filter-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
          <el-table 
            :data="filteredClients" 
            style="width: 100%"
            @row-click="handleClientClick"
            :row-class-name="tableRowClassName"
            border
            stripe
            highlight-current-row
          >
            <el-table-column prop="client_id" label="客户ID" min-width="100" align="center" />
            <el-table-column label="姓名" min-width="150" align="center">
              <template #default="{ row }">
                <span class="client-name">{{ row.last_name }}{{ row.first_name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="护理等级" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getCareTypeTag(row.care_level)" size="small">
                  {{ row.care_level }} 级
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="性别" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag 
                  :type="row.gender === '男' ? 'info' : 'danger'" 
                  size="small"
                  effect="plain"
                >
                  {{ row.gender }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="出生日期" min-width="150" align="center">
              <template #default="{ row }">
                {{ row.birth_date || '未设置' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="120" align="center">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click.stop="handleClientClick(row)"
                >
                  查看数据
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 客户身体数据展示页面 -->
      <div v-else class="client-metrics">
        <div class="page-header">
          <div class="header-section">
            <el-button @click="backToHome" type="primary" plain>
              <el-icon><ArrowLeft /></el-icon>
              返回首页
            </el-button>
            <h1>{{ selectedClient.last_name }}{{ selectedClient.first_name }} 的身体数据记录</h1>
          </div>
          <div class="client-info">
            <div class="info-item">
              <span class="label">客户ID:</span>
              <span class="value">{{ selectedClient.client_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">性别:</span>
              <span class="value">{{ selectedClient.gender }}</span>
            </div>
            <div class="info-item">
              <span class="label">护理等级:</span>
              <span class="value">{{ selectedClient.care_level }} 级</span>
            </div>
            <div class="info-item" v-if="selectedClient.birth_date">
              <span class="label">出生日期:</span>
              <span class="value">{{ selectedClient.birth_date }}</span>
            </div>
          </div>
        </div>
        <div class="metrics-charts">
          <template v-if="hasMetricsData">
            <div class="chart-container" v-for="(metric, key) in metricsConfig" :key="key">
              <h3>{{ metric.title }}</h3>
              <div :ref="el => metricsCharts[key] = el" class="chart"></div>
              <div class="chart-info" v-if="metric.normalRange">
                <span class="normal-range">正常范围: {{ metric.normalRange }}</span>
              </div>
            </div>
          </template>
          <el-empty v-else description="暂无身体数据记录" />
        </div>
      </div>
    </template>

    <!-- 客户视图 -->
    <template v-else>
      <div class="client-metrics">
        <div class="page-header">
          <h1>我的身体数据记录</h1>
          <div class="page-description">以下是您的身体健康数据趋势图</div>
        </div>
        <div class="metrics-charts">
          <template v-if="hasMetricsData">
            <div class="chart-container" v-for="(metric, key) in metricsConfig" :key="key">
              <h3>{{ metric.title }}</h3>
              <div :ref="el => metricsCharts[key] = el" class="chart"></div>
              <div class="chart-info" v-if="metric.normalRange">
                <span class="normal-range">正常范围: {{ metric.normalRange }}</span>
              </div>
            </div>
          </template>
          <el-empty v-else description="暂无身体数据记录" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue';
import { Search, ArrowLeft, Refresh } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import http from '../utils/axios';

// 用户角色判断
const isStaff = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return user.role_name === '员工' || user.role_name === '管理员';
});

// 数据存储
const appointments = ref([]);
const carePlans = ref([]);
const clients = ref([]);
const metrics = ref([]);
const selectedClient = ref(null);
const appointmentAggregation = ref(null);
const planAggregation = ref(null);

// 时间视图类型
const appointmentTimeView = ref('daily');
const planTimeView = ref('daily');

// 图表实例存储
const appointmentSatisfactionChart = ref(null);
const appointmentStateChart = ref(null);
const serviceTypeChart = ref(null);
const planSatisfactionChart = ref(null);
const planStateChart = ref(null);
const goalStateChart = ref(null);
const metricsCharts = ref({});

// 新增图表
const appointmentTimeChart = ref(null);
const serviceSatisfactionChart = ref(null);
const planTimeChart = ref(null);

// 客户筛选
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

// 数据加载状态
const hasAppointmentData = computed(() => appointments.value.length > 0);
const hasPlanData = computed(() => carePlans.value.length > 0);
const hasMetricsData = computed(() => metrics.value.length > 0);
const hasAppointmentAggregationData = computed(() => appointmentAggregation.value && 
  (appointmentTimeView.value === 'daily' ? appointmentAggregation.value.daily_avg.length > 0 : 
   appointmentTimeView.value === 'monthly' ? appointmentAggregation.value.monthly_avg.length > 0 : 
   appointmentAggregation.value.yearly_avg.length > 0));
const hasServiceSatisfactionData = computed(() => appointmentAggregation.value && 
  appointmentAggregation.value.service_avg && appointmentAggregation.value.service_avg.length > 0);
const hasPlanAggregationData = computed(() => planAggregation.value && 
  (planTimeView.value === 'daily' ? planAggregation.value.daily_avg.length > 0 : 
   planTimeView.value === 'monthly' ? planAggregation.value.monthly_avg.length > 0 : 
   planAggregation.value.yearly_avg.length > 0));

// 身体指标配置
const metricsConfig = {
  bmi: { title: 'BMI指数', unit: '', normalRange: '18.5-24.9' },
  heart_rate: { title: '心率', unit: 'bpm', normalRange: '60-100' },
  systolic: { title: '收缩压', unit: 'mmHg', normalRange: '90-140' },
  diastolic: { title: '舒张压', unit: 'mmHg', normalRange: '60-90' },
  body_temperature: { title: '体温', unit: '°C', normalRange: '36.3-37.2' },
  respiratory_rate: { title: '呼吸率', unit: 'bpm', normalRange: '12-20' },
  oxygen_saturation: { title: '血氧饱和度', unit: '%', normalRange: '95-100' },
  weight: { title: '体重', unit: 'kg', normalRange: null },
  height: { title: '身高', unit: 'cm', normalRange: null },
  waist_circumference: { title: '腰围', unit: 'cm', normalRange: '<90 (男性), <80 (女性)' },
  uric_acid: { title: '尿酸', unit: 'mg/dL', normalRange: '3.4-7.0 (男性), 2.4-6.0 (女性)' },
  albuminuria: { title: '尿蛋白', unit: 'mg/L', normalRange: '<30' },
  blood_glucose: { title: '血糖', unit: 'mmol/L', normalRange: '<5.6 (空腹)' },
  triglycerides: { title: '甘油三酯', unit: 'mmol/L', normalRange: '<1.7' },
  hdl_cholesterol: { title: 'HDL胆固醇', unit: 'mmol/L', normalRange: '>1.0' },
  urine_albumin_creatinine_ratio: { title: '尿白蛋白肌酐比', unit: 'mg/g', normalRange: '<30' }
};

// 图表主题色
const chartColors = [
  '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272', '#FC8452', '#9A60B4'
];

// 获取护理等级对应的标签类型
const getCareTypeTag = (level) => {
  const levelNum = parseInt(level);
  if (levelNum <= 1) return 'success';
  if (levelNum <= 3) return 'warning';
  return 'danger';
};

// 刷新数据
const refreshAppointmentData = () => {
  fetchAppointments();
};

const refreshPlanData = () => {
  fetchCarePlans();
};

// 刷新所有数据
const refreshAllData = () => {
  fetchAppointments();
  fetchCarePlans();
};

// 初始化饼图
const initPieChart = (chartRef, title, data) => {
  if (!chartRef.value) return;
  
  const chart = echarts.init(chartRef.value);
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      padding: [8, 12]
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: {
        color: '#606266'
      },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 12
    },
    series: [{
      name: title,
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '40%'],
      avoidLabelOverlap: true,
      data: data,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        },
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold'
        }
      }
    }],
    color: chartColors
  };
  
  chart.setOption(option);
  return chart;
};

// 初始化折线图
const initLineChart = (chartRef, title, data) => {
  if (!chartRef) return;
  
  // 按照日期排序（从旧到新）
  const sortedData = [...Array(data.dates.length).keys()]
    .map(i => ({ date: data.dates[i], value: data.values[i] }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));
  
  const sortedDates = sortedData.map(item => item.date);
  const sortedValues = sortedData.map(item => item.value);
  
  const chart = echarts.init(chartRef);
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0];
        return `${param.name}<br/>${param.marker}${param.value}${data.unit}`;
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      padding: [8, 12]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: sortedDates,
      axisLabel: {
        color: '#606266',
        fontSize: 10,
        rotate: 30
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: data.unit,
      nameTextStyle: {
        color: '#606266',
        padding: [0, 0, 0, 30]
      },
      axisLabel: {
        color: '#606266'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [{
      name: title,
      type: 'line',
      smooth: true,
      data: sortedValues,
      symbolSize: 6,
      itemStyle: {
        color: chartColors[0]
      },
      lineStyle: {
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
          offset: 0,
          color: chartColors[0] + '40'
        }, {
          offset: 1,
          color: chartColors[0] + '10'
        }])
      }
    }],
    markLine: data.normalRange ? {
      silent: true,
      lineStyle: {
        color: '#909399',
        type: 'dashed'
      },
      label: {
        position: 'start',
        formatter: '{b}'
      },
      data: [
        { yAxis: data.normalRange[0], name: '下限' },
        { yAxis: data.normalRange[1], name: '上限' }
      ]
    } : undefined
  };
  
  chart.setOption(option);
  return chart;
};

// 初始化柱状图
const initBarChart = (chartRef, title, data, options = {}) => {
  if (!chartRef) return;
  
  const chart = echarts.init(chartRef);
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: options.formatter || null,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      padding: [8, 12]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      axisLabel: {
        color: '#606266',
        fontSize: options.xAxisFontSize || 10,
        rotate: options.xAxisRotate || 0,
        interval: options.xAxisInterval || 0,
        formatter: options.xAxisFormatter || null
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: data.yAxisName || '',
      min: options.yAxisMin,
      max: options.yAxisMax,
      nameTextStyle: {
        color: '#606266',
        padding: [0, 0, 0, 30]
      },
      axisLabel: {
        color: '#606266',
        formatter: options.yAxisFormatter || null
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [{
      name: title,
      type: 'bar',
      barWidth: options.barWidth || '60%',
      data: data.series,
      itemStyle: {
        color: options.color || chartColors[0],
        borderRadius: 4
      },
      label: options.showLabels ? {
        show: true,
        position: 'top',
        formatter: options.labelFormatter || '{c}',
        fontSize: 12,
        color: '#606266'
      } : null
    }],
    color: chartColors
  };
  
  chart.setOption(option);
  return chart;
};

// 处理客户点击事件
const handleClientClick = (row) => {
  selectedClient.value = row;
  fetchClientMetrics(row.client_id);
};

// 返回首页
const backToHome = () => {
  selectedClient.value = null;
  metrics.value = [];
  
  // 重新加载首页数据
  if (isStaff.value) {
    fetchAppointments();
    fetchCarePlans();
    fetchClients();
  }
};

// 表格行样式
const tableRowClassName = () => {
  return 'clickable-row';
};

// 数据获取函数
const fetchAppointments = async () => {
  try {
    const response = await http.get('/api/appointments/all/');
    appointments.value = response.data.appointments;
    appointmentAggregation.value = response.data.aggregations;
    nextTick(() => {
      updateAppointmentCharts();
      updateNewCharts();
    });
  } catch (error) {
    console.error('获取预约数据失败:', error);
  }
};

const fetchCarePlans = async () => {
  try {
    const response = await http.get('/api/plans/all/');
    carePlans.value = response.data.plans;
    planAggregation.value = response.data.aggregations;
    nextTick(() => {
      updatePlanCharts();
      updateNewCharts();
    });
  } catch (error) {
    console.error('获取护理计划数据失败:', error);
  }
};

const fetchClients = async () => {
  try {
    const response = await http.get('/api/clients/');
    clients.value = response.data;
  } catch (error) {
    console.error('获取客户列表失败:', error);
  }
};

const fetchClientMetrics = async (clientId) => {
  try {
    // 如果是员工/管理员，使用传入的 clientId
    // 如果是客户，从本地存储中获取 client_id
    let id = clientId;
    if (!isStaff.value) {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      id = user.client_id;
      
      if (!id) {
        console.error('未找到客户ID信息');
        return;
      }
    }
    
    const response = await http.get(`/api/metrics/get/${id}/`);
    // 按照记录时间排序
    metrics.value = response.data.sort((a, b) => new Date(a.record_date) - new Date(b.record_date));
    nextTick(() => {
      updateMetricsCharts();
    });
  } catch (error) {
    console.error('获取身体数据失败:', error);
  }
};

// 更新图表函数
const updateAppointmentCharts = () => {
  if (!hasAppointmentData.value) return;

  // 预约满意度统计
  const satisfactionData = appointments.value.reduce((acc, app) => {
    if (app.satisfaction !== null) {
      acc[app.satisfaction] = (acc[app.satisfaction] || 0) + 1;
    }
    return acc;
  }, {});

  // 预约状态统计
  const stateData = appointments.value.reduce((acc, app) => {
    acc[app.state] = (acc[app.state] || 0) + 1;
    return acc;
  }, {});

  // 服务类型统计
  const serviceData = appointments.value.reduce((acc, app) => {
    acc[app.service_name] = (acc[app.service_name] || 0) + 1;
    return acc;
  }, {});

  // 确保DOM元素已经渲染
  nextTick(() => {
    if (appointmentSatisfactionChart.value) {
      initPieChart(
        appointmentSatisfactionChart,
        '预约满意度',
        Object.entries(satisfactionData).map(([key, value]) => ({
          name: `${key}分`,
          value
        }))
      );
    }

    if (appointmentStateChart.value) {
      initPieChart(
        appointmentStateChart,
        '预约状态',
        Object.entries(stateData).map(([key, value]) => ({
          name: key,
          value
        }))
      );
    }

    if (serviceTypeChart.value) {
      initPieChart(
        serviceTypeChart,
        '服务类型',
        Object.entries(serviceData).map(([key, value]) => ({
          name: key,
          value
        }))
      );
    }
  });
};

const updatePlanCharts = () => {
  if (!hasPlanData.value) return;

  // 计划满意度统计
  const satisfactionData = carePlans.value.reduce((acc, plan) => {
    if (plan.plan_satisfaction !== null) {
      acc[plan.plan_satisfaction] = (acc[plan.plan_satisfaction] || 0) + 1;
    }
    return acc;
  }, {});

  // 计划状态统计
  const stateData = carePlans.value.reduce((acc, plan) => {
    acc[plan.plan_state] = (acc[plan.plan_state] || 0) + 1;
    return acc;
  }, {});

  // 目标状态统计
  const goalData = carePlans.value.reduce((acc, plan) => {
    plan.goals.forEach(goal => {
      acc[goal.goal_state] = (acc[goal.goal_state] || 0) + 1;
    });
    return acc;
  }, {});

  // 确保DOM元素已经渲染
  nextTick(() => {
    if (planSatisfactionChart.value) {
      initPieChart(
        planSatisfactionChart,
        '计划满意度',
        Object.entries(satisfactionData).map(([key, value]) => ({
          name: `${key}分`,
          value
        }))
      );
    }

    if (planStateChart.value) {
      initPieChart(
        planStateChart,
        '计划状态',
        Object.entries(stateData).map(([key, value]) => ({
          name: key,
          value
        }))
      );
    }

    if (goalStateChart.value) {
      initPieChart(
        goalStateChart,
        '目标状态',
        Object.entries(goalData).map(([key, value]) => ({
          name: key,
          value
        }))
      );
    }
  });
};

// 更新新增的图表
const updateNewCharts = () => {
  // 更新预约满意度时间趋势图
  if (hasAppointmentAggregationData.value && appointmentTimeChart.value) {
    let data;
    let options = {
      yAxisMin: 0,
      yAxisMax: 10,
      yAxisFormatter: '{value} 分',
      showLabels: true,
      labelFormatter: '{c} 分',
    };
    
    if (appointmentTimeView.value === 'daily') {
      data = {
        xAxis: appointmentAggregation.value.daily_avg.map(item => item.date),
        series: appointmentAggregation.value.daily_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
      options.xAxisFormatter = value => value.slice(5); // 只显示月-日
    } else if (appointmentTimeView.value === 'monthly') {
      data = {
        xAxis: appointmentAggregation.value.monthly_avg.map(item => item.month),
        series: appointmentAggregation.value.monthly_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
    } else {
      data = {
        xAxis: appointmentAggregation.value.yearly_avg.map(item => item.year),
        series: appointmentAggregation.value.yearly_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
    }
    
    initTrendChart(
      appointmentTimeChart.value,
      '预约满意度时间趋势',
      data,
      options
    );
  }

  // 更新服务满意度分布图
  if (hasServiceSatisfactionData.value && serviceSatisfactionChart.value) {
    const serviceData = appointmentAggregation.value.service_avg;
    
    // 排序 - 按满意度从高到低
    const sortedData = [...serviceData].sort((a, b) => b.avg_satisfaction - a.avg_satisfaction);
    
    const data = {
      xAxis: sortedData.map(item => item.service_name),
      series: sortedData.map(item => item.avg_satisfaction),
      yAxisName: '平均满意度（分）'
    };
    
    const options = {
      yAxisMin: 0,
      yAxisMax: 10,
      yAxisFormatter: '{value} 分',
      xAxisRotate: 30,
      showLabels: true,
      labelFormatter: '{c} 分',
      barWidth: '50%',
      color: chartColors[1]
    };
    
    initBarChart(
      serviceSatisfactionChart.value,
      '服务满意度分布',
      data,
      options
    );
  }

  // 更新护理计划满意度时间趋势图
  if (hasPlanAggregationData.value && planTimeChart.value) {
    let data;
    let options = {
      yAxisMin: 0,
      yAxisMax: 10,
      yAxisFormatter: '{value} 分',
      showLabels: true,
      labelFormatter: '{c} 分',
      color: chartColors[2]
    };
    
    if (planTimeView.value === 'daily') {
      data = {
        xAxis: planAggregation.value.daily_avg.map(item => item.date),
        series: planAggregation.value.daily_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
      options.xAxisFormatter = value => value.slice(5); // 只显示月-日
    } else if (planTimeView.value === 'monthly') {
      data = {
        xAxis: planAggregation.value.monthly_avg.map(item => item.month),
        series: planAggregation.value.monthly_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
    } else {
      data = {
        xAxis: planAggregation.value.yearly_avg.map(item => item.year),
        series: planAggregation.value.yearly_avg.map(item => item.avg_satisfaction),
        yAxisName: '平均满意度（分）'
      };
    }
    
    initTrendChart(
      planTimeChart.value,
      '护理计划满意度时间趋势',
      data,
      options
    );
  }
};

// 初始化趋势图（柱状图+曲线图）
const initTrendChart = (chartRef, title, data, options = {}) => {
  if (!chartRef) return;
  
  // 确定柱状图颜色
  const barColor = options.color || chartColors[0];
  
  // 根据柱状图颜色选择最佳趋势线颜色
  let lineColor;
  if (barColor === chartColors[0]) { // 绿色
    lineColor = '#3366CC'; // 深蓝色
  } else if (barColor === chartColors[2]) { // 红色
    lineColor = '#5470C6'; // 蓝紫色
  } else {
    // 默认使用浅蓝色
    lineColor = '#73C0DE';
  }
  
  const chart = echarts.init(chartRef);
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: options.formatter || '{b}<br/>{a0}: {c0} 分<br/>{a1}: {c1} 分',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      padding: [8, 12]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',  // 增加底部空间，为图例留出更多位置
      containLabel: true
    },
    legend: {
      data: ['满意度值', '趋势线'],
      bottom: '0%',  // 将图例固定在底部
      textStyle: {
        color: '#606266',
        fontSize: 12
      },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 15,
      padding: [5, 5, 5, 5]  // 给图例增加内边距
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      axisLabel: {
        color: '#606266',
        fontSize: options.xAxisFontSize || 10,
        rotate: options.xAxisRotate || 0,
        interval: options.xAxisInterval || 0,
        formatter: options.xAxisFormatter || null,
        margin: 14  // 增加标签与轴的距离
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: data.yAxisName || '',
      min: options.yAxisMin,
      max: options.yAxisMax,
      nameTextStyle: {
        color: '#606266',
        padding: [0, 0, 0, 30]
      },
      axisLabel: {
        color: '#606266',
        formatter: options.yAxisFormatter || null
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '满意度值',
        type: 'bar',
        barWidth: options.barWidth || '50%',
        data: data.series,
        itemStyle: {
          color: barColor,
          borderRadius: [4, 4, 0, 0]
        },
        label: options.showLabels ? {
          show: true,
          position: 'top',
          formatter: options.labelFormatter || '{c}',
          fontSize: 12,
          color: '#606266'
        } : null
      },
      {
        name: '趋势线',
        type: 'line',
        smooth: true,
        data: data.series,
        symbolSize: 6,
        symbol: 'circle',
        z: 10,
        itemStyle: {
          color: lineColor
        },
        lineStyle: {
          width: 3,
          color: lineColor,
          shadowColor: 'rgba(0, 0, 0, 0.2)',
          shadowBlur: 5,
          shadowOffsetY: 5,
          cap: 'round'
        }
      }
    ],
    color: chartColors
  };
  
  chart.setOption(option);
  return chart;
};

const updateMetricsCharts = () => {
  if (!hasMetricsData.value) return;

  Object.entries(metricsConfig).forEach(([key, config]) => {
    const chartData = {
      dates: [],
      values: [],
      unit: config.unit,
      normalRange: null
    };

    // 处理不同格式的正常范围
    if (config.normalRange) {
      if (config.normalRange.includes('-')) {
        // 处理标准范围格式，如 "18.5-24.9"
        chartData.normalRange = config.normalRange.split('-').map(Number);
      } else if (config.normalRange.startsWith('<')) {
        // 处理上限格式，如 "<30"
        const upperLimit = parseFloat(config.normalRange.substring(1).trim());
        chartData.normalRange = [0, upperLimit];
      } else if (config.normalRange.startsWith('>')) {
        // 处理下限格式，如 ">1.0"
        const lowerLimit = parseFloat(config.normalRange.substring(1).trim());
        chartData.normalRange = [lowerLimit, lowerLimit * 2]; // 使用下限的两倍作为上限进行显示
      } else if (config.normalRange.includes(',')) {
        // 处理性别差异格式，如 "3.4-7.0 (男性), 2.4-6.0 (女性)"
        // 简化处理：使用第一个范围
        const firstRange = config.normalRange.split(',')[0];
        const matches = firstRange.match(/(\d+\.?\d*)-(\d+\.?\d*)/);
        if (matches && matches.length >= 3) {
          chartData.normalRange = [parseFloat(matches[1]), parseFloat(matches[2])];
        }
      }
    }

    // 数据已经在fetchClientMetrics中按时间排序
    metrics.value.forEach(metric => {
      const date = new Date(metric.record_date);
      const localDate = new Date(date.getTime() + date.getTimezoneOffset() * 60000 + 8 * 3600000); // 转换为北京时间
      const dateStr = localDate.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });

      let value = null;
      if (key === 'systolic' || key === 'diastolic') {
        value = metric.vital_signs.blood_pressure[key]?.value;
      } else {
        value = metric.vital_signs[key]?.value;
      }

      if (value !== null) {
        chartData.dates.push(dateStr);
        chartData.values.push(value);
      }
    });

    if (chartData.values.length > 0) {
      const chartRef = metricsCharts.value[key];
      if (chartRef) {
        initLineChart(chartRef, config.title, chartData);
      }
    }
  });
};

// 组件挂载
onMounted(() => {
  loadData();
});

// 加载数据函数
const loadData = () => {
  if (isStaff.value) {
    if (!selectedClient.value) {
      fetchAppointments();
      fetchCarePlans();
      fetchClients();
    } else {
      fetchClientMetrics(selectedClient.value.client_id);
    }
  } else {
    fetchClientMetrics();
  }
};

// 监听窗口大小变化，重新渲染图表
window.addEventListener('resize', () => {
  if (selectedClient.value) {
    nextTick(() => {
      updateMetricsCharts();
    });
  } else if (isStaff.value) {
    nextTick(() => {
      updateAppointmentCharts();
      updatePlanCharts();
      updateNewCharts();
    });
  }
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', () => {});
});
</script>

<style scoped>
.home {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 40px);
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

.section-container {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.section-container:hover {
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

.section-actions {
  display: flex;
  gap: 12px;
}

.charts-row, .chart-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-row {
  flex-wrap: wrap;
}

@media (max-width: 1200px) {
  .charts-row, .chart-row {
    flex-direction: column;
  }
}

.chart-container {
  flex: 1;
  min-height: 320px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.trend-chart {
  min-width: 400px;
}

.chart-container:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin: 0 0 16px;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 500;
  text-align: center;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
}

.view-selector {
  display: flex;
  align-items: center;
}

.chart {
  height: 280px;
}

.chart-info {
  margin-top: 8px;
  text-align: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.normal-range {
  background-color: #f0f9eb;
  color: #67c23a;
  padding: 2px 8px;
  border-radius: 4px;
}

.filter-input {
  width: 300px;
}

.clickable-row {
  cursor: pointer;
  transition: all 0.2s;
}

.clickable-row:hover {
  background-color: var(--el-table-row-hover-bg-color) !important;
}

.client-metrics {
  padding: 20px;
}

.header-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.header-section h1 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 22px;
  font-weight: 600;
}

.client-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: var(--el-text-color-secondary);
  margin-right: 8px;
}

.info-item .value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.metrics-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

.client-name {
  font-weight: 500;
}

:deep(.el-empty) {
  padding: 40px 0;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #fafafa;
}
</style> 