<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRecords, deleteRecord, updateVisibility } from '@/api/record'

const loading = ref(false)
const records = ref([])
const total = ref(null)

const query = reactive({
  date: new Date().toISOString().slice(0, 10),
  mealType: ''
})

const mealTypes = ['早餐', '午餐', '晚餐', '加餐']

async function loadData() {
  loading.value = true
  try {
    const params = { date: query.date }
    if (query.mealType) params.mealType = query.mealType
    const data = await getRecords(params)
    records.value = data.records || []
    total.value = data.total || null
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function handleToggleVisibility(record) {
  const next = record.visibility === 'public' ? 'private' : 'public'
  try {
    await updateVisibility(record.recordId, next)
    record.visibility = next
    ElMessage.success(next === 'public' ? '已公开，广场可见' : '已设为私密')
  } catch (e) {
    /* 拦截器已提示 */
  }
}

async function handleDelete(record) {
  await ElMessageBox.confirm(`确定删除「${record.foodName}」这条记录吗？`, '删除确认', {
    type: 'warning'
  })
  try {
    await deleteRecord(record.recordId)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function mealTagType(mealType) {
  const map = { 早餐: 'success', 午餐: 'primary', 晚餐: 'warning', 加餐: 'info' }
  return map[mealType] || 'info'
}

onMounted(loadData)
</script>

<template>
  <div class="list-page">
    <!-- 筛选栏 -->
    <el-card class="page-card">
      <div class="filter-bar">
        <span class="filter-label">日期：</span>
        <el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" clearable placeholder="全部日期" style="width: 180px" />
        <span class="filter-label">餐次：</span>
        <el-select v-model="query.mealType" clearable placeholder="全部餐次" style="width: 120px">
          <el-option v-for="t in mealTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <el-button type="primary" @click="loadData">查询</el-button>
      </div>
    </el-card>

    <!-- 当日汇总 -->
    <el-card v-if="total" class="page-card summary-card">
      <div class="summary-title">当日摄入汇总</div>
      <div class="summary-items">
        <div class="summary-item">
          <div class="value nutri-calories">{{ total.calories }}</div>
          <div class="label">热量 kcal</div>
        </div>
        <div class="summary-item">
          <div class="value nutri-protein">{{ total.protein }}g</div>
          <div class="label">蛋白质</div>
        </div>
        <div class="summary-item">
          <div class="value nutri-fat">{{ total.fat }}g</div>
          <div class="label">脂肪</div>
        </div>
        <div class="summary-item">
          <div class="value nutri-carbs">{{ total.carbs }}g</div>
          <div class="label">碳水</div>
        </div>
        <div class="summary-item">
          <div class="value nutri-fiber">{{ total.fiber }}g</div>
          <div class="label">纤维</div>
        </div>
        <div class="summary-item">
          <div class="value nutri-sodium">{{ total.sodium }}mg</div>
          <div class="label">钠</div>
        </div>
      </div>
    </el-card>

    <!-- 记录列表 -->
    <el-card v-loading="loading" class="page-card">
      <el-empty v-if="!loading && !records.length" description="该日暂无记录，去记录一餐吧">
        <el-button type="primary" @click="$router.push('/record/create')">记录一餐</el-button>
      </el-empty>

      <div v-for="record in records" :key="record.recordId" class="record-item">
        <img v-if="record.imageUrl" :src="record.imageUrl" class="record-img" alt="" />
        <div v-else class="record-img record-img-placeholder">
          <el-icon :size="28"><Food /></el-icon>
        </div>

        <div class="record-info">
          <div class="record-title">
            <span class="food-name">{{ record.foodName }}</span>
            <el-tag :type="mealTagType(record.mealType)" size="small">{{ record.mealType }}</el-tag>
            <el-tag
              :type="record.visibility === 'public' ? 'success' : 'info'"
              size="small"
              effect="plain"
            >
              {{ record.visibility === 'public' ? '🌍 公开' : '🔒 私密' }}
            </el-tag>
          </div>
          <div class="record-nutrition">
            <span class="nutri-calories">{{ record.nutrition?.calories }} kcal</span>
            <span class="nutri-protein">蛋白 {{ record.nutrition?.protein }}g</span>
            <span class="nutri-fat">脂肪 {{ record.nutrition?.fat }}g</span>
            <span class="nutri-carbs">碳水 {{ record.nutrition?.carbs }}g</span>
          </div>
          <div class="record-time">{{ record.createdAt }}</div>
        </div>

        <div class="record-actions">
          <el-button
            size="small"
            :type="record.visibility === 'public' ? 'info' : 'success'"
            plain
            @click="handleToggleVisibility(record)"
          >
            {{ record.visibility === 'public' ? '设为私密' : '设为公开' }}
          </el-button>
          <el-button size="small" type="danger" plain @click="handleDelete(record)">删除</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.list-page {
  max-width: 1000px;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-label {
  color: #606266;
  font-size: 14px;
  margin-left: 8px;
}

.summary-card {
  margin: 16px 0;
}

.summary-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.summary-items {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 12px;
}

.summary-item {
  text-align: center;
}

.summary-item .value {
  font-size: 22px;
  font-weight: 700;
}

.summary-item .label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.record-item:last-child {
  border-bottom: none;
}

.record-img {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.record-img-placeholder {
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.food-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.record-nutrition {
  display: flex;
  gap: 16px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
}

.record-time {
  font-size: 12px;
  color: #c0c4cc;
}

.record-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
