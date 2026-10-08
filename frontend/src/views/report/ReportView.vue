<script setup>
import { onMounted, ref, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getDailyReport, getWeeklyReport } from '@/api/report'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const activeTab = ref('daily')
const date = ref(new Date().toISOString().slice(0, 10))
const weekStart = ref(getMonday(new Date()))
const daily = ref(null)
const weekly = ref(null)

// 获取本周一
function getMonday(d) {
  const date = new Date(d)
  const day = date.getDay() || 7
  date.setDate(date.getDate() - day + 1)
  return date.toISOString().slice(0, 10)
}

// 每日报告
async function loadDaily() {
  loading.value = true
  try {
    daily.value = await getDailyReport(date.value)
    await nextTick()
    renderDailyChart()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

// 一周报告
async function loadWeekly() {
  loading.value = true
  try {
    weekly.value = await getWeeklyReport(weekStart.value)
    await nextTick()
    renderWeeklyChart()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

/* ============ 每日图表 ============ */
let dailyChart = null

function renderDailyChart() {
  if (!daily.value || !document.getElementById('daily-chart')) return
  if (!dailyChart) {
    dailyChart = echarts.init(document.getElementById('daily-chart'))
  }
  const { total, target, gap } = daily.value
  const dims = ['calories', 'protein', 'fat', 'carbs']
  const dimNames = { calories: '热量(kcal)', protein: '蛋白质(g)', fat: '脂肪(g)', carbs: '碳水(g)' }
  dailyChart.setOption({
    title: { text: '摄入 vs 目标 vs 缺口', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['实际摄入', '目标', '缺口'], bottom: 0 },
    grid: { left: 50, right: 20, top: 50, bottom: 40 },
    xAxis: { type: 'category', data: dims.map((d) => dimNames[d]) },
    yAxis: { type: 'value' },
    series: [
      { name: '实际摄入', type: 'bar', data: dims.map((d) => total[d]), itemStyle: { color: '#67c23a' } },
      { name: '目标', type: 'bar', data: dims.map((d) => target[d]), itemStyle: { color: '#409eff' } },
      { name: '缺口', type: 'bar', data: dims.map((d) => gap[d]), itemStyle: { color: '#e6a23c' } }
    ]
  })
}

/* ============ 一周趋势图 ============ */
let weeklyChart = null

function renderWeeklyChart() {
  if (!weekly.value || !document.getElementById('weekly-chart')) return
  if (!weeklyChart) {
    weeklyChart = echarts.init(document.getElementById('weekly-chart'))
  }
  const days = weekly.value.days || []
  const dimNames = { calories: '热量(kcal)', protein: '蛋白质(g)', fat: '脂肪(g)', carbs: '碳水(g)' }
  weeklyChart.setOption(
    {
      title: { text: '一周营养趋势', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      legend: { bottom: 0 },
      grid: { left: 50, right: 20, top: 50, bottom: 40 },
      xAxis: { type: 'category', data: days.map((d) => d.date) },
      yAxis: { type: 'value' },
      series: ['calories', 'protein', 'fat', 'carbs'].map((dim) => ({
        name: dimNames[dim],
        type: 'line',
        smooth: true,
        data: days.map((d) => d[dim])
      }))
    },
    true
  )
}

function handleResize() {
  dailyChart?.resize()
  weeklyChart?.resize()
}

watch(activeTab, (tab) => {
  if (tab === 'daily') loadDaily()
  else loadWeekly()
})

onMounted(() => {
  loadDaily()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  weeklyChart?.dispose()
})

function gapText(v) {
  const n = Number(v) || 0
  if (n > 0) return `还差 ${n}`
  if (n < 0) return `超出 ${-n}`
  return '刚好达标'
}
</script>

<template>
  <div class="report-page" v-loading="loading">
    <el-card class="page-card">
      <el-tabs v-model="activeTab">
        <!-- 每日报告 -->
        <el-tab-pane label="每日报告" name="daily">
          <div class="date-picker">
            <span>选择日期：</span>
            <el-date-picker
              v-model="date"
              type="date"
              value-format="YYYY-MM-DD"
              :clearable="false"
              @change="loadDaily"
            />
          </div>

          <el-empty v-if="!daily" description="暂无数据" />

          <template v-else>
            <div class="stat-cards">
              <div class="stat-card">
                <div class="stat-label">热量摄入</div>
                <div class="stat-value nutri-calories">{{ daily.total.calories }}</div>
                <div class="stat-sub">kcal / 目标 {{ daily.target.calories }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">蛋白质</div>
                <div class="stat-value nutri-protein">{{ daily.total.protein }}g</div>
                <div class="stat-sub">{{ gapText(daily.gap.protein) }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">脂肪</div>
                <div class="stat-value nutri-fat">{{ daily.total.fat }}g</div>
                <div class="stat-sub">{{ gapText(daily.gap.fat) }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">碳水</div>
                <div class="stat-value nutri-carbs">{{ daily.total.carbs }}g</div>
                <div class="stat-sub">{{ gapText(daily.gap.carbs) }}</div>
              </div>
            </div>
            <div id="daily-chart" class="chart"></div>
          </template>
        </el-tab-pane>

        <!-- 一周趋势 -->
        <el-tab-pane label="一周趋势" name="weekly">
          <div class="date-picker">
            <span>起始日期（周一）：</span>
            <el-date-picker
              v-model="weekStart"
              type="date"
              value-format="YYYY-MM-DD"
              :clearable="false"
              @change="loadWeekly"
            />
          </div>

          <el-empty v-if="!weekly || !weekly.days?.length" description="本周暂无数据" />
          <div v-else id="weekly-chart" class="chart"></div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style scoped>
.report-page {
  max-width: 1000px;
  margin: 0 auto;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #606266;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  margin: 6px 0 4px;
}

.stat-sub {
  font-size: 12px;
  color: #c0c4cc;
}

.chart {
  width: 100%;
  height: 380px;
}
</style>
