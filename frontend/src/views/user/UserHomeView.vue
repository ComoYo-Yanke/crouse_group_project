<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUserHome } from '@/api/user'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const home = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    home.value = await getUserHome(route.params.userId)
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="user-home-page" v-loading="loading">
    <el-empty v-if="!loading && !home" description="用户不存在" />

    <template v-if="home">
      <!-- 用户信息 -->
      <el-card class="page-card">
        <div class="user-header">
          <el-avatar :size="64" class="avatar">
            {{ (home.username || 'U').charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-info">
            <div class="username">{{ home.username }}</div>
            <div class="user-bio">的健康饮食公开主页</div>
          </div>
          <div class="user-stats">
            <div class="stat">
              <div class="stat-value">{{ home.totalLikes }}</div>
              <div class="stat-label">获赞</div>
            </div>
            <div class="stat">
              <div class="stat-value">{{ home.totalComments }}</div>
              <div class="stat-label">获评</div>
            </div>
            <div class="stat">
              <div class="stat-value">{{ home.publicRecords?.length || 0 }}</div>
              <div class="stat-label">公开记录</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 公开记录列表 -->
      <el-card class="page-card records-card">
        <template #header>公开记录</template>
        <el-empty v-if="!home.publicRecords?.length" description="TA 还没有公开记录" />
        <div class="record-grid">
          <div
            v-for="record in home.publicRecords"
            :key="record.recordId"
            class="record-cell"
          >
            <img v-if="record.imageUrl" :src="record.imageUrl" class="cell-img" alt="" loading="lazy" />
            <div v-else class="cell-img cell-placeholder">
              <el-icon :size="24"><Food /></el-icon>
            </div>
            <div class="cell-name">{{ record.foodName }}</div>
            <div class="cell-meta">
              <span class="nutri-calories">{{ record.calories }} kcal</span>
              <span>❤️ {{ record.likeCount }}</span>
              <span>💬 {{ record.commentCount }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.user-home-page {
  max-width: 900px;
  margin: 0 auto;
}

.user-header {
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

.username {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.user-bio {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.user-stats {
  display: flex;
  gap: 40px;
  margin-left: auto;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.records-card {
  margin-top: 16px;
}

.record-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.record-cell {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.record-cell:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.cell-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}

.cell-placeholder {
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.cell-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  padding: 8px 10px 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cell-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  padding: 4px 10px 10px;
}

.cell-meta .nutri-calories {
  font-weight: 600;
}
</style>
