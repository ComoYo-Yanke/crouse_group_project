<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile } from '@/api/user'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  height: 170,
  weight: 60,
  age: 25,
  gender: '男',
  goal: '维持',
  avoid: '',
  allergy: ''
})

const profileInfo = ref(null) // 展示 BMR、目标摄入

async function loadProfile() {
  loading.value = true
  try {
    const p = await getProfile()
    profileInfo.value = p
    Object.assign(form, {
      height: p.height,
      weight: p.weight,
      age: p.age,
      gender: p.gender,
      goal: p.goal,
      avoid: p.avoid || '',
      allergy: p.allergy || ''
    })
    userStore.profile = p
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const p = await updateProfile(form)
    profileInfo.value = p?.profile || profileInfo.value
    userStore.profile = p?.profile || userStore.profile
    ElMessage.success('画像已更新')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="profile-page" v-loading="loading">
    <!-- 概览卡 -->
    <el-card v-if="profileInfo" class="page-card overview-card">
      <div class="overview">
        <el-avatar :size="64" class="avatar">
          {{ (profileInfo.username || 'U').charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="overview-info">
          <div class="overview-name">{{ profileInfo.username }}</div>
          <el-tag type="success" effect="plain">{{ profileInfo.goal }}</el-tag>
        </div>
        <div class="overview-stats">
          <div class="stat">
            <div class="stat-value">{{ profileInfo.bmr }}</div>
            <div class="stat-label">基础代谢 BMR (kcal)</div>
          </div>
          <div class="stat">
            <div class="stat-value nutri-calories">{{ profileInfo.targetCalories }}</div>
            <div class="stat-label">目标摄入 (kcal/天)</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 编辑画像 -->
    <el-card class="page-card">
      <div class="page-title">编辑个人画像</div>
      <el-form :model="form" label-width="90px" style="max-width: 520px">
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="身高(cm)">
          <el-input-number v-model="form.height" :min="80" :max="250" />
        </el-form-item>
        <el-form-item label="体重(kg)">
          <el-input-number v-model="form.weight" :min="20" :max="300" />
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="10" :max="100" />
        </el-form-item>
        <el-form-item label="目标">
          <el-select v-model="form.goal">
            <el-option label="减脂" value="减脂" />
            <el-option label="增肌" value="增肌" />
            <el-option label="控糖" value="控糖" />
            <el-option label="维持" value="维持" />
          </el-select>
        </el-form-item>
        <el-form-item label="忌口">
          <el-input v-model="form.avoid" placeholder="如：香菜、内脏" />
        </el-form-item>
        <el-form-item label="过敏原">
          <el-input v-model="form.allergy" placeholder="如：花生、海鲜" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存画像</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 720px;
  margin: 0 auto;
}

.overview-card {
  margin-bottom: 16px;
}

.overview {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.avatar {
  background: #67c23a;
  color: #fff;
  font-size: 26px;
}

.overview-name {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 6px;
}

.overview-stats {
  display: flex;
  gap: 48px;
  margin-left: auto;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

@media (max-width: 640px) {
  .overview-stats {
    margin-left: 0;
  }
}
</style>
