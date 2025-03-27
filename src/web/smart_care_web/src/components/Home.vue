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

// 图表实例存储
const appointmentSatisfactionChart = ref(null);
const appointmentStateChart = ref(null);
const serviceTypeChart = ref(null);
const planSatisfactionChart = ref(null);
const planStateChart = ref(null);
const goalStateChart = ref(null);
const metricsCharts = ref({});

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
    const response = await http.get('/api/appointments/');
    appointments.value = response.data;
    nextTick(() => {
      updateAppointmentCharts();
    });
  } catch (error) {
    console.error('获取预约数据失败:', error);
  }
};

const fetchCarePlans = async () => {
  try {
    const response = await http.get('/api/plans/all/');
    carePlans.value = response.data;
    nextTick(() => {
      updatePlanCharts();
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

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 1200px) {
  .charts-row {
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