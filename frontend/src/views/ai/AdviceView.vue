<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateAdvice } from '@/api/ai'
import { getDailyReport } from '@/api/report'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const result = ref(null) // { advice, basedOn, safe }

onMounted(async () => {
  // 尝试获取画像（含 bmr、targetCalories）
  try {
    if (!userStore.profile) await userStore.fetchProfile()
  } catch (e) {
    /* 未登录或后端未启动 */
  }
})

async function handleGenerate() {
  loading.value = true
  result.value = null
  try {
    // 组装 AI 建议所需数据（按 api.md 六.3）
    const profile = userStore.profile || {}
    let todayIntake = { calories: 0, protein: 0, fat: 0, carbs: 0 }
    let gap = { calories: 0, protein: 0, fat: 0, carbs: 0 }
    try {
      const today = new Date().toISOString().slice(0, 10)
      const daily = await getDailyReport(today)
      todayIntake = daily.total
      gap = daily.gap
    } catch (e) {
      /* 今日可能无记录，用 0 值 */
    }

    const data = await generateAdvice({
      profile: {
        goal: profile.goal || '维持',
        bmr: profile.bmr || 1500,
        targetCalories: profile.targetCalories || 2000,
        avoid: profile.avoid || '',
        allergy: profile.allergy || ''
      },
      todayIntake,
      gap
    })
    result.value = data
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="advice-page">
    <el-card class="page-card hero-card">
      <div class="hero">
        <el-icon :size="42" color="#67c23a"><MagicStick /></el-icon>
        <h3>AI 营养师建议</h3>
        <p>基于《中国居民膳食指南》RAG 检索 + 你的画像和今日摄入，给出个性化建议</p>
        <el-button type="primary" size="large" :loading="loading" @click="handleGenerate">
          {{ loading ? 'AI 思考中…' : '下一餐吃什么？获取建议' }}
        </el-button>
      </div>
    </el-card>

    <el-card v-if="result" class="page-card result-card">
      <!-- 安全提示 -->
      <el-alert
        v-if="result.safe === false"
        title="该建议未通过安全检查，已拦截"
        :description="result.reason || '建议内容可能存在健康风险'"
        type="error"
        show-icon
        :closable="false"
        class="safe-alert"
      />
      <el-alert
        v-else
        title="建议已通过安全检查"
        type="success"
        show-icon
        :closable="false"
        class="safe-alert"
      />

      <div class="advice-content">
        <h4>📝 AI 建议</h4>
        <p class="advice-text">{{ result.advice }}</p>
      </div>

      <div v-if="result.basedOn?.length" class="advice-basis">
        <h4>📚 依据（膳食指南）</h4>
        <ul>
          <li v-for="(b, i) in result.basedOn" :key="i">{{ b }}</li>
        </ul>
      </div>
    </el-card>

    <div class="disclaimer">
      ⚠️ 免责声明：AI 建议仅供参考，不能替代专业医疗意见。如有疾病请遵医嘱。
    </div>
  </div>
</template>

<style scoped>
.advice-page {
  max-width: 800px;
  margin: 0 auto;
}

.hero-card .hero {
  text-align: center;
  padding: 24px 0;
}

.hero h3 {
  margin: 12px 0 8px;
  color: #303133;
}

.hero p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.result-card {
  margin-top: 16px;
}

.safe-alert {
  margin-bottom: 16px;
}

.advice-content h4,
.advice-basis h4 {
  margin-bottom: 10px;
  color: #303133;
}

.advice-text {
  background: #f0f9eb;
  border-radius: 8px;
  padding: 16px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

.advice-basis {
  margin-top: 16px;
}

.advice-basis ul {
  padding-left: 20px;
}

.advice-basis li {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
}

.disclaimer {
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 24px;
}
</style>
