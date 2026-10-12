<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateRecipe } from '@/api/ai'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const result = ref(null) // { breakfast, lunch, dinner, shoppingList }

const form = reactive({
  goal: '减脂',
  budget: 50,
  ingredients: '',
  avoid: ''
})

async function handleGenerate() {
  loading.value = true
  result.value = null
  try {
    // 默认带入用户画像的忌口
    const avoid = form.avoid || userStore.profile?.avoid || ''
    const data = await generateRecipe({ ...form, avoid })
    result.value = data
    ElMessage.success('菜谱生成成功')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

const mealIcons = { breakfast: '🌅', lunch: '☀️', dinner: '🌙' }
const mealNames = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' }
</script>

<template>
  <div class="recipe-page">
    <!-- 生成表单 -->
    <el-card class="page-card">
      <div class="page-title">AI 菜谱生成</div>
      <el-form :model="form" label-width="90px">
        <el-form-item label="目标">
          <el-select v-model="form.goal" style="width: 200px">
            <el-option label="减脂" value="减脂" />
            <el-option label="增肌" value="增肌" />
            <el-option label="控糖" value="控糖" />
            <el-option label="维持" value="维持" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算(元/天)">
          <el-input-number v-model="form.budget" :min="10" :max="500" :step="10" />
        </el-form-item>
        <el-form-item label="现有食材">
          <el-input
            v-model="form.ingredients"
            type="textarea"
            :rows="2"
            placeholder="家里有什么就填什么，如：鸡蛋、西红柿、鸡胸肉、米饭（选填）"
          />
        </el-form-item>
        <el-form-item label="忌口">
          <el-input
            v-model="form.avoid"
            :placeholder="`不填则使用画像中的忌口：${userStore.profile?.avoid || '无'}`"
          />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleGenerate">
          {{ loading ? 'AI 生成中…' : '🥗 生成一日三餐' }}
        </el-button>
      </el-form>
    </el-card>

    <!-- 生成结果 -->
    <div v-if="result" class="recipe-result">
      <div class="meals">
        <el-card v-for="meal in ['breakfast', 'lunch', 'dinner']" :key="meal" class="meal-card">
          <div class="meal-title">
            <span class="meal-icon">{{ mealIcons[meal] }}</span>
            {{ mealNames[meal] }}
          </div>
          <div class="meal-name">{{ result[meal]?.name }}</div>
          <div class="meal-ingredients">
            食材：{{ (result[meal]?.ingredients || []).join('、') }}
          </div>
          <div class="meal-calories nutri-calories">{{ result[meal]?.calories }} kcal</div>
        </el-card>
      </div>

      <el-card class="page-card shopping-card">
        <template #header>🛒 购物清单</template>
        <div class="shopping-list">
          <el-tag v-for="(item, i) in result.shoppingList || []" :key="i" class="shopping-item">
            {{ item }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.recipe-page {
  max-width: 1000px;
  margin: 0 auto;
}

.meals {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.meal-card {
  text-align: center;
}

.meal-title {
  font-size: 15px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.meal-icon {
  margin-right: 4px;
}

.meal-name {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.meal-ingredients {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  line-height: 1.6;
}

.meal-calories {
  font-size: 20px;
  font-weight: 700;
}

.shopping-card {
  margin-top: 16px;
}

.shopping-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.shopping-item {
  font-size: 14px;
}
</style>
