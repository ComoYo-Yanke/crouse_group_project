<script setup>
/**
 * AI 生成进度组件
 *
 * 说明：HTTP 请求本身拿不到模型推理的真实进度，因此这里显示的是
 * 「已等待秒数（真实）」+「估算进度（基于预估时长推进，封顶 99%）」，
 * 目的是给用户明确的等待反馈，避免只有转圈造成的焦虑。
 *
 * 用法：
 *   <AiProgress :active="loading" :estimated-sec="90" @cancel="onCancel" />
 */
import { onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  active: { type: Boolean, default: false },
  // 预估生成耗时（秒），仅用于进度条推进速度
  estimatedSec: { type: Number, default: 90 }
})

const emit = defineEmits(['cancel'])

const elapsed = ref(0)
const progress = ref(0)
const stage = ref('正在准备…')
let timer = null

function stageText(sec) {
  if (sec < 10) return '正在整理你的营养数据…'
  if (sec < 40) return '模型推理中，本地大模型通常需要 30~90 秒…'
  if (sec < 90) return '仍在生成，内容较多请耐心等待…'
  return '生成时间较长，可继续等待，也可点击右侧停止…'
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(
  () => props.active,
  (on) => {
    stopTimer()
    if (on) {
      elapsed.value = 0
      progress.value = 0
      stage.value = stageText(0)
      timer = setInterval(() => {
        elapsed.value += 1
        // 封顶 99%：未真正完成前不显示 100%
        progress.value = Math.min(
          99,
          Math.round((elapsed.value / props.estimatedSec) * 95)
        )
        stage.value = stageText(elapsed.value)
      }, 1000)
    } else {
      progress.value = 100 // 完成
    }
  }
)

onUnmounted(stopTimer)
</script>

<template>
  <div v-if="active" class="ai-progress">
    <el-progress
      :percentage="progress"
      :stroke-width="10"
      :show-text="false"
      striped
      striped-flow
    />
    <div class="ai-progress-bar">
      <span class="ai-stage">
        <el-icon class="is-loading"><Loading /></el-icon>
        {{ stage }}
      </span>
      <span class="ai-elapsed">已等待 {{ elapsed }} 秒</span>
      <el-button size="small" type="danger" plain @click="emit('cancel')">
        停止生成
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.ai-progress {
  margin-top: 14px;
}

.ai-progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.ai-stage {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  flex: 1;
  min-width: 200px;
}

.ai-elapsed {
  font-size: 13px;
  color: #909399;
  font-variant-numeric: tabular-nums;
}
</style>
