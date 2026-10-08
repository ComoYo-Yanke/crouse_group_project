<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/user'

const router = useRouter()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  height: 170,
  weight: 60,
  age: 25,
  gender: '男',
  goal: '维持',
  avoid: '',
  allergy: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入密码不一致'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度 2-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ],
  height: [{ required: true, message: '请输入身高', trigger: 'blur' }],
  weight: [{ required: true, message: '请输入体重', trigger: 'blur' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  goal: [{ required: true, message: '请选择目标', trigger: 'change' }]
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    const { confirmPassword, ...data } = form
    await register(data)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <div class="auth-title">
        <el-icon :size="36" color="#67c23a"><Food /></el-icon>
        <h2>注册私人营养师</h2>
        <p>填写基础信息，获取专属营养方案</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="2-20 个字符" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password />
        </el-form-item>

        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="身高cm" prop="height">
          <el-input-number v-model="form.height" :min="80" :max="250" />
        </el-form-item>
        <el-form-item label="体重kg" prop="weight">
          <el-input-number v-model="form.weight" :min="20" :max="300" />
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="10" :max="100" />
        </el-form-item>
        <el-form-item label="目标" prop="goal">
          <el-select v-model="form.goal" style="width: 100%">
            <el-option label="减脂" value="减脂" />
            <el-option label="增肌" value="增肌" />
            <el-option label="控糖" value="控糖" />
            <el-option label="维持" value="维持" />
          </el-select>
        </el-form-item>
        <el-form-item label="忌口">
          <el-input v-model="form.avoid" placeholder="如：香菜、内脏，用顿号分隔" />
        </el-form-item>
        <el-form-item label="过敏原">
          <el-input v-model="form.allergy" placeholder="如：花生、海鲜，用顿号分隔" />
        </el-form-item>

        <el-button type="primary" class="submit-btn" :loading="loading" @click="handleRegister">
          注 册
        </el-button>
      </el-form>

      <div class="auth-footer">
        已有账号？<el-link type="primary" @click="router.push('/login')">去登录</el-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  padding: 24px 0;
}

.auth-card {
  width: 480px;
  padding: 12px 8px;
}

.auth-title {
  text-align: center;
  margin-bottom: 24px;
}

.auth-title h2 {
  margin: 8px 0 4px;
  color: #303133;
}

.auth-title p {
  font-size: 13px;
  color: #909399;
}

.submit-btn {
  width: 100%;
}

.auth-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}
</style>
