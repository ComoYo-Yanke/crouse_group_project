<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getDailyReport } from '@/api/report'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const today = ref(null)

onMounted(async () => {
  // 尝试加载今日报告（后端未启动时静默失败）
  try {
    const date = new Date().toISOString().slice(0, 10)
    today.value = await getDailyReport(date)
  } catch (e) {
    /* ignore */
  }
})

const features = [
  { icon: 'Camera', title: '拍照识别', desc: '拍下食物，AI 自动估算营养', path: '/record/create' },
  { icon: 'DataAnalysis', title: '营养报告', desc: '每日缺口分析与一周趋势', path: '/report' },
  { icon: 'MagicStick', title: 'AI 建议', desc: '基于膳食指南的个性化建议', path: '/advice' },
  { icon: 'Food', title: 'AI 菜谱', desc: '根据目标预算生成三餐', path: '/recipe' },
  { icon: 'ChatDotRound', title: '健康广场', desc: '晒记录，收获点赞与鼓励', path: '/square' }
]
</script>

<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <el-card class="page-card banner">
      <div class="banner-content">
        <div>
          <h2>你好，{{ userStore.username || '朋友' }} 👋</h2>
          <p>今天吃了什么？拍张照让 AI 营养师帮你分析吧</p>
          <div class="banner-actions">
            <el-button type="primary" size="large" @click="router.push('/record/create')">
              📷 记录一餐
            </el-button>
            <el-button size="large" @click="router.push('/square')">逛逛广场</el-button>
          </div>
        </div>
        <el-icon :size="120" color="#e1f3d8" class="banner-icon"><Food /></el-icon>
      </div>
    </el-card>

    <!-- 今日概览 -->
    <el-card v-if="today" class="page-card today-card">
      <div class="today-title">今日摄入</div>
      <div class="today-stats">
        <div class="t-stat">
          <div class="t-value nutri-calories">{{ today.total?.calories || 0 }}</div>
          <div class="t-label">热量 kcal / 目标 {{ today.target?.calories || '-' }}</div>
        </div>
        <div class="t-stat">
          <div class="t-value nutri-protein">{{ today.total?.protein || 0 }}g</div>
          <div class="t-label">蛋白质</div>
        </div>
        <div class="t-stat">
          <div class="t-value nutri-fat">{{ today.total?.fat || 0 }}g</div>
          <div class="t-label">脂肪</div>
        </div>
        <div class="t-stat">
          <div class="t-value nutri-carbs">{{ today.total?.carbs || 0 }}g</div>
          <div class="t-label">碳水</div>
        </div>
      </div>
    </el-card>

    <!-- 功能入口 -->
    <div class="feature-grid">
      <el-card
        v-for="f in features"
        :key="f.path"
        class="feature-card"
        shadow="hover"
        @click="router.push(f.path)"
      >
        <el-icon :size="36" color="#67c23a"><component :is="f.icon" /></el-icon>
        <div class="feature-title">{{ f.title }}</div>
        <div class="feature-desc">{{ f.desc }}</div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1000px;
  margin: 0 auto;
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.banner h2 {
  color: #303133;
  margin-bottom: 8px;
}

.banner p {
  color: #909399;
  margin-bottom: 20px;
}

.banner-icon {
  flex-shrink: 0;
}

.today-card {
  margin-top: 16px;
}

.today-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.today-stats {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 12px;
}

.t-stat {
  text-align: center;
}

.t-value {
  font-size: 24px;
  font-weight: 700;
}

.t-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.feature-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-top: 10px;
}

.feature-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}
</style>
