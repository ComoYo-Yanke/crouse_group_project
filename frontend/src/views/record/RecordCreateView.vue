<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { recognizeFood, safetyCheck } from '@/api/ai'
import { createRecord } from '@/api/record'

const router = useRouter()

const mode = ref('photo') // photo | text
const loading = ref(false)
const saving = ref(false)
const recognized = ref(false)

// 拍照录入
const imageBase64 = ref('')
const previewUrl = ref('')

// 文字录入
const textDescription = ref('')

// 识别结果（可修正）
const recognizeResult = reactive({
  foods: [], // [{ name, portion, calories, protein, fat, carbs, fiber, sodium, confidence }]
  mealType: '午餐',
  visibility: 'private'
})

const mealTypes = ['早餐', '午餐', '晚餐', '加餐']

// 选择图片
function handleFileChange(file) {
  const raw = file.raw || file
  if (!raw.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
    // 去掉 data:image/xxx;base64, 前缀
    imageBase64.value = e.target.result.split(',')[1]
  }
  reader.readAsDataURL(raw)
}

// 调用 AI 识别
async function handleRecognize() {
  if (mode.value === 'photo' && !imageBase64.value) {
    ElMessage.warning('请先选择食物照片')
    return
  }
  if (mode.value === 'text' && !textDescription.value.trim()) {
    ElMessage.warning('请输入食物描述，如：一碗牛肉面')
    return
  }
  loading.value = true
  recognized.value = false
  try {
    const payload =
      mode.value === 'photo'
        ? { imageBase64: imageBase64.value }
        : { textDescription: textDescription.value.trim() }
    const data = await recognizeFood(payload)
    if (!data?.foods?.length) {
      ElMessage.warning('AI 未识别到食物，请重试或手动填写')
      return
    }
    recognizeResult.foods = data.foods
    recognized.value = true
    ElMessage.success('识别成功，请核对营养数据')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

// 保存记录
async function handleSave() {
  if (!recognizeResult.foods.length) {
    ElMessage.warning('请先识别或手动添加食物')
    return
  }
  saving.value = true
  try {
    // 汇总所有食物营养
    const sum = (key) =>
      recognizeResult.foods.reduce((s, f) => s + (Number(f[key]) || 0), 0)
    const foodNames = recognizeResult.foods.map((f) => f.name).join('、')

    await createRecord({
      foodName: foodNames,
      portion: recognizeResult.foods.map((f) => `${f.name} ${f.portion}`).join('；'),
      mealType: recognizeResult.mealType,
      imageUrl: mode.value === 'photo' ? previewUrl.value : '',
      nutrition: {
        calories: Math.round(sum('calories')),
        protein: Math.round(sum('protein') * 10) / 10,
        fat: Math.round(sum('fat') * 10) / 10,
        carbs: Math.round(sum('carbs') * 10) / 10,
        fiber: Math.round(sum('fiber') * 10) / 10,
        sodium: Math.round(sum('sodium') * 10) / 10
      },
      visibility: recognizeResult.visibility
    })
    ElMessage.success('记录保存成功')
    router.push('/record/list')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}

// 手动添加一行食物
function addFood() {
  recognizeResult.foods.push({
    name: '',
    portion: '1 份',
    calories: 0,
    protein: 0,
    fat: 0,
    carbs: 0,
    fiber: 0,
    sodium: 0,
    confidence: 1
  })
  recognized.value = true
}

function removeFood(index) {
  recognizeResult.foods.splice(index, 1)
}
</script>

<template>
  <div class="create-page">
    <!-- 录入方式切换 -->
    <el-card class="page-card">
      <div class="mode-switch">
        <el-radio-group v-model="mode" size="large">
          <el-radio-button value="photo">📷 拍照录入</el-radio-button>
          <el-radio-button value="text">✏️ 文字录入</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 拍照录入 -->
      <div v-if="mode === 'photo'" class="upload-area">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          accept="image/*"
          :on-change="handleFileChange"
        >
          <div v-if="!previewUrl" class="upload-placeholder">
            <el-icon :size="48" color="#c0c4cc"><Plus /></el-icon>
            <p>点击选择食物照片</p>
            <p class="tip">支持 JPG / PNG，拍照后由 AI 自动识别</p>
          </div>
          <img v-else :src="previewUrl" class="preview-img" alt="食物预览" />
        </el-upload>
      </div>

      <!-- 文字录入 -->
      <div v-else class="text-area">
        <el-input
          v-model="textDescription"
          type="textarea"
          :rows="3"
          size="large"
          placeholder="描述你吃了什么，例如：一碗牛肉面、两个鸡蛋、一杯豆浆"
        />
      </div>

      <div class="action-bar">
        <el-button type="primary" size="large" :loading="loading" @click="handleRecognize">
          <el-icon v-if="!loading"><MagicStick /></el-icon>
          {{ loading ? 'AI 识别中（约 10 秒）…' : '开始 AI 识别' }}
        </el-button>
        <el-button size="large" @click="addFood">手动填写</el-button>
      </div>
    </el-card>

    <!-- 识别结果确认/修正 -->
    <el-card v-if="recognized" class="page-card result-card">
      <template #header>
        <div class="result-header">
          <span>识别结果（可修正）</span>
          <el-button text type="primary" @click="addFood">+ 添加食物</el-button>
        </div>
      </template>

      <el-table :data="recognizeResult.foods" border>
        <el-table-column label="食物" min-width="140">
          <template #default="{ row }">
            <el-input v-model="row.name" placeholder="食物名" />
          </template>
        </el-table-column>
        <el-table-column label="份量" min-width="110">
          <template #default="{ row }">
            <el-input v-model="row.portion" placeholder="如 1 碗" />
          </template>
        </el-table-column>
        <el-table-column label="热量(kcal)" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.calories" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="蛋白质(g)" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.protein" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="脂肪(g)" width="110">
          <template #default="{ row }">
            <el-input-number v-model="row.fat" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="碳水(g)" width="110">
          <template #default="{ row }">
            <el-input-number v-model="row.carbs" :min="0" :controls="false" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.confidence >= 0.8 ? 'success' : row.confidence >= 0.5 ? 'warning' : 'danger'"
              size="small"
            >
              {{ Math.round((row.confidence ?? 1) * 100) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ $index }">
            <el-button text type="danger" @click="removeFood($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="save-bar">
        <div class="save-options">
          <span class="option-label">餐次：</span>
          <el-select v-model="recognizeResult.mealType" style="width: 110px">
            <el-option v-for="t in mealTypes" :key="t" :label="t" :value="t" />
          </el-select>
          <span class="option-label" style="margin-left: 24px">可见性：</span>
          <el-radio-group v-model="recognizeResult.visibility">
            <el-radio value="private">🔒 私密</el-radio>
            <el-radio value="public">🌍 公开（出现在广场）</el-radio>
          </el-radio-group>
        </div>
        <el-button type="primary" size="large" :loading="saving" @click="handleSave">
          保存记录
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.create-page {
  max-width: 1000px;
  margin: 0 auto;
}

.mode-switch {
  text-align: center;
  margin-bottom: 20px;
}

.upload-area {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.upload-placeholder {
  width: 360px;
  height: 240px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-placeholder:hover {
  border-color: #67c23a;
}

.upload-placeholder .tip {
  font-size: 12px;
  color: #c0c4cc;
}

.preview-img {
  max-width: 360px;
  max-height: 280px;
  border-radius: 8px;
  object-fit: cover;
}

.text-area {
  margin-bottom: 16px;
}

.action-bar {
  text-align: center;
}

.result-card {
  margin-top: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.save-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.save-options {
  display: flex;
  align-items: center;
}

.option-label {
  color: #606266;
  font-size: 14px;
}
</style>
